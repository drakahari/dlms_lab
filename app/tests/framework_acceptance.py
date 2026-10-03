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
 # Actual native keyboard flow through all original labs.
 activate('open-gateway-dns');check('library Enter opens gateway',b.page==1)
 activate('settingsTab');replace('gatewayInput','192.168.50.1')
 check('draft separate',b.session.attempt['applied']['gateway']=='192.168.50.254')
 activate('applyButton');activate('testButton')
 check('gateway-only diagnostics',b.session.engine.reach('10.20.0.10').ok and not b.session.engine.resolve('portal.lab.test')[0].ok)
 activate('settingsTab');replace('dnsInput','10.20.0.10');activate('applyButton')
 activate('submitButton');check('gateway full grade',b.view['grade']['score']==100)
 for _ in range(3):activate('hintButton')
 check('three hints retained without score penalty',b.session.attempt['hints']==3 and b.view['grade']['score']==100)
 capture('gateway-review')
 activate('resetButton');key(Qt.Key_Escape);check('Escape returns reset focus',current()=='resetButton')
 activate('modeButton');activate('confirmRestart');check('Challenge fresh',b.session.attempt['mode']=='Challenge' and b.session.attempt['hints']==0)
 check('assisted archive preserved',b.store.history(b.session.attempt['id'])[0][0]['hints']==3)
 key(Qt.Key_1,Qt.AltModifier);activate('open-subnet-boundary')
 check('subnet peer-only baseline',b.session.engine.reach('192.168.50.21').ok and not b.session.engine.reach('192.168.50.1').ok)
 activate('settingsTab');replace('prefixInput','24');activate('applyButton');activate('submitButton')
 check('subnet full grade',b.view['grade']['score']==100)
 key(Qt.Key_1,Qt.AltModifier);activate('open-service-firewall')
 check('firewall baseline',b.session.engine.resolve('portal.lab.test')[0].ok and b.session.engine.reach('10.20.0.10').ok and not b.session.engine.connect('portal.lab.test',443).ok)
 activate('firewallTab');tab_to('ruleActionInput');key(Qt.Key_Down);key(Qt.Key_Return)
 replace('ruleSourceInput','192.168.50.20/32');activate('applyButton');activate('testButton');activate('submitButton')
 check('narrow firewall full grade',b.view['grade']['score']==100)
 capture('firewall-review')
 activate('continueWorking');activate('firewallTab');replace('ruleSourceInput','any');activate('applyButton');activate('submitButton')
 check('broad rule loses credit',b.view['grade']['score']<100)
 activate('continueWorking');activate('firewallTab');replace('ruleSourceInput','192.168.50.20/32');activate('applyButton')
 activate('consoleTab');replace('commandInput','connect portal.lab.test 443');key(Qt.Key_Return)
 check('console decision names rule','CONNECTED' in b.view['console'] and 'block-portal' in b.view['console'])
 key(Qt.Key_F6);check('F6 console to mission',in_region('missionPanel'))
 key(Qt.Key_F6);check('F6 mission to workspace',in_region('networkWorkspace'))
 key(Qt.Key_F6);check('F6 workspace to diagnostics',in_region('diagnosticsDock'))
 key(Qt.Key_F6,Qt.ShiftModifier);check('Shift F6 returns workspace',in_region('networkWorkspace'))
 # Direct geometry/focus probes, separate from the keyboard flow above.
 for lab in ('gateway-dns','subnet-boundary','service-firewall'):
  b.selectLab(lab,True);w.setProperty('reviewing',False)
  for width,height in ((800,600),(1024,768),(1180,860),(1280,900)):
   w.resize(width,height);QTest.qWait(120)
   item('inspectorTabs').setProperty('currentIndex',2);QTest.qWait(60)
   check(f'{lab} {width}x{height} actual geometry',w.width()==width and w.height()==height)
   check(f'{lab} {width} mission accessible',item('missionPanel').height()>=80 and inside(item('missionPanel'),w.contentItem()))
   check(f'{lab} {width} command input not overlapped',inside(item('commandInput'),item('diagnosticsDock')) and item('commandInput').mapToItem(w.contentItem(),QPointF(0,0)).y()+item('commandInput').height()<=item('draftWarning').mapToItem(w.contentItem(),QPointF(0,0)).y())
   for field in ('address','prefix','gateway','dns'):
    widget=item(field+'Input');widget.forceActiveFocus();QTest.qWait(40)
    applied=item('applied'+{'address':'Address','prefix':'Prefix','gateway':'Gateway','dns':'Dns'}[field])
    check(f'{lab} {width} {field} draft reachable',inside(widget,item('settingsViewport')))
    check(f'{lab} {width} {field} applied readable',inside(applied,item('settingsViewport')) and applied.property('truncated') is not True)
   if width in (800,1280):capture(lab+'-'+str(width))
  if lab=='service-firewall':
   for width,height in ((800,600),(1024,768),(1280,900)):
    w.resize(width,height);item('inspectorTabs').setProperty('currentIndex',3);QTest.qWait(100)
    for name in ('defaultPolicyInput','ruleSourceInput','ruleDestinationInput','rulePortInput','addRule','removeRule'):
     widget=item(name);widget.forceActiveFocus();QTest.qWait(40)
     check(f'firewall {width} {name} reachable',inside(widget,item('firewallViewport')))
    capture('firewall-editor-'+str(width))
 # Keep pending text and settings through switching and restart.
 b.setCommandDraft('connect portal.lab.test 22');b.editRule('port','bad');b.flush()
 pending_id=b.session.attempt['id'];b.selectLab('gateway-dns',True);b.selectLab('service-firewall',True)
 check('switch preserves pending console text',b.view['commandDraft']=='connect portal.lab.test 22')
 check('switch preserves invalid rule draft',b.view['ruleInputs']['port']=='bad')
 b.navigate(2);w.resize(1280,900);capture('history')
 check('History window title scoped','Attempt history' in w.title())
 b.navigate(0);check('Library window title scoped','Lab library' in w.title())
 b.fallbackTheme(True);b.navigate(1);capture('fallback')
 expected={key:{'id':lab.session.attempt['id'],'draft':lab.session.attempt['draft'],'mode':lab.session.attempt['mode'],'assessments':lab.session.attempt['assessments']} for key,lab in b.labs.items()}
 (root/'expected.json').write_text(json.dumps(expected));b.flush();w.close();app.processEvents();lock.unlock()
 restart=subprocess.run([sys.executable,'-B','tests/framework_restart_probe.py',str(root)],capture_output=True,text=True,timeout=20)
 report['restart']=restart.stdout+restart.stderr;check('fresh process resumes all labs',restart.returncode==0)
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
