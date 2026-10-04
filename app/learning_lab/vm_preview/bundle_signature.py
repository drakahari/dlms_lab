"""Optional fixed gpgv verifier. Never uses a personal/default keyring."""
import os
import re
from pathlib import Path
import selectors
import subprocess
import tempfile
import time
from .files import require

VERIFIER='/usr/bin/gpgv'
TIMEOUT=15
OUTPUT_LIMIT=65536


def check_status(code,raw,signer):
    require(code==0,'Signature verification failed')
    try:lines=raw.decode('utf-8').splitlines()
    except UnicodeError as exc:raise ValueError('Invalid verifier status encoding') from exc
    valid=[];good=[]
    allowed={'NEWSIG','KEY_CONSIDERED','SIG_ID','GOODSIG','VALIDSIG'}
    newsig=0;sig_ids=0;phase=0
    for line in lines:
        fields=line.split()
        require(len(fields)>=2 and fields[0]=='[GNUPG:]' and fields[1] in allowed,'Malformed or ambiguous signature status')
        if fields[1]=='NEWSIG':
            newsig+=1;require(len(fields)==2 and phase==0,'Malformed NEWSIG status');phase=1
        if fields[1]=='KEY_CONSIDERED':
            require(phase==1,'Out-of-order key status')
            require(len(fields)==4 and fields[2]==signer and fields[3] in ('0','1'),'Unexpected key status')
        if fields[1]=='SIG_ID':
            sig_ids+=1;require(phase==1 and sig_ids==1,'Ambiguous signature ID status')
            require(len(fields)==5 and re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}',fields[3]) and fields[4].isdigit(),'Malformed signature ID status')
        if fields[1]=='VALIDSIG':
            require(phase==2,'Out-of-order valid signature status');phase=3
            require(len(fields) in (11,12),'Malformed VALIDSIG status')
            valid.append(fields)
        if fields[1]=='GOODSIG':
            require(phase==1,'Out-of-order good signature status');phase=2
            require(len(fields)>=4,'Malformed GOODSIG status');good.append(fields)
    require(newsig==1 and len(valid)==len(good)==1,'Expected exactly one valid signature')
    row=valid[0]
    require(row[2]==signer and (len(row)==11 or row[11]==signer) and good[0][2]==signer[-16:], 'Signature signer differs from permitted fingerprint')
    # Binary detached signature, modern SHA-2 digest, no expiration ambiguity.
    require(re.fullmatch(r'[0-9]{4}-[0-9]{2}-[0-9]{2}',row[3]) and row[4].isdigit() and row[5]=='0' and row[6]=='4' and row[7]=='0' and row[8] in ('1','19','22') and row[9] in ('8','9','10','11') and row[10]=='00','Unsupported signature type/digest/expiry')


def verify(manifest,signature,keyring,signer):
    require(0<len(signature)<=16384 and 0<len(keyring)<=65536,'Signature/keyring exceeds limit')
    require(os.access(VERIFIER,os.X_OK),'Optional gpgv verifier is unavailable; no image installed')
    with tempfile.TemporaryDirectory(prefix='oll-image-signature-') as temp:
        root=Path(temp)
        for name,raw in (('manifest',manifest),('signature',signature),('keyring.gpg',keyring)):
            fd=os.open(root/name,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
            with os.fdopen(fd,'wb') as stream:stream.write(raw)
        args=[VERIFIER,'--homedir',temp,'--keyring',str(root/'keyring.gpg'),'--status-fd','1','--',str(root/'signature'),str(root/'manifest')]
        child=subprocess.Popen(args,stdin=subprocess.DEVNULL,stdout=subprocess.PIPE,stderr=subprocess.PIPE,
                               env={'PATH':'/usr/bin','LC_ALL':'C'},close_fds=True)
        output={child.stdout:bytearray(),child.stderr:bytearray()};deadline=time.monotonic()+TIMEOUT
        try:
            with selectors.DefaultSelector() as selector:
                for stream in output:os.set_blocking(stream.fileno(),False);selector.register(stream,selectors.EVENT_READ)
                while selector.get_map():
                    require(time.monotonic()<deadline,'Signature verifier timed out')
                    for event,_ in selector.select(min(.1,max(0,deadline-time.monotonic()))):
                        block=os.read(event.fileobj.fileno(),4096)
                        if not block:selector.unregister(event.fileobj);continue
                        output[event.fileobj].extend(block)
                        require(sum(len(v) for v in output.values())<=OUTPUT_LIMIT,'Signature verifier output exceeds limit')
            code=child.wait(timeout=max(.01,deadline-time.monotonic()))
            check_status(code,bytes(output[child.stdout]),signer)
        except subprocess.TimeoutExpired as exc:
            raise ValueError('Signature verifier timed out') from exc
        finally:
            if child.poll() is None:child.kill();child.wait()
            child.stdout.close();child.stderr.close()
