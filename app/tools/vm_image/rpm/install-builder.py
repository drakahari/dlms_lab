#!/usr/bin/python3 -I
"""One-time build-only guest install of the frozen, vendor-signed93-package set."""
import hashlib,json,os,signal,sys
from pathlib import Path
import dnf
import dnf.transaction as t

def require(ok,message):
 if not ok:raise RuntimeError(message)
signal.signal(signal.SIGALRM,lambda *_: (_ for _ in ()).throw(TimeoutError('Builder installation deadline')))
signal.alarm(300)
require(os.geteuid()==0 and sys.flags.isolated and not sys.flags.optimize,'Trusted isolated guest root step required')
root=Path('/opt/learning-lab-builder-inputs')
manifest=json.loads((root/'manifest.json').read_text())
require(manifest['format_version']==1 and len(manifest['packages'])==93,'Unexpected builder package set')
paths=[];expected=set()
for row in manifest['packages']:
 path=root/row['file'];require(path.is_file() and not path.is_symlink() and path.stat().st_size==row['bytes'],'Builder input type/size mismatch')
 digest=hashlib.sha256();count=0
 with path.open('rb') as f:
  while chunk:=f.read(65536):
   count+=len(chunk);require(count<=row['bytes'],'Builder input grew during admission');digest.update(chunk)
 require(count==row['bytes'] and digest.hexdigest()==row['sha256'],'Builder input hash/size mismatch')
 paths.append(str(path));expected.add((row['name'],row['arch'],row['epoch'],row['version'],row['release'],int(t.PKG_INSTALL)))
require(len(expected)==93,'Duplicate builder identity')
with dnf.Base() as base:
 base.conf.plugins=False;base.conf.install_weak_deps=False;base.conf.clean_requirements_on_remove=False;base.conf.obsoletes=False
 base.conf.gpgcheck=True;base.conf.localpkg_gpgcheck=True;base.conf.exit_on_lock=True;base.conf.debuglevel=0
 base.conf.substitutions['releasever']='9.8';base.conf.substitutions['basearch']='x86_64'
 base.fill_sack(load_system_repo=True,load_available_repos=False)
 require(not list(base.repos.iter_enabled()),'Unexpected builder repo')
 packages=base.add_remote_rpms(paths,strict=True)
 require(len(packages)==93,'Builder input count mismatch')
 for package in packages:base.package_install(package,strict=True)
 for package in packages:
  code,message=base._sig_check_pkg(package)
  require(code==0,'Official builder-package signature failed: '+message)
 base.resolve(allow_erasing=False)
 actual=[(i.pkg.name,i.pkg.arch,str(i.pkg.epoch),i.pkg.version,i.pkg.release,int(i.action)) for i in base.transaction]
 require(len(actual)==93 and set(actual)==expected,'Builder solver changed the frozen set')
 transaction=base.transaction
 base.do_transaction()
 require(base.transaction is transaction,'Builder transaction replaced')
print('LL_FROZEN_BUILDER_PACKAGES_INSTALLED',flush=True)
