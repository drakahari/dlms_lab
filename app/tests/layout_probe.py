"""Native Settings layout geometry and screenshot checks (not keyboard evidence)."""
import argparse,json,os,subprocess,sys,tempfile
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import QObject,QPointF,Qt
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application
p=argparse.ArgumentParser();p.add_argument('--label',required=True);p.add_argument('--workspace',default='2');args=p.parse_args()
t=tempfile.TemporaryDirectory();app,engine,b,lock=build_application(Path(t.name)/'data',Path(t.name)/'config');w=engine.rootObjects()[0]
report={'kind':'native layout geometry; direct page selection','checks':[]}
def dispatch(expr):
 r=subprocess.run(['hyprctl','dispatch',expr],capture_output=True,text=True);assert r.returncode==0,r.stdout+r.stderr;QTest.qWait(150)
def check(name,ok):
 report['checks'].append({'name':name,'passed':bool(ok)});assert ok,name
def visual_item(root,name):
 if root.objectName()==name:return root
 for child in root.childItems():
  found=visual_item(child,name)
  if found is not None:return found
try:
 check('native Wayland exposed',app.platformName()=='wayland' and QTest.qWaitForWindowExposed(w,5000))
 selector=f'pid:{os.getpid()}'
 dispatch(f'hl.dsp.window.float({{window="{selector}",action="toggle"}})')
 dispatch(f'hl.dsp.window.move({{window="{selector}",workspace="{args.workspace}",follow=false}})')
 b.navigate(1);w.findChild(QObject,'labTabs').setProperty('currentIndex',1)
 QTest.qWait(300)
 report['dpr']=w.devicePixelRatio();report['screen']=w.screen().name()
 for lab_id in ('gateway-dns','subnet-boundary','service-firewall'):
  b.selectLab(lab_id,True);w.findChild(QObject,'labTabs').setProperty('currentIndex',1);QTest.qWait(150)
  for width,height in [(1024,768),(1180,860),(1260,880)]:
   w.resize(width,height);QTest.qWait(300)
   viewport=w.findChild(QObject,'settingsViewport')
   check(f'geometry {width}x{height}',w.width()==width and w.height()==height)
   for name in ('Address','Prefix','Gateway','Dns'):
    item=w.findChild(QObject,'applied'+name);origin=item.mapToItem(viewport,QPointF(0,0))
    check(f'{width}x{height} {name} inside',origin.x()>=0 and origin.x()+item.width()<=viewport.width()+0.5 and origin.y()>=0 and origin.y()+item.height()<=viewport.height()+0.5)
    check(f'{width}x{height} {name} full text',item.width()+0.5>=item.property('implicitWidth'))
   w.grabWindow().save(f'evidence/{args.label}-{lab_id}-{width}x{height}.png')
  if lab_id == 'service-firewall':
   b.editRule('source','192.168.50.20/32')
   w.findChild(QObject,'labTabs').setProperty('currentIndex',4)
   panel=w.findChild(QObject,'firewallViewport')
   for width,height in [(1024,768),(1180,860),(1260,880)]:
    w.resize(width,height);QTest.qWait(300)
    check(f'firewall geometry {width}x{height}',w.width()==width and w.height()==height)
    for name in ('ruleIdInput','ruleSourceInput','ruleDestinationInput','rulePortInput','ruleActionInput','defaultPolicyInput','inspectAppliedPolicy','addRule','removeRule'):
     item=w.findChild(QObject,name);item.forceActiveFocus();QTest.qWait(100)
     origin=item.mapToItem(panel,QPointF(0,0))
     check(f'{width}x{height} {name} keyboard-visible',origin.x()>=0 and origin.x()+item.width()<=panel.width()+0.5 and origin.y()>=0 and origin.y()+item.height()<=panel.height()+0.5)
     if name in ('ruleIdInput','ruleSourceInput','ruleDestinationInput','rulePortInput'):
      check(f'{width}x{height} {name} full text',item.width()+0.5 >= item.property('contentWidth')+item.property('leftPadding')+item.property('rightPadding'))
    w.grabWindow().save(f'evidence/{args.label}-firewall-{width}x{height}.png')
  w.resize(1024,768)
  for _ in range(3):b.hint()
  b.submit();w.findChild(QObject,'labTabs').setProperty('currentIndex',3);QTest.qWait(300)
  panel=w.findChild(QObject,'feedbackViewport');panel.forceActiveFocus()
  dispatch(f'hl.dsp.focus({{window="{selector}"}})')
  w.resize(1024,768);QTest.qWait(300)
  check(f'{lab_id} hint minimum geometry',w.width()==1024 and w.height()==768)
  for _ in range(4):QTest.keyClick(w,Qt.Key_PageDown);QTest.qWait(50)
  hint=visual_item(w.contentItem(),'shownHint2');origin=hint.mapToItem(panel,QPointF(0,0))
  check(f'{lab_id} third hint reachable by PageDown',origin.y()>=0 and origin.y()+hint.height()<=panel.height()+0.5)
  check(f'{lab_id} hint width fits',origin.x()>=0 and origin.x()+hint.width()<=panel.width()+0.5)
  w.grabWindow().save(f'evidence/{args.label}-{lab_id}-hints.png')
 report['result']='PASS'
except Exception as exc:
 report['result']='FAIL';report['error']=str(exc);w.grabWindow().save(f'evidence/{args.label}-failure.png')
finally:
 w.close();app.processEvents();lock.unlock();t.cleanup();Path(f'evidence/{args.label}.json').write_text(json.dumps(report,indent=2));print(json.dumps({k:report.get(k) for k in ('result','error','dpr','screen')} | {'checks':len(report['checks'])}))
sys.exit(0 if report['result']=='PASS' else 1)
