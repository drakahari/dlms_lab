from platform_preservation import projection as platform_projection
from foundation_preservation import NEW_IDS
"""Capacity, exact pins and static fixtures. Real guest evidence is separate."""
import copy,hashlib,json,os,re,subprocess,tempfile,unittest
from pathlib import Path
from unittest.mock import patch
from learning_lab.vm_preview import registry
from learning_lab.vm_preview.image_catalog import production_catalog,Catalog,digest,resource,read_json,MAX_RETAINED_LESSONS,MAX_DEFAULT_LESSONS
from learning_lab.vm_preview.sessions import Sessions
from discovery_guest_fixtures import COMMANDS,UNIT,CLEANUP,CHALLENGE_FAULTS
class DiscoveryTests(unittest.TestCase):
 def test_capacity_and_unit_order(self):
  self.assertEqual((registry.MAX_UNITS,registry.MAX_TOTAL_LESSONS,registry.MAX_LESSONS_PER_UNIT),(14,120,16))
  self.assertEqual([len(u['entries']) for u in registry.units()],[8,8,8,12,8,8,8,8,8,10,8,8,10,8]);self.assertEqual(len(registry.entries()),120)
  self.assertEqual([e['id'] for e in registry.catalog(UNIT)['entries']],list(COMMANDS))
 def test_catalog_capacity_and_unrelated_bounds(self):
  c=production_catalog();self.assertEqual((len(c.images),len(c.lessons),len(c.default_images)),(6,120,120));self.assertFalse(c.keys or c.releases)
  self.assertEqual((MAX_RETAINED_LESSONS,MAX_DEFAULT_LESSONS),(120,120));self.assertLess(len(resource('image-catalog.json')),65536)
  data=json.loads(resource('image-catalog.json'))
  bad=copy.deepcopy(data);bad['lessons'].append(copy.deepcopy(bad['lessons'][0]))
  with self.assertRaisesRegex(ValueError,'count'):Catalog(bad)
  bad=copy.deepcopy(data);bad['default_lessons']['extra']='0'*64
  with self.assertRaisesRegex(ValueError,'default'):Catalog(bad)
  bad=copy.deepcopy(data);bad['default_images']['extra']=bad['default_image']
  with self.assertRaisesRegex(ValueError,'defaults'):Catalog(bad)
  for field in ('images','keys','releases'):
   bad=copy.deepcopy(data);bad[field]=[bad['images'][0]]*65
   with self.assertRaisesRegex(ValueError,'count'):Catalog(bad)
  bad=copy.deepcopy(data);bad['images'][0]['lessons']=[bad['images'][0]['lessons'][0]]*65
  with self.assertRaisesRegex(ValueError,'compatibility'):Catalog(bad)
  with self.assertRaisesRegex(ValueError,'size'):read_json(b' '*65537)
  with self.assertRaisesRegex(ValueError,'nesting'):read_json(('['*34+'0'+']'*34).encode())
 def test_empty_default_rejection_matches_baseline(self):
  data=json.loads(resource('image-catalog.json'));data['default_lessons']={};data['default_images']={}
  with self.assertRaisesRegex(ValueError,'Missing default lesson'):Catalog(data)
 def test_protected_legacy_bytes_and_catalog_projection(self):
  for name,h in PROTECTED.items():self.assertEqual(hashlib.sha256((registry.ROOT/name).read_bytes()).hexdigest(),h,name)
  c=json.loads(platform_projection('image-catalog.json', resource('image-catalog.json')));new=set(COMMANDS)
  c['images']=[i for i in c['images'] if i['descriptor']['image_id']!='debian13-package-admin-local-v1']
  new |= {e['id'] for e in registry.catalog('linux-storage-filesystems-mounts-safe-maintenance')['entries']}
  new |= {e['id'] for e in registry.catalog('lpic-local-shell-filesystem')['entries']}
  new |= NEW_IDS
  for image in c['images']:image['lessons']=[l for l in image['lessons'] if l['id'] not in new]
  c['lessons']=[l for l in c['lessons'] if l['id'] not in new]
  for f in ('default_images','default_lessons'):c[f]={k:v for k,v in c[f].items() if k not in new}
  self.assertEqual(digest(c),OLD_CATALOG)
 def test_exact_new_image_no_fallback_or_substitution(self):
  spec=json.loads(resource('package-image.json'));c=production_catalog()
  for id in COMMANDS:
   image,l=c.defaults(id);self.assertEqual(image,spec);self.assertEqual(l,registry.load_lesson(id))
   for old in ('image.json','admin-image.json'):
    with self.assertRaisesRegex(ValueError,'combination'):c.resolve({'backend':'offline-qemu-preview-1','image':json.loads(resource(old)),'lesson_sha256':digest(l)},id)
  c.images.pop(digest(spec))
  for id in COMMANDS:
   with self.assertRaisesRegex(ValueError,'no substitute'):c.defaults(id)
 def test_unavailable_states_do_not_rewrite_sessions(self):
  for mode in ('Learn','Challenge'):
   with tempfile.TemporaryDirectory() as td:
    root=Path(td);fake=root/'fixture';fake.write_bytes(b'NOT A DISK')
    sessions=Sessions(root/'vm','b'*64,root/'gate');m=sessions.manager(list(COMMANDS)[0])
    with patch.object(m,'admission'),patch.object(m,'image',side_effect=lambda _:os.open(fake,os.O_RDONLY)):record=m.reset(mode,True)
    before={str(p):p.read_bytes() for p in (root/'vm').rglob('*') if p.is_file()}
    fresh=Sessions(root/'vm','b'*64,root/'gate').manager(m.lesson_id)
    self.assertEqual(fresh.status()['session'],record)
    fresh.catalog.images[digest(fresh.spec)]['state']='withdrawn'
    for op in ('resume','reset','new'):
     with self.assertRaisesRegex(ValueError,'withdrawn'):fresh.catalog.allow(record['pin'],m.lesson_id,op)
    self.assertEqual(before,{str(p):p.read_bytes() for p in (root/'vm').rglob('*') if p.is_file()})
 def test_guidance_is_display_only_and_fixture_parity(self):
  with patch('subprocess.Popen',side_effect=AssertionError('host execution')),patch('socket.socket',side_effect=AssertionError('network')):
   for id,commands in COMMANDS.items():
    l=registry.load_lesson(id);self.assertEqual([s['command'] for s in l['steps']],commands)
    self.assertIn('Self-reviewed',l['coverage']);self.assertNotIn('sudo apt-get',l['challenge'])
    for c in commands:c.encode('ascii');self.assertNotIn('--force',c);self.assertNotRegex(c,r'(?:plan|apt-get|sudo|apt_base\[@\]}") +autoremove')
 def test_static_apt_plan_guard_rejects_unrelated_actions_and_overflow(self):
  # Developer-only fixtures for the exact displayed awk guard. Runtime never
  # executes lesson content or receives this parser as imported code.
  setup=COMMANDS['real-linux-discovery-repair'][3]
  parser=re.search(r"awk '([^']+)' plan.txt",setup).group(1)
  summary='0 upgraded, 2 newly installed, 0 to remove and 0 not upgraded.\n'
  cases=[(summary+'Inst ll-discovery-data (1.0-1 local-deb [all])\nConf ll-discovery-report (1.0-1 local-deb [all])\n',0),
         ('0 upgraded, 0 newly installed, 2 to remove and 0 not upgraded.\nRemv ll-discovery-report [1.1-1]\nPurg ll-discovery-data\n',0),
         (summary+'Inst coreutils [1]\n',1),(summary+'Conf coreutils [1]\n',1),
         (summary+'Remv coreutils [1]\n',1),(summary+'Purg coreutils [1]\n',1),
         (summary+'Inst\n',1),(summary+'Inst ll-discovery-data [1]\n'*5,1),
         (summary+'ll-discovery-report is already the newest version (1.0-1).\n',0),
         (summary+'coreutils is already the newest version (1.0-1).\n',1),
         (summary+'ll-discovery-report is already the newest version (9.9-1).\n',1),
         (summary+"The following package was automatically installed and is no longer required:\n  ll-discovery-data\nUse 'sudo apt autoremove' to remove it.\n",0),
         (summary+"The following package was automatically installed and is no longer required:\n  coreutils\nUse 'sudo apt autoremove' to remove it.\n",1),
         (summary+"Use 'sudo apt remove coreutils' to remove it.\n",1),
         ('totally unrecognized output\n',1),(summary+'UnknownAction coreutils\n',1),
         (summary+'  coreutils\n',1),(summary+summary,1),
         (summary+'W: unexpected configuration warning\n',1)]
  for fixture,expected in cases:
   with self.subTest(fixture=fixture):
    result=subprocess.run(['awk',parser],input=fixture,text=True,capture_output=True,timeout=5)
    self.assertEqual(result.returncode,expected)
 def test_visible_cleanup_and_challenge_fault_setup(self):
  for n,e in enumerate(registry.catalog(UNIT)['entries'],1):
   self.assertIn(CLEANUP[n],e['cleanup'][0]);self.assertNotIn('-exec rm',CLEANUP[n])
  repair=registry.entry('real-linux-discovery-repair');materials='\n'.join(repair['materials'])
  for command in CHALLENGE_FAULTS.values():self.assertIn(command,materials)
  self.assertIn('fresh image starts with neither fixture installed',materials)
  self.assertIn('only after you have a configured, working report',materials)
 def test_recipe_is_fixed_and_no_new_debian_versions(self):
  tools=Path(__file__).parents[1]/'tools/vm_image/packages'
  self.assertEqual((tools/'expected-packages.tsv').read_bytes(),(Path(__file__).parents[1]/'docs/vm-preview/admin-packages.tsv').read_bytes())
  recipe=(tools/'build-fixtures.sh').read_text()
  self.assertIn('cmp "$a" "$work/b/$name"',recipe);self.assertIn('ll-discovery-data (= 1.0-1), dash, coreutils',recipe)
  self.assertIn('65536',recipe);self.assertNotIn('postinst',recipe);self.assertIn('find "$dir" -type l',recipe)

 def test_rejected_candidate_pin_retained_without_fallback(self):
  c=production_catalog();rejected=[x for x in c.images.values() if x['descriptor']['sha256']=='9dddf19d72343a17e682c012d8ff049f54c1fbed8dbc6823ea899569053aee0a']
  self.assertEqual(len(rejected),1);old=rejected[0];self.assertEqual(old['state'],'withdrawn')
  for id in COMMANDS:
   spec,lesson=c.defaults(id);self.assertEqual(spec['version'],2);self.assertEqual(spec['recipe_version'],2)
   pin={'backend':'offline-qemu-preview-1','image':old['descriptor'],'lesson_sha256':digest(lesson)}
   self.assertEqual(c.resolve(pin,id)[0],old)
   for action in ('new','resume','reset'):
    with self.assertRaisesRegex(ValueError,'withdrawn'):c.allow(pin,id,action)
   self.assertNotEqual(spec,old['descriptor'])
 def test_finalized_inventory_admission(self):
  import importlib.util
  path=Path(__file__).parents[1]/'tools/vm_image/packages/final_inventory.py'
  spec=importlib.util.spec_from_file_location('fixture_final_inventory',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
  expected=b'bash\t1\tbash\t1\n'
  good=module.BEGIN+'\r\n'+expected.decode().replace('\n','\r\n')+module.END+'\r\n'+module.DONE
  self.assertEqual(module.finalized_inventory(good,expected),expected)
  for bad in (good.replace(module.DONE,''),good+module.DONE,
              good.replace(module.END,module.BEGIN),module.DONE+good.replace(module.DONE,''),
              good.replace('bash\t1','bash\t2'),good.replace(module.END,'extra\t1\textra\t1\n'+module.END),
              good.replace(module.END,'unrecognized output\n'+module.END),good+' '*(4*1024*1024)):
   with self.subTest(bad=bad[:80]):
    with self.assertRaises(ValueError):module.finalized_inventory(bad,expected)

PROTECTED = {'__init__.py': '1e2f17daefc011e021e1c5eb273f11eddce55c305b2a79fa2a376837c59ffeb9', 'admin-image.json': '6adaf2d5d4b885221e190fcefc7cfeb25bc3901dc7b645721e237ae785ce85fd', 'admin-unit.json': '7e0a1f116d25d261946f381bdf86f06c1adb99cf33f48b2af202690c9467eb55', 'backup-unit.json': '56565062ed586195041fb856fbd4ec613c7027470304a789ce282bb7f2a94760', 'bash-unit.json': '539a468b60d73529a0ac97dde1694ee0ba5523f9dae1ec98daacfe553636a9f2', 'bridge.py': '825f3c42660f084f993a7be62e24a5a0844bd36eadcd63261aa762d6da24b73f', 'bundle_archive.py': 'e474cbbc8ba9a3638b8fc9baee92faeb64f5566bc3ac399ee03718c2d5e629cd', 'bundle_signature.py': '48c73f464e1a8c9259bf2f81042f089e13c10d0b346bfd5f586b0af3bf210068', 'catalog_manager.py': '8de739b4dfaebffb74aa5671a5be878b2fb9365984e208d20dd65ba536cd1aa2', 'files.py': '548868ac623bb1a4796884a140c959fa2b2d5bbb539f3fa16d642c93b5f361c0', 'image.json': '1499ad6e7f5cced795f5f0ff97348fbaa321a60aba3c8a810f074a846410a417', 'image_bundle.py': '7699e9544080028448a7742d212c267a93a82e4f82d239885e5876869067a470', 'lesson.json': '246f12b80f72fff3fae2a6484de185706c90dedf6ecd68f92417aea2ff6881da', 'manager.py': '10c9c248ef11bbb221c37054a47c4096b569ceff0fe9231cdf24d0fbe02fe236', 'policy.py': '0fc31036904c975950ed5902a910cfe2a3a02a8aa60e421aa460cdcbcc104031', 'process.py': 'b01bcf16fa10daa001f75c04e6054fcda610eb59db8c3737506e12bc2f9ba4c6', 'real-linux-admin-access.json': '028a9c82e801a7fc75a3d4d54009a09feb3bb5eb2d85aefdc0242054498ccd17', 'real-linux-admin-boot.json': '6c0b4f2900ff942121c11324c0f50a85350b451a3f0e6a7b554add8af886e8bc', 'real-linux-admin-change.json': '02277b4f40be2eec8a77832ce8e89e7663a09f06a3189b3e0146263b43ad9062', 'real-linux-admin-incident.json': '2b20aa5b0e9a54669a6edeb86211b2929ef263b5c773ac24c507e151cc0aee43', 'real-linux-admin-lifecycle.json': 'e70399c1cac835825e09d502e840861ff62ba2cd2f3d025bc7ff7b58c24c307a', 'real-linux-admin-logs.json': '2ce60f3d5868d6f82af76f49a7212d7819a2c729c749e40811ae65844686a87b', 'real-linux-admin-override.json': 'deb90abd551eaa539a4d9d9e02f5e88f2d0558c8b788094aa35df9d5f1729a52', 'real-linux-admin-rotation.json': '5596a103d689a84de21136dbfdf849d01cac810e49f9f2ff5dd48019ace572cb', 'real-linux-backup-access.json': '48ea55390411d74638c43e3d937a44fc7c711ea6dea68c08f59c0dbdcf59586d', 'real-linux-backup-archive.json': '87eda2b4e5f5c42c3399b2a4993ac32b188bb7b4ccec83f273f8634afca5a46d', 'real-linux-backup-assessment.json': '778370b0b0cc07b493c4c54855ac89dd04fe0c31b6476b2f47ad89d28299f6ef', 'real-linux-backup-checksum.json': 'f57a447c4e7cf948d7ec2223d39d4b749deae4ca97f2f9cb11082030dfebc32a', 'real-linux-backup-damage.json': 'f74e696639bdab8ed3e053e9bec9b1b91cb3f41cd758a02ffa40185d9a8422ce', 'real-linux-backup-requirements.json': '9260a5f805e1c0c19fce17e1c09fa50f10ae213d38f627aeffd0552ecdc4a0ad', 'real-linux-backup-restore.json': 'e8886cc6f41c64f869f1177f402b4d657da15bc20e214cff4baf416c52b83df7', 'real-linux-backup-versions.json': 'a6e6e943024071bbec234f51639ee4cdc842158ce8397a204151ad315cca7ac3', 'real-linux-bash-environment.json': '975a5dade292d60e621884f1d318cdd208df23fcc42bf4a13c6035c5ff27608e', 'real-linux-bash-files.json': '748d64684a4f0d92b8288cb2c556d1a61e2fe43105a98e130e236dc50832616e', 'real-linux-bash-guards.json': 'b8e0ed564b7450a51ebc8d3131a8441ef384cec989a65f34ed70b24b4b637fb7', 'real-linux-bash-handover.json': '157a824a4bd4c8ea33fded7244aaa8c63d777b20d95cf19c57953cad3d5055dc', 'real-linux-bash-quoting.json': 'ba60b71dfa3cec7b046489ed1d042b40cf1a9afb38d1146bf35e651c87837e55', 'real-linux-bash-records.json': '039584858810c38050db7fa3d3bfd6893d63005132bd055aae95a1a01e4860e6', 'real-linux-bash-regex.json': 'd1924bf55ffeb5f8e431be670c8e46553375f3d589f5c8cbf840d0ff76278686', 'real-linux-bash-rollback.json': '15f6bffe41ce2cf7daf6fd41c4a819cce395ae314f793495275ca95f2dd74186', 'real-linux-bash-script.json': '85b409f617b1f00da955d8cf48d5280db7b9d94432a3385b059fffc5cb16678c', 'real-linux-bash-streams.json': '78f2185a3776bab0c596820c79e9bb9cb72e8e65b49ceda704698bcc1c5f1162', 'real-linux-bash-transform.json': 'e4574f9c4bacd9f5a09158e3ec96ef347880ca76d1bcfdb560eef63b2cb0651d', 'real-linux-bash-vi.json': '9fac14c98be2390d884565f55a47715c5591a771fcc5c9a73d175783056e0a30', 'real-linux-capacity-baseline.json': '89b3d63e1576524a31fcdbd70551c2fdb6137000c7a1a6b71172485066fdc4f1', 'real-linux-capacity-cpu.json': 'dfe1958e0d51f4c14393527e276f337d46516d8d4e00fbada1f71e8b17111bae', 'real-linux-capacity-forecast.json': 'c5c1ae68c7477b16380be8e41c6d84510e75ddaa6c2d6233c13f3ff0aa672c6f', 'real-linux-capacity-io.json': 'f26c8148b9dacb9b5c4fb65b7130a569e43b8fc3eb2b7c4a54a72b3b604c653c', 'real-linux-capacity-memory.json': '3c760586d55a1442bff0ec010576e653ba43c926ace2daad32c127cc671b9368', 'real-linux-capacity-recommendation.json': '31c38667c6bf87958b2dc9861876ad87e79fdd8444e68abd9e3b52a83608de32', 'real-linux-capacity-space-inodes.json': '506eb05d32b549e8da04870b54a98f77ba7902d87844c417567a7e9bc65cf2f7', 'real-linux-capacity-trends.json': 'e12aabc6ea190d3a435f619b228c01c3c2a61705e425f87145a697ded6781692', 'real-linux-foreground-jobs.json': 'd5b4794811e15969a8d0b81a82581648d72fcc0389e5fe2add0783f6b0217ee2', 'real-linux-live-monitoring.json': '24b4d79d57e31835559bde8a8212b6135df3311a17c48d7b616a2c1414ed40c2', 'real-linux-logout-persistence.json': '7f5a32defd10c1a645b832df6359f53951e4ce8ca9ab23ca6b653f0559555d0d', 'real-linux-process-handover.json': 'eab59839bc70e8c4acb05e184d5d11531f94b3fc524ee234eb61d3f36f29f32c', 'real-linux-process-inspection.json': 'b954c498e5b3cb415d5e04091c7886c08cb632e3dc960e785362020d91e9feed', 'real-linux-process-priorities.json': 'f81821b9d040be954a406f8c168e064a8d258504c9f13af9c4eb4bfd66f57fed', 'real-linux-schedule-assessment.json': 'd81afd29561adc21c95f0a2334da8e6a623e0452d8914240fb687aa7902b91c9', 'real-linux-schedule-calendar.json': '26ac1bc858a2e0e24fd4774d429244762d26badfe40c0288a0c1eb1ca98c3e05', 'real-linux-schedule-cron.json': 'a2efd686d841aad5c93e06546e2994cbb25757ff5b8efaa4ef22901b0e3cda13', 'real-linux-schedule-diagnose.json': '256e044afd3a1072c71efab88409c50061a68d1befd5989625824a57abe32734', 'real-linux-schedule-inspect.json': '2ab3069d2eb4290045c52512ae60371ed508c31a84f35617a203b3fdccc61b8a', 'real-linux-schedule-monotonic.json': '68b53c4a31f922a91dfc17d27c84013e476c79eab15aa3e503ceb6bb09b1ea1b', 'real-linux-schedule-persistence.json': 'a426b3540dc3d4535f44aece25c8cd6ce2b68728b2dbf36c55f96f75bd49095d', 'real-linux-schedule-report.json': '268fe3bebb4407b660321bf6f277fc2f8025e53d65036abb1d2593bec86ad77e', 'real-linux-targeted-signals.json': '3be3c2d2f4fab885c7ca1d8eafe6833b2bc7c6fac58912dbde5a7de31c8cd2aa', 'real-linux-users-create.json': 'f8942ff0a9448dbae3427ca06279a88c3d4a67ca1b47c928121c0056e48cd762', 'real-linux-users-inspect.json': '2b0c7436de62339f24115699021e8a440db33b73f6bae022d1a133536c8b848f', 'real-linux-users-membership.json': 'a758c3af430648dd34f408597a13f647300b27d3013dbe61291e699dbe6476e4', 'real-linux-users-ownership.json': '7691c75e514ebe770db9b3b22b77eca59d57e97070e6883acf268d45b07c6bd9', 'real-linux-users-repair.json': '6e10129ca23817f7838f4a43a88e7a7284ab0cbd95fb8287b45fdbcdf5e44150', 'real-linux-users-restrictions.json': '8b41049e01b20f7a9c59b8b42181a13264c967ba6719db0c1470b4724e51c824', 'real-linux-users-shared.json': '8c89fa669d205e81bc5422e1c3087e9f1b9f2c4e161a02b8269356bbc78f534c', 'real-linux-users-umask.json': 'cd96c6b08a4cf6a940132382173739e3b8fed8f5764046f534156f0451027dd9', 'resource-unit.json': 'e6d3c0e6e8d6e47fccfe383a02f455b14f60168b3971ec88d426afe3ee2c9879', 'runner.py': 'dfc173564c073c0ac0d80c6a717a0b7a203d53194c466122a391ba932a2b5c48', 'scheduling-unit.json': '5950112d028b9d80d657dfa204b15989ff07923223246ca564852e518435c7ad', 'sessions.py': '5879078e3b4221ee4fcf95a9ae8cd59b03b2d6a84945bc8be6655c1d53a3166a', 'unit.json': '6de3c33587271f923ae230a99d9fbec013a005fb818fde07533ab3fe781b7ad1', 'users-unit.json': 'da69c8ae6980682d6fdda1f92f2c553a953c5931781b28191a90efbdbdd43519'}
OLD_CATALOG = 'db96f152658732e56175668651c8d05a0bc04afc962565a04c5fb683041bd491'
