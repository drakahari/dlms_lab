"""Isolated native workspace acceptance. QtTest input is not physical-keyboard proof."""
import argparse,json,os,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QObject,QPointF,Qt,qInstallMessageHandler
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application
from learning_lab.portable import load_portable

p=argparse.ArgumentParser();p.add_argument('--label',required=True);p.add_argument('--monitor',choices=['external','internal'],default='external');p.add_argument('--expected-dpr',type=float,default=1);p.add_argument('--offscreen',action='store_true');args=p.parse_args()
tmp=tempfile.TemporaryDirectory(prefix='lab-framework-native-');root=Path(tmp.name)
messages=[];qInstallMessageHandler(lambda typ,ctx,msg:messages.append(msg))
app,engine,b,lock=build_application(root/'data',root/'config');w=engine.rootObjects()[0]
report={'label':args.label,'platform':app.platformName(),'checks':[],'input':'QtTest key events; physical keyboard unverified','file_picker':'Native file chooser manual acceptance outstanding; transfer API tested separately','qml_messages':messages}
out=Path('evidence');out.mkdir(exist_ok=True)
def check(name,condition):
 report['checks'].append({'name':name,'passed':bool(condition)})
 if not condition:raise AssertionError(name)
def dispatch(expression):
 r=subprocess.run(['hyprctl','dispatch',expression],capture_output=True,text=True)
 if r.returncode:raise RuntimeError(r.stdout+r.stderr)
 QTest.qWait(100)
def focus():
 if args.offscreen:return
 if not w.isActive():
  for _ in range(3):
   w.requestActivate();dispatch(f'hl.dsp.focus({{window="pid:{os.getpid()}"}})')
   if QTest.qWaitForWindowActive(w,1000):return
  raise AssertionError('Native window cannot regain focus')
def key(code,mod=Qt.NoModifier):
 focus();QTest.keyClick(w,code,mod);QTest.qWait(12)
def current():return w.activeFocusItem().objectName() if w.activeFocusItem() else ''
def in_region(name):
 obj=w.activeFocusItem()
 while obj:
  if obj.objectName()==name:return True
  obj=obj.parentItem()
 return False
def tab_to(name):
 trail=[]
 for _ in range(200):
  if current()==name:return
  key(Qt.Key_Tab);trail.append(current())
 raise AssertionError('Tab cannot reach '+name+'; tail '+str(trail[-35:]))
def activate(name):tab_to(name);key(Qt.Key_Return)
def replace(name,text):
 tab_to(name);key(Qt.Key_A,Qt.ControlModifier)
 for char in text:key(ord(char))
def item(name):
 def walk(obj):
  if obj.objectName()==name and obj.isVisible():return obj
  for c in obj.childItems():
   got=walk(c)
   if got is not None:return got
  return None
 got=walk(w.contentItem())
 if got is None:got=w.findChild(QObject,name)
 if got is None:raise AssertionError('Missing item '+name)
 return got
def capture(name):
 QTest.qWait(100);pic=w.grabWindow();check('rendered '+name,not pic.isNull());pic.save(str(out/f'{args.label}-{name}.png'))
def inside(child,parent):
 pt=child.mapToItem(parent,QPointF(0,0));return pt.x()>=-1 and pt.y()>=-1 and pt.x()+child.width()<=parent.width()+1 and pt.y()+child.height()<=parent.height()+1
try:
 check('window exposed',QTest.qWaitForWindowExposed(w,5000))
 if not args.offscreen:
  check('native Wayland',app.platformName()=='wayland')
  monitors=json.loads(subprocess.run(['hyprctl','monitors','-j'],capture_output=True,text=True,check=True).stdout)
  monitor=next(m for m in monitors if (m['name'].startswith('eDP'))==(args.monitor=='internal'))
  workspace=monitor['activeWorkspace']['name']
  clients=json.loads(subprocess.run(['hyprctl','clients','-j'],capture_output=True,text=True,check=True).stdout)
  client=next(c for c in clients if c['pid']==os.getpid())
  if not client['floating']:dispatch(f'hl.dsp.window.float({{window="pid:{os.getpid()}",action="toggle"}})')
  dispatch(f'hl.dsp.window.move({{window="pid:{os.getpid()}",workspace="{workspace}",follow=false}})')
  dispatch(f'hl.dsp.focus({{window="pid:{os.getpid()}"}})')
 w.resize(1280,900);QTest.qWait(250)
 report.update(dpr=w.devicePixelRatio(),screen=w.screen().name(),graphics_api=str(w.rendererInterface().graphicsApi()))
 check('expected display scale',abs(w.devicePixelRatio()-args.expected_dpr)<0.01)
 capture('library')
 # Native proof uses the transfer API; system file-picker interaction remains manual.
 from learning_lab.portable import PackRepository
 from learning_lab.workspace_state import load_workspace
 import hashlib
 app_root=Path(__file__).resolve().parents[1]
 freeze=json.loads((app_root/'evidence/proof-code-freeze.json').read_bytes())
 def code_files():
  return {str(p.relative_to(app_root)):hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted((app_root/'learning_lab').rglob('*')) if p.is_file() and '__pycache__' not in p.parts}
 check('application still matches pre-authoring freeze',code_files()==freeze['files'])
 original={str(p.relative_to(root/'data')):p.read_bytes().hex() for p in (root/'data').rglob('*.json')}
 for filename in ('gateway-dns.lab.json','resolver-misdirection.lab.json'):
  check('import '+filename,b.importPack(str(app_root/'examples'/filename)))
 scenario=load_portable((app_root/'examples/resolver-misdirection.lab.json').read_bytes())
 w.resize(800,600);QTest.qWait(150)
 tab_to('open-'+scenario.key)
 check('imported card scrolls into view with keyboard',inside(item('open-'+scenario.key),item('libraryPage')))
 capture('imported-library-800')
 key(Qt.Key_Return);check('keyboard opens data-only scenario',b.view['labKey']==scenario.key)
 w.resize(1280,900);QTest.qWait(150)
 activate('testButton');activate('resultsTab')
 check('baseline routes and DNS succeed but endpoints fail',[row['ok'] for row in b.view['diagnostics']]==[True,True,True,True,False,False])
 check('different source and topology',b.view['sourceDevice']=='CLIENT-7' and len(b.view['topologyNodes'])==4)
 capture('misdirection-baseline')
 b.saveLayout({'dock_height':400});QTest.qWait(100);item('inspectorTabs').setProperty('currentIndex',0);QTest.qWait(80)
 item('missionPanel').property('contentItem').setProperty('contentY',0)
 capture('misdirection-diagnostics')
 b.saveLayout({});QTest.qWait(100)
 activate('hintButton');activate('settingsTab');replace('dnsInput','172.22.20.10')
 check('DNS draft does not change applied resolver',b.session.attempt['applied']['dns']=='172.22.20.20')
 activate('applyButton');activate('testButton');activate('submitButton')
 check('Learn full grade',b.view['grade']['score']==100 and b.view['hintCount']==1)
 capture('misdirection-learn-review')
 learn_id=b.session.attempt['id'];activate('modeButton');activate('confirmRestart')
 check('Challenge fresh with no assistance',b.view['mode']=='Challenge' and b.view['hintCount']==0 and b.session.engine.grade()['score']==40)
 check('Learn evidence retained',b.store.history(b.session.attempt['id'])[0][0]['id']==learn_id)
 activate('settingsTab');replace('dnsInput','172.22.20.10');activate('applyButton');activate('submitButton')
 check('Challenge full grade',b.view['grade']['score']==100 and b.view['hintCount']==0)
 capture('misdirection-challenge-review')
 activate('continueWorking');activate('consoleTab');replace('commandInput','nslookup inventory.lab.test');key(Qt.Key_Return)
 check('simulated command uses pack data','172.22.20.10' in b.view['console'])
 activate('resetButton');key(Qt.Key_Escape);check('reset cancel preserves grade',b.view['grade']['score']==100)
 challenge_id=b.session.attempt['id'];activate('resetButton');activate('confirmRestart')
 check('reset preserves Challenge evidence',any(a['id']==challenge_id for a in b.store.history(b.session.attempt['id'])[0]))
 activate('settingsTab');replace('dnsInput','172.22.20.10');activate('applyButton');activate('submitButton')
 activate('continueWorking');activate('consoleTab');replace('commandInput','nslookup orders.lab.test')
 b.flush()
 export=root/'proof-export.lab.json';check('export scenario only',b.exportScenario(str(export)))
 check('export exact content bytes',export.read_bytes()==scenario.original_bytes)
 count=len(b.labs);check('duplicate reimport idempotent',b.importPack(str(export)) and len(b.labs)==count)
 imported,added=PackRepository(root/'fresh-repository').import_file(export)
 check('fresh repository reimport retains identity',added and imported.identity==scenario.identity)
 bad=root/'bad.lab.json';bad.write_bytes(b'{"format":"learning-lab.scenario","script":"malicious"}')
 check('invalid import fails cleanly',not b.importPack(str(bad)) and len(b.labs)==count)
 for rel,raw in original.items():check('legacy record preserved '+rel,(root/'data'/rel).read_bytes().hex()==raw)
 b.navigate(2);capture('portable-history')
 expected={key:{'attempt':lab.session.attempt,'workspace':lab.workspace_state()} for key,lab in b.labs.items()}
 (root/'expected.json').write_text(json.dumps(expected));b.flush();w.close();app.processEvents();lock.unlock()
 restart=subprocess.run([sys.executable,'-B','tests/proof_restart_probe.py',str(root)],capture_output=True,text=True,timeout=20)
 report['restart']=restart.stdout+restart.stderr;check('fresh process resumes original and portable attempts',restart.returncode==0)
 check('application code unchanged after proof',code_files()==freeze['files'])
 check('no QML runtime errors',not any('ReferenceError' in m or 'TypeError' in m or 'Binding loop' in m for m in messages))
 report['result']='PASS'
except Exception as exc:
 report['result']='FAIL';report['error']=str(exc)
 try:capture('failure')
 except Exception:pass
finally:
 try:w.close();app.processEvents();lock.unlock()
 except Exception:pass
 (out/f'{args.label}.json').write_text(json.dumps(report,indent=2))
 print(json.dumps({k:report.get(k) for k in ('label','result','error','dpr','screen','restart')}|{'checks':len(report['checks']),'qml_messages':messages[-5:]},indent=2),flush=True)
 tmp.cleanup()
sys.exit(0 if report['result']=='PASS' else 1)
