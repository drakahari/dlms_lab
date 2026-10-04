"""Fixed trusted launch policy. Imported packs cannot select a VM backend."""
import json
import os
from pathlib import Path
import struct
from .files import require

QEMU='/usr/bin/qemu-system-x86_64'
QEMU_IMG='/usr/bin/qemu-img'
VIRTUAL_BYTES=16*1024**3
FILE_CEILING=18*1024**3
RESERVE=4*1024**3
BACKEND='offline-qemu-preview-1'
# Display-only policy revision. Keep the legacy exact argv recognizable so a
# console started by the previous app remains safely controllable after reopen.
GTK_LEGACY='gtk,gl=off,clipboard=off,grab-on-hover=off'
GTK_READABLE=GTK_LEGACY+',zoom-to-fit=on,keep-aspect-ratio=on'
VGA_READABLE='VGA,xres=800,yres=600'

def image_spec():return json.loads(Path(__file__).with_name('image.json').read_text())
def lesson():return json.loads(Path(__file__).with_name('lesson.json').read_text())

def inspect_overlay(fd,size=VIRTUAL_BYTES):
    """Read bounded qcow2 header BEFORE invoking QEMU; no external references."""
    raw=os.pread(fd,104,0);require(len(raw)==104,'Truncated qcow2 header')
    magic,version=struct.unpack_from('>4sI',raw)
    require(magic==b'QFI\xfb' and version==3,'Only qcow2 version 3 is supported')
    backing,backing_len,cluster_bits,virtual,crypt=struct.unpack_from('>QIIQI',raw,8)
    require(backing==0 and backing_len==0,'Embedded backing paths are forbidden')
    require(cluster_bits==16 and virtual==size and crypt==0,'Unsupported disk geometry or encryption')
    snapshots,snapshot_offset=struct.unpack_from('>IQ',raw,60)
    incompatible,compatible,autoclear,refcount_order,header_len=struct.unpack_from('>QQQII',raw,72)
    require(snapshots==snapshot_offset==0,'Internal snapshots are not supported')
    require(incompatible&~1==0 and compatible==autoclear==0 and refcount_order==4 and header_len in (104,112),'Unsupported qcow2 features')
    require(header_len==104 or os.pread(fd,8,104)==b'\x00'*8,'Unsupported compression/header fields')
    # The known feature-name table is descriptive. No external data, encryption,
    # bitmap or backing-format extensions may cause QEMU to open extra resources.
    extensions=os.pread(fd,(1<<cluster_bits)-header_len,header_len);offset=0
    while offset+8<=len(extensions):
        kind,length=struct.unpack_from('>II',extensions,offset);offset+=8
        if kind==0:
            require(length==0,'Malformed extension terminator');break
        require(kind==0x6803f857 and length<=4096 and offset+length<=len(extensions),'Unsupported qcow2 extension')
        offset+=(length+7)&~7
    else:raise ValueError('Missing qcow2 extension terminator')
    return {'dirty':bool(incompatible&1),'virtual_bytes':virtual}

def launch_arguments(base_fd,disk_fd,gate_fd,run_id,socket_path,*,display='gtk'):
    require(display in ('gtk','none'),'Unsupported console')
    args=[QEMU,'-name','Learning Lab — Real Linux preview','-uuid',run_id,
          '-machine','q35,accel=kvm','-cpu','host','-smp','2','-m','2048',
          '-nodefaults','-no-user-config','-device',VGA_READABLE if display=='gtk' else 'VGA','-nic','none',
          '-display',GTK_READABLE if display=='gtk' else 'none',
          '-monitor','none','-serial','none','-qmp',f'unix:{socket_path},server=on,wait=off']
    for fd,index in ((base_fd,1),(disk_fd,2),(gate_fd,3)):args+=['-add-fd',f'fd={fd},set={index}']
    nodes=[{'driver':'file','node-name':'base-file','filename':'/dev/fdset/1','read-only':True},
           {'driver':'raw','node-name':'base','file':'base-file','read-only':True},
           {'driver':'file','node-name':'work-file','filename':'/dev/fdset/2','aio':'threads'},
           {'driver':'qcow2','node-name':'work','file':'work-file','backing':'base'}]
    for node in nodes:args+=['-blockdev',json.dumps(node,separators=(',',':'))]
    args+=['-device','virtio-blk-pci,drive=work,werror=stop,rerror=stop']
    return args


def verify_arguments(args,run_id,socket_path):
    """Reject even a correctly hashed process record for another QEMU policy."""
    import re
    descriptors={}
    try:
        for index,arg in enumerate(args):
            if arg=='-add-fd':
                match=re.fullmatch(r'fd=([0-9]+),set=([123])',args[index+1])
                require(match is not None,'Unexpected descriptor policy')
                number,group=int(match[1]),int(match[2])
                require(number>2 and group not in descriptors,'Duplicate or invalid descriptor policy')
                descriptors[group]=number
        require(set(descriptors)=={1,2,3} and len(set(descriptors.values()))==3,'Missing or aliased descriptor policy')
        display='none' if args[args.index('-display')+1]=='none' else 'gtk'
        expected=launch_arguments(descriptors[1],descriptors[2],descriptors[3],run_id,socket_path,display=display)
        legacy=expected.copy()
        if display=='gtk':
            legacy[legacy.index('-device')+1]='VGA'
            legacy[legacy.index('-display')+1]=GTK_LEGACY
        # Exactly two GTK forms, never arbitrary display/device options or a
        # mixture. The headless graph is unchanged. All isolation flags, private
        # QMP and descriptor bindings remain part of the exact comparison.
        require(args==expected or args==legacy,'Process launch arguments differ from trusted policy')
    except (IndexError,TypeError) as exc:
        raise ValueError('Malformed process launch arguments') from exc
