"""Opt-in local full-size acceptance. Test-only trust; never starts QEMU.
Run with an explicitly chosen new home-filesystem root, never a real VM store.
"""
import argparse, hashlib, json, os, resource, stat, subprocess, sys, tempfile, threading, time
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from offline_image_fixtures import SigningFixture, stream_bundle, file_hash
from learning_lab.vm_preview import image_bundle
from learning_lab.vm_preview.image_catalog import production_catalog, canonical, digest
from learning_lab.vm_preview.policy import image_spec

GIB=1024**3


def run(root, source, registered):
    spec=image_spec();start=time.monotonic();before=os.statvfs(root.parent)
    available=before.f_bavail*before.f_frsize
    if available<80*GIB:raise ValueError('80 GiB free-space admission failed; nothing created')
    root.mkdir(mode=0o700,exist_ok=False)
    for name in ('inputs','tmp','evidence'): (root/name).mkdir(mode=0o700)
    report={'scope':'Local full-size TEST bundle; not a production release',
            'root':str(root),'source':str(source),'registered_reference':str(registered),
            'raw_bytes':spec['bytes'],'initial_free_bytes':available,'phases':[]}
    stop=threading.Event();samples=[]
    def monitor():
        while not stop.is_set():
            v=os.statvfs(root);samples.append(v.f_bavail*v.f_frsize);stop.wait(.25)
    thread=threading.Thread(target=monitor,daemon=True);thread.start()
    def phase(name,fn):
        print(name,flush=True);t=time.monotonic();result=fn()
        report['phases'].append({'name':name,'seconds':round(time.monotonic()-t,3),'result':result})
        (root/'evidence/report.json').write_text(json.dumps(report,indent=2)+'\n')
        return result
    def check_source(path):
        with image_bundle.source_file(path) as fd:
            st=os.fstat(fd)
            if st.st_size!=spec['bytes'] or st.st_mode&0o222:raise ValueError('Reference size/mode differs')
            actual=image_bundle.sha256(fd)
            if actual!=spec['sha256']:raise ValueError('Reference image digest differs')
            return {'sha256':actual,'bytes':st.st_size,'mode':oct(stat.S_IMODE(st.st_mode))}
    signer=None;prior_temp=tempfile.tempdir
    try:
        cat=production_catalog();assert cat.keys==cat.releases=={}
        phase('verify-source-before',lambda:check_source(source))
        phase('verify-existing-registered-base-before',lambda:check_source(registered))
        signer=SigningFixture()  # short private /tmp homedir for GnuPG sockets
        report['test_signer']=signer.fingerprint
        (root/'evidence/test-public-key.gpg').write_bytes(signer.public)
        tempfile.tempdir=str(root/'tmp')  # full validation expansion must not use tmpfs
        bundle=root/'inputs/local-test.llvmimage'
        metadata={'packages.json':json.dumps({'purpose':'local test only','inventory':(source.parent/'packages.tsv').read_text().splitlines()}).encode(),
                  'provenance.json':canonical({'purpose':'local test only','descriptor':spec}),
                  'notices.txt':b'LOCAL ACCEPTANCE ARTIFACT ONLY. Not cleared or offered for redistribution. Package notices remain inside the unchanged prepared guest.\n'}
        last=[-1]
        def progress(n):
            if n//GIB!=last[0]:last[0]=n//GIB;print('compressed input GiB:',last[0],flush=True)
        t=time.monotonic();catalog,manifest,compressed=stream_bundle(signer,bundle,source,spec,metadata=metadata,progress=progress)
        (root/'evidence/test-catalog.json').write_text(json.dumps(catalog._data,indent=2)+'\n')
        report['phases'].append({'name':'build-streamed-test-bundle','seconds':round(time.monotonic()-t,3),'result':'PASS'})
        report.update(bundle_bytes=bundle.stat().st_size,compressed_bytes=compressed.stat().st_size,
                      bundle_sha256=file_hash(bundle),manifest_sha256=hashlib.sha256(canonical(manifest)+b'\n').hexdigest())
        home=root/'vm';gate=root/'import-gate'
        phase('full-validate-no-install',lambda:image_bundle.validate_bundle(bundle,_catalog=catalog));assert not home.exists()
        def cli_reject():
            result=subprocess.run([sys.executable,'-I','-B','-m','learning_lab.vm_preview.image_bundle','validate',str(bundle)],capture_output=True,text=True)
            (root/'evidence/production-cli.txt').write_text(result.stdout+result.stderr)
            assert result.returncode==1 and 'allowlist' in result.stdout
            return {'exit':result.returncode,'result':'refused by empty production allowlist'}
        phase('production-cli-refusal',cli_reject)
        result=phase('full-import',lambda:image_bundle.import_bundle(bundle,home,_catalog=catalog,_gate_root=gate));assert result['result']=='installed'
        target=home/'images'/spec['sha256']
        expected={'base.raw','manifest.json','manifest.sig','packages.json','release-provenance.json','notices.txt','provenance.json','receipt.json'}
        assert {p.name for p in target.iterdir()}==expected
        inventory={p.name:{'sha256':file_hash(p),'inode':p.stat().st_ino,'bytes':p.stat().st_size} for p in target.iterdir()}
        receipt=json.loads((target/'receipt.json').read_bytes())
        assert receipt['manifest_sha256']==report['manifest_sha256'] and receipt['descriptor_sha256']==digest(spec)
        assert json.loads((target/'provenance.json').read_bytes())==spec
        phase('verify-imported-base',lambda:check_source(target/'base.raw'))
        result=phase('full-duplicate-import',lambda:image_bundle.import_bundle(bundle,home,_catalog=catalog,_gate_root=gate));assert result['result']=='already-installed'
        assert inventory=={p.name:{'sha256':file_hash(p),'inode':p.stat().st_ino,'bytes':p.stat().st_size} for p in target.iterdir()}
        assert inventory['base.raw']['sha256']==spec['sha256']
        report['installed_inventory']=inventory
        phase('verify-source-after',lambda:check_source(source))
        phase('verify-existing-registered-base-after',lambda:check_source(registered))
        assert production_catalog().keys==production_catalog().releases=={}
        report['result']='PASS';report['guest_started']=False
    except BaseException as exc:
        report.update(result='FAIL',error=type(exc).__name__+': '+str(exc));raise
    finally:
        tempfile.tempdir=prior_temp
        if signer:
            trust_path=signer.root;signer.close();report['test_signing_home_removed']=not trust_path.exists()
        stop.set();thread.join()
        report.update(elapsed_seconds=round(time.monotonic()-start,3),min_free_bytes=min(samples) if samples else available,
                      max_rss_bytes=resource.getrusage(resource.RUSAGE_SELF).ru_maxrss*1024)
        report['retained_allocated_bytes']=sum(p.stat().st_blocks*512 for p in root.rglob('*') if p.is_file())
        (root/'evidence/report.json').write_text(json.dumps(report,indent=2)+'\n')
        print(json.dumps({k:report.get(k) for k in ('result','elapsed_seconds','max_rss_bytes','retained_allocated_bytes','min_free_bytes')},indent=2),flush=True)
    return report


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root',type=Path,required=True);parser.add_argument('--source',type=Path,required=True);parser.add_argument('--registered-reference',type=Path,required=True)
    args=parser.parse_args();run(args.root.absolute(),args.source.absolute(),args.registered_reference.absolute())
