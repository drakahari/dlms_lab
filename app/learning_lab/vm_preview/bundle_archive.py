"""Strict ZIP subset: bounded header parsing and immutable member byte ranges."""
import os
import stat
import struct
import zipfile
import zlib
from .files import require

LIMITS={'manifest.json':65536,'manifest.sig':16384,'image.raw.gz':8*1024**3,
        'packages.json':1024**2,'provenance.json':1024**2,'notices.txt':8*1024**2}
ARCHIVE_LIMIT=8*1024**3+16*1024**2
CD_LIMIT=16384


def read_at(fd,offset,size):
    length=os.fstat(fd).st_size
    require(0<=offset<=length and 0<=size<=length-offset,'Invalid/truncated archive byte range')
    raw=os.pread(fd,size,offset)
    require(len(raw)==size,'Truncated archive')
    return raw


def extra64(raw,fields):
    if not fields:
        require(not raw,'Unsupported ZIP extra fields');return []
    require(len(raw)==4+8*len(fields),'Invalid ZIP64 extra length')
    kind,size=struct.unpack_from('<HH',raw)
    require(kind==1 and size==8*len(fields),'Only required ZIP64 sizes/offsets are supported')
    return list(struct.unpack_from('<'+'Q'*len(fields),raw,4))


def preflight(fd):
    size=os.fstat(fd).st_size
    require(22<=size<=ARCHIVE_LIMIT,'Archive size exceeds limit or is truncated')
    end=read_at(fd,size-22,22)
    sig,disk,cd_disk,n_disk,n,cd_size,cd_at,comment=struct.unpack('<4s4H2IH',end)
    require(sig==b'PK\x05\x06' and disk==cd_disk==comment==0,'Invalid ZIP end record; comments/multiple disks forbidden')
    end_at=size-22
    if n==65535 or cd_size==0xffffffff or cd_at==0xffffffff:
        loc=read_at(fd,end_at-20,20)
        magic,loc_disk,z_at,disks=struct.unpack('<4sIQI',loc)
        require(magic==b'PK\x06\x07' and loc_disk==0 and disks==1,'Invalid ZIP64 locator')
        z=read_at(fd,z_at,56)
        magic,length,made,needed,disk,cd_disk,zn_disk,zn,z_size,z_cd=struct.unpack('<4sQ2H2I4Q',z)
        require(magic==b'PK\x06\x06' and length==44 and disk==cd_disk==0 and z_at+56==end_at-20 and
                needed==45 and made&255<=45,'Unsupported ZIP64 end record')
        require(n in (65535,zn) and n_disk in (65535,zn_disk) and
                cd_size in (0xffffffff,z_size) and cd_at in (0xffffffff,z_cd),'Inconsistent ZIP64 end record')
        n,n_disk,cd_size,cd_at=zn,zn_disk,z_size,z_cd;end_at=z_at
    require(n==n_disk==len(LIMITS) and 0<cd_size<=CD_LIMIT and cd_at+cd_size==end_at,'Central directory bounds/count invalid')
    cd=read_at(fd,cd_at,cd_size);position=0;members={};ranges=[]
    for _ in range(n):
        require(position+46<=len(cd),'Truncated central directory')
        fields=struct.unpack_from('<4s6H3I5H2I',cd,position)
        magic,made,needed,flags,method,mtime,mdate,crc,compressed,uncompressed,nlen,xlen,clen,disk,internal,external,offset=fields
        require(magic==b'PK\x01\x02' and flags==0 and method==0 and clen==disk==internal==0 and
                needed in (10,20,45) and made>>8 in (0,3),'Unsupported ZIP member flags/type; data descriptors forbidden')
        stop=position+46+nlen+xlen
        require(nlen<=64 and xlen<=32 and stop<=len(cd),'ZIP member header exceeds bounds')
        namebytes=cd[position+46:position+46+nlen]
        try:name=namebytes.decode('ascii')
        except UnicodeError as exc:raise ValueError('Non-ASCII archive name') from exc
        require(name in LIMITS and name not in members,'Unknown or duplicate archive member')
        mode=external>>16
        require(external&0xffff==0 and stat.S_IFMT(mode) in (0,stat.S_IFREG),'Links, directories and special members forbidden')
        fields64=[k for k,v in enumerate((uncompressed,compressed,offset)) if v==0xffffffff]
        require(not fields64 or needed==45,'ZIP64 sizes require version 4.5')
        expanded=extra64(cd[position+46+nlen:stop],fields64)
        values=[uncompressed,compressed,offset]
        for k,v in zip(fields64,expanded):values[k]=v
        uncompressed,compressed,offset=values
        require(compressed==uncompressed and compressed<=LIMITS[name],'Member size exceeds limit')
        local=read_at(fd,offset,30)
        lm,ln,lf,lmethod,lt,ld,lcrc,lc,lu,lnlen,lxlen=struct.unpack('<4s5H3I2H',local)
        require((lm,ln,lf,lmethod,lt,ld,lcrc,lnlen)==(b'PK\x03\x04',needed,flags,method,mtime,mdate,crc,nlen) and lxlen<=20,'Local/central header differs')
        require(read_at(fd,offset+30,nlen)==namebytes,'Local/central name differs')
        lf64=[k for k,v in enumerate((lu,lc)) if v==0xffffffff]
        require(not lf64 or ln==45,'ZIP64 local sizes require version 4.5')
        lv=[lu,lc]
        for k,v in zip(lf64,extra64(read_at(fd,offset+30+nlen,lxlen),lf64)):lv[k]=v
        require(lv==[uncompressed,compressed],'Local/central sizes differ')
        data_at=offset+30+nlen+lxlen;require(data_at+compressed<=cd_at,'Member overlaps central directory')
        ranges.append((offset,data_at+compressed));members[name]=(data_at,compressed,crc)
        position=stop
    require(position==len(cd),'Unexpected central-directory content')
    cursor=0
    for start,end in sorted(ranges):
        require(start==cursor,'Overlapping entries, gaps or prepended content forbidden');cursor=end
    require(cursor==cd_at,'Trailing payload bytes forbidden')
    return members


class StoredMember:
    """Read only the validated STORED range; never reparse mutable ZIP headers."""
    def __init__(self,fd,record):
        self.fd=os.dup(fd);self.offset,self.remaining,self.expected=record
        self.crc=0
    def read(self,size):
        require(type(size) is int and 0<=size<=8*1024**2+1,'Unbounded member read refused')
        count=min(size,self.remaining)
        raw=read_at(self.fd,self.offset,count)
        self.offset+=count;self.remaining-=count;self.crc=zlib.crc32(raw,self.crc)
        if not self.remaining:
            require(self.crc==self.expected,'ZIP member CRC differs')
        return raw
    def __enter__(self):return self
    def __exit__(self,*args):os.close(self.fd)


class Archive:
    def __init__(self,fd):
        # Capture all six bounded records once. Reopening ZipFile here would let
        # concurrent header edits bypass the preflight's allocation/type limits.
        self.members=preflight(fd)
        self.fd=os.dup(fd)
    def size(self,name):return self.members[name][1]
    def open(self,name):return StoredMember(self.fd,self.members[name])
    def close(self):os.close(self.fd)
    def __enter__(self):return self
    def __exit__(self,*args):self.close()
    def read(self,name):
        require(name!='image.raw.gz','Image payload must be streamed')
        with self.open(name) as stream:
            raw=stream.read(LIMITS[name]+1)
            require(len(raw)<=LIMITS[name],'Member exceeds size limit')
            return raw
