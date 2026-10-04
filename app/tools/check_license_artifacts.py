"""Read-only checks for locally built wheel/sdist legal files and metadata."""
import argparse
from email.parser import BytesParser
from pathlib import Path
import tarfile
from zipfile import ZipFile

APP=Path(__file__).resolve().parents[1]
LEGAL=('LICENSE','THIRD_PARTY_NOTICES.md')


def metadata(raw):
    value=BytesParser().parsebytes(raw)
    assert value['License-Expression']=='MIT', 'Incorrect license expression'
    assert set(value.get_all('License-File',[]))==set(LEGAL), 'Incorrect license-file entries'
    assert tuple(map(int,value['Metadata-Version'].split('.'))) >= (2,4)


def check(path):
    expected={name:(APP/name).read_bytes() for name in LEGAL}
    if path.name.endswith('.whl'):
        with ZipFile(path) as z:
            members=z.namelist();assert len(members)==len(set(members))
            info=[n for n in members if n.endswith('.dist-info/METADATA')];assert len(info)==1
            prefix=info[0].rsplit('/',1)[0];metadata(z.read(info[0]))
            for name,raw in expected.items():assert z.read(prefix+'/licenses/'+name)==raw,name
            assert not any(n.endswith(('.raw','.qcow2','.llvmimage','.gpg')) for n in members)
    else:
        # Inspect without extracting or executing archive members.
        with tarfile.open(path,'r:gz') as archive:
            names=archive.getnames();assert len(names)==len(set(names))
            roots={n.split('/')[0] for n in names};assert len(roots)==1
            prefix=next(iter(roots));metadata(archive.extractfile(prefix+'/PKG-INFO').read())
            for name,raw in expected.items():assert archive.extractfile(prefix+'/'+name).read()==raw,name
            assert archive.getmember(prefix+'/docs/distribution-licensing.md').isfile()
            assert not any(n.endswith(('.raw','.qcow2','.llvmimage','.gpg')) for n in names)
    return str(path)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('artifacts',type=Path,nargs='+')
    for path in p.parse_args().artifacts:print('PASS',check(path))
