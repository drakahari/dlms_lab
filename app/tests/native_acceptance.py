"""Native Qt keyboard walkthrough. Uses QtTest keys, never a mouse.
Host compositor commands in this test affect only this test process's window.
"""
import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from PySide6.QtCore import Qt, QObject, QPointF
from PySide6.QtTest import QTest
from learning_lab.__main__ import build_application

parser=argparse.ArgumentParser()
parser.add_argument('--label',default='native-100')
parser.add_argument('--monitor',choices=['internal','external'],default='external')
args=parser.parse_args()
out=Path('evidence');out.mkdir(exist_ok=True)
tmp=tempfile.TemporaryDirectory(prefix='learning-lab-native-')
app,engine,bridge,lock=build_application(Path(tmp.name)/'data',Path(tmp.name)/'config')
window=engine.rootObjects()[0]
report={'label':args.label,'platform':app.platformName(),'input':'QtTest key events delivered to the real Wayland QQuickWindow; no mouse events','checks':[],'focus_trace':[]}

def check(name,condition):
    report['checks'].append({'name':name,'passed':bool(condition)})
    if not condition:raise AssertionError(name)

def key(k,mod=Qt.NoModifier):
    if not window.isActive():
        for _ in range(3):
            window.requestActivate()
            own_dispatch('focuswindow',f'pid:{os.getpid()}')
            if QTest.qWaitForWindowActive(window,1000): break
        if not window.isActive():
            report['focus_blocker']=subprocess.run(['hyprctl','activewindow','-j'],capture_output=True,text=True).stdout
            raise AssertionError('Native window could not regain focus')
    QTest.keyClick(window,k,mod);QTest.qWait(25)

def focused():
    item=window.activeFocusItem()
    return item.objectName() if item else ''

def tab_to(name):
    for _ in range(100):
        if focused()==name:return
        key(Qt.Key_Tab)
        report['focus_trace'].append(focused())
    raise AssertionError(f'Could not reach {name} with Tab. Current focus: {focused()}')

def activate(name):
    tab_to(name);key(Qt.Key_Return)

def type_text(value):
    for char in value:
        key(ord(char))

def replace(name,value):
    tab_to(name);key(Qt.Key_A,Qt.ControlModifier);type_text(value)

def capture(name):
    QTest.qWait(150)
    image=window.grabWindow()
    check('rendered '+name,not image.isNull())
    image.save(str(out/f'{args.label}-{name}.png'))

def check_applied_layout():
    viewport=window.findChild(QObject,'settingsViewport')
    for name in ('Address','Prefix','Gateway','Dns'):
        item=window.findChild(QObject,'applied'+name)
        origin=item.mapToItem(viewport,QPointF(0,0))
        check('Applied '+name+' fits viewport',origin.x()>=0 and origin.x()+item.width()<=viewport.width()+0.5 and origin.y()>=0 and origin.y()+item.height()<=viewport.height()+0.5)
        check('Applied '+name+' text untruncated',item.width()+0.5>=item.property('implicitWidth'))

def own_dispatch(command,arg):
    selector=f'pid:{os.getpid()}'
    if command=='setfloating':
        expression=f'hl.dsp.window.float({{ window = "{selector}", action = "toggle" }})'
    elif command=='movewindowpixel':
        workspace='2' if args.monitor=='external' else '1'
        expression=f'hl.dsp.window.move({{ window = "{selector}", workspace = "{workspace}", follow = false }})'
    else:
        expression=f'hl.dsp.focus({{ window = "{selector}" }})'
    result=subprocess.run(['hyprctl','dispatch',expression],capture_output=True,text=True)
    if result.returncode:
        raise RuntimeError(result.stdout+result.stderr)
    QTest.qWait(150)

try:
    check('window exposed',QTest.qWaitForWindowExposed(window,5000))
    check('native Wayland platform',app.platformName()=='wayland')
    pid=f'pid:{os.getpid()}'
    own_dispatch('setfloating',pid)
    own_dispatch('movewindowpixel',('exact 1480 60,' if args.monitor=='external' else 'exact 40 55,')+pid)
    window.resize(1180,860)
    own_dispatch('focuswindow',pid)
    QTest.qWait(500)
    report['device_pixel_ratio']=window.devicePixelRatio()
    report['graphics_api']=str(window.rendererInterface().graphicsApi())
    report['screen']=window.screen().name()
    report['initial_size']=[window.width(),window.height()]
    clients=json.loads(subprocess.run(['hyprctl','clients','-j'],capture_output=True,text=True,check=True).stdout)
    report['compositor_window']=[{k:c[k] for k in ('pid','class','title','at','size','floating','monitor','xwayland')} for c in clients if c['pid']==os.getpid()]
    capture('library')
    activate('openLab')
    check('Enter opens lab',bridge.page==1)
    activate('deviceRTR-01')
    check('keyboard topology inspection',bridge.selected=='RTR-01')
    capture('topology')
    activate('consoleTab')
    tab_to('commandInput');type_text('ipconfig');key(Qt.Key_Return)
    check('console executes through keyboard','192.168.50.254' in bridge.view['console'])
    key(Qt.Key_Up)
    check('console history up',window.findChild(QObject,'commandInput').property('text')=='ipconfig')
    key(Qt.Key_Down)
    check('console history down',window.findChild(QObject,'commandInput').property('text')=='')
    activate('settingsTab')
    replace('gatewayInput','192.168.50.1')
    check('draft is separate',bridge.view['dirty'] and bridge.session.attempt['applied']['gateway']=='192.168.50.254')
    activate('submitButton')
    check('draft excluded from grading',bridge.session.attempt['assessments']['0']['score']==40)
    activate('settingsTab');activate('applyButton')
    check('gateway apply',bridge.session.engine.grade()['score']==70)
    activate('settingsTab');replace('dnsInput','10.20.0.10')
    capture('drafts')
    activate('applyButton');activate('testButton')
    check('portal diagnostic excludes TCP','TCP, HTTPS and firewall behavior are not validated' in bridge.view['console'])
    capture('console')
    activate('hintButton')
    check('hint usage recorded',bridge.session.attempt['hints']==1)
    activate('submitButton')
    check('complete rubric',bridge.session.attempt['assessments']['2']['score']==100)
    capture('completed')
    original=bridge.session.attempt['id']
    activate('resetButton')
    check('dialog opens',window.findChild(QObject,'restartDialog').property('visible'))
    check('dialog defaults to Cancel',focused()=='cancelRestart')
    key(Qt.Key_Tab)
    check('dialog Tab reaches confirmation',focused()=='confirmRestart')
    key(Qt.Key_Tab)
    check('dialog contains Tab focus',focused()=='cancelRestart')
    capture('reset-dialog')
    key(Qt.Key_Escape)
    check('Escape cancels reset',bridge.session.attempt['id']==original)
    check('dialog focus returns',focused()=='resetButton')
    activate('modeButton');activate('confirmRestart')
    check('fresh Challenge attempt',bridge.session.attempt['mode']=='Challenge' and bridge.session.attempt['hints']==0 and not bridge.session.attempt['draft'])
    history=bridge.store.history(bridge.session.attempt['id'])[0]
    check('assisted prior attempt preserved',len(history)==1 and history[0]['id']==original and history[0]['hints']==1 and history[0]['assessments']['2']['score']==100)
    check('Challenge hides hints',not window.findChild(QObject,'hintButton').property('visible'))
    challenge_id=bridge.session.attempt['id']
    activate('resetButton');activate('confirmRestart')
    check('reset archives incomplete attempt',bridge.session.attempt['id']!=challenge_id and bridge.store.history(bridge.session.attempt['id'])[1]==2)
    key(Qt.Key_3,Qt.AltModifier)
    check('keyboard history navigation',bridge.page==2)
    capture('history')
    tab_to('fallbackTheme');key(Qt.Key_Space)
    check('fallback palette',bridge.force_fallback and bridge.theme_name=='Built-in palette')
    key(Qt.Key_2,Qt.AltModifier)
    activate('settingsTab')
    window.resize(1024,768);QTest.qWait(300)
    report['minimum_size']=[window.width(),window.height()]
    check('minimum geometry',window.width()==1024 and window.height()==768)
    check_applied_layout()
    capture('minimum-fallback')
    window.resize(1260,880);QTest.qWait(200)
    check('resize larger',window.width()>=1024 and window.height()>=768)
    check_applied_layout()
    replace('gatewayInput','192.168.50.1')
    bridge.flush()
    from learning_lab.storage import Store
    check('restart state reload',Store(Path(tmp.name)/'data',bridge.pack).load()==bridge.session.attempt)
    from PySide6.QtCore import QLockFile
    second=QLockFile(str(Path(tmp.name)/'data/writer.lock'));second.setStaleLockTime(0)
    check('single writer lock',not second.tryLock(0))
    gateway_attempt=bridge.session.attempt['id']
    key(Qt.Key_1,Qt.AltModifier);activate('openSubnet')
    check('dirty lab switch asks confirmation',window.findChild(QObject,'switchDialog').property('visible'))
    check('switch defaults to Cancel',focused()=='cancelSwitch')
    key(Qt.Key_Escape)
    check('cancel switch retains gateway lab',bridge.pack['lab_id']=='gateway-dns')
    activate('openSubnet');activate('confirmSwitch')
    check('subnet opens with original fault',bridge.pack['lab_id']=='subnet-boundary' and bridge.session.attempt['applied']['prefix']==28)
    activate('briefButton')
    check('subnet task brief dialog',window.findChild(QObject,'briefDialog').property('visible'))
    capture('subnet-brief');key(Qt.Key_Escape)
    check('brief focus returns',focused()=='briefButton')
    activate('devicePEER-01')
    check('peer inspectable','192.168.50.21/24' in bridge.view['deviceDetails'])
    capture('subnet-topology')
    activate('testButton')
    console=bridge.view['console']
    check('native subnet baseline diagnostics','PASS · Retain local peer' in console and 'FAIL · Reach the assigned gateway' in console and 'FAIL · Restore remote server' in console)
    capture('subnet-baseline')
    activate('settingsTab')
    check('gateway and DNS fixed',window.findChild(QObject,'gatewayInput').property('readOnly') and window.findChild(QObject,'dnsInput').property('readOnly'))
    window.resize(1024,768);QTest.qWait(300);check_applied_layout();capture('subnet-settings-minimum')
    replace('prefixInput','24');activate('submitButton')
    check('subnet drafts excluded',bridge.session.attempt['assessments']['0']['score']==40)
    activate('settingsTab');activate('applyButton');activate('testButton')
    check('native subnet correction restores all paths',all(bridge.session.engine.reach(ip).ok for ip in ('192.168.50.21','192.168.50.1','10.20.0.10')))
    capture('subnet-connectivity')
    for _ in range(3):activate('hintButton')
    check('all three hints recorded',bridge.session.attempt['hints']==3)
    activate('submitButton')
    check('subnet full credit with hints',bridge.session.attempt['assessments']['1']['score']==100)
    capture('subnet-completed')
    activate('submitButton')
    check('subnet duplicate submit idempotent',len(bridge.session.attempt['assessments'])==2)
    activate('settingsTab');replace('prefixInput','16');activate('applyButton');activate('submitButton')
    check('working wider prefix not full credit',bridge.session.attempt['assessments']['2']['score']==70 and bridge.session.engine.reach('10.20.0.10').ok)
    complete_id=bridge.session.attempt['id']
    activate('modeButton');activate('confirmRestart')
    check('subnet Challenge starts fresh',bridge.session.attempt['mode']=='Challenge' and bridge.session.attempt['applied']['prefix']==28 and bridge.session.attempt['hints']==0)
    check('subnet Challenge hides hints',not window.findChild(QObject,'hintButton').property('visible'))
    rows=bridge.store.history(bridge.session.attempt['id'])[0]
    check('subnet completed assisted attempt retained',rows[0]['id']==complete_id and rows[0]['hints']==3 and rows[0]['assessments']['1']['score']==100)
    activate('resetButton');activate('confirmRestart')
    check('subnet reset retained both prior attempts',bridge.store.history(bridge.session.attempt['id'])[1]==2 and not bridge.session.attempt['console'])
    key(Qt.Key_3,Qt.AltModifier);capture('subnet-history')
    key(Qt.Key_2,Qt.AltModifier);activate('settingsTab');replace('prefixInput','24')
    subnet_attempt=bridge.session.attempt['id']
    key(Qt.Key_1,Qt.AltModifier);activate('openLab');activate('confirmSwitch')
    check('gateway resumes exact attempt and draft',bridge.session.attempt['id']==gateway_attempt and bridge.session.attempt['draft']['gateway']=='192.168.50.1')
    key(Qt.Key_1,Qt.AltModifier);activate('openSubnet');activate('confirmSwitch')
    check('subnet resumes exact attempt and draft',bridge.session.attempt['id']==subnet_attempt and bridge.session.attempt['draft']['prefix']=='24')
    activate('settingsTab');window.resize(1260,880);QTest.qWait(200);check_applied_layout();capture('subnet-settings-large')
    key(Qt.Key_1,Qt.AltModifier);activate('openFirewall');activate('confirmSwitch')
    check('firewall opens with separate attempt',bridge.pack['lab_id']=='service-firewall' and bridge.session.attempt['mode']=='Learn')
    activate('deviceRTR-01');capture('firewall-topology')
    activate('testButton')
    baseline=bridge.view['console']
    check('firewall baseline separates ping and TCP','PASS · Preserve ICMP' in baseline and 'PASS · DNS' in baseline and '443 BLOCKED' in baseline and 'default policy deny' in baseline)
    capture('firewall-baseline')
    tab_to('commandInput');type_text('connect portal.lab.test 443');key(Qt.Key_Return)
    check('connect command from keyboard','> connect portal.lab.test 443' in bridge.view['console'] and 'rule 1 [block-portal]' in bridge.view['console'])
    activate('firewallTab');window.resize(1024,768);QTest.qWait(300)
    tab_to('ruleActionInput');key(Qt.Key_End)
    check('keyboard changes draft action',bridge.session.policy_draft()['rules'][0]['action']=='allow')
    replace('ruleSourceInput','192.168.50.20/32')
    check('rule draft separate from applied',bridge.view['firewallDirty'] and bridge.session.attempt['applied']['firewall']['rules'][0]['action']=='deny')
    activate('inspectAppliedPolicy')
    check('Applied policy dialog shows original deny','deny tcp any' in window.findChild(QObject,'appliedPolicyText').property('text'))
    capture('firewall-applied-dialog');key(Qt.Key_Escape)
    check('Applied dialog restores focus',focused()=='inspectAppliedPolicy')
    activate('submitButton');check('draft firewall grading excluded',bridge.session.attempt['assessments']['0']['score']==40)
    activate('firewallTab');replace('rulePortInput','0');activate('applyButton')
    check('invalid rule Apply atomic',bridge.session.attempt['revision']==0 and bridge.session.attempt['applied']['firewall']['rules'][0]['action']=='deny' and 'port' in bridge.view['message'])
    activate('firewallTab');replace('rulePortInput','443');capture('firewall-drafts')
    activate('applyButton');activate('testButton')
    check('narrow correction allows only service',bridge.session.engine.connect('portal.lab.test',443).ok and bridge.session.engine.connect('portal.lab.test',22).kind=='policy-deny' and bridge.session.engine.grade()['score']==100)
    capture('firewall-corrected-connections')
    for _ in range(3):activate('hintButton')
    activate('submitButton');check('firewall full credit with three hints',bridge.session.attempt['assessments']['1']['score']==100 and bridge.session.attempt['hints']==3)
    capture('firewall-completed')
    activate('submitButton');check('firewall duplicate submit idempotent',len(bridge.session.attempt['assessments'])==2)
    assisted_id=bridge.session.attempt['id']
    activate('resetButton');activate('confirmRestart')
    check('firewall reset restores initial rules and archives assisted work',bridge.session.attempt['applied']['firewall']['rules'][0]['action']=='deny' and bridge.view['historyCount']==1 and bridge.session.attempt['hints']==0 and not bridge.session.attempt['console'])
    activate('firewallTab');activate('addRule')
    check('add rule creates second draft',bridge.view['ruleCount']==2 and bridge.view['ruleIndex']==1)
    tab_to('ruleActionInput');key(Qt.Key_End);activate('applyButton')
    check('allow after matching deny stays blocked',bridge.session.engine.grade()['score']==40 and 'rule 1 [block-portal]' in bridge.session.engine.connect('portal.lab.test',443).message)
    activate('firewallTab');activate('moveRuleUp');activate('applyButton')
    check('moving narrow allow before deny succeeds',bridge.session.engine.grade()['score']==100 and 'rule 1 [rule-1]' in bridge.session.engine.connect('portal.lab.test',443).message)
    activate('firewallTab');replace('ruleSourceInput','any');activate('applyButton');activate('submitButton')
    check('broad source loses isolation credit',bridge.session.engine.grade()['score']==80 and not bridge.session.engine.grade()['complete'])
    capture('firewall-broad-rejected')
    activate('firewallTab');replace('rulePortInput','any');activate('applyButton')
    check('broad port also opens restricted flow',bridge.session.engine.connect('portal.lab.test',22).ok and bridge.session.engine.grade()['score']==70)
    activate('firewallTab');replace('ruleSourceInput','192.168.50.20/32');replace('rulePortInput','443');activate('applyButton')
    activate('firewallTab');activate('moveRuleDown');activate('applyButton')
    check('moving below deny blocks again',not bridge.session.engine.connect('portal.lab.test',443).ok)
    activate('firewallTab');activate('moveRuleUp');activate('applyButton')
    activate('firewallTab');tab_to('ruleSelect');key(Qt.Key_End)
    check('keyboard selects second rule',bridge.view['ruleIndex']==1)
    activate('removeRule');activate('applyButton')
    check('remove redundant deny retains narrow behavior',bridge.view['ruleCount']==1 and bridge.session.engine.grade()['score']==100)
    activate('firewallTab');tab_to('defaultPolicyInput');key(Qt.Key_End);activate('applyButton');activate('testButton')
    check('default allow opens unmatched SSH',bridge.session.engine.connect('portal.lab.test',22).ok and 'default policy allow' in bridge.view['console'])
    activate('firewallTab');tab_to('defaultPolicyInput');key(Qt.Key_Home);activate('applyButton');activate('submitButton')
    check('default deny restores narrow grade',bridge.session.engine.grade()['score']==100)
    activate('modeButton');activate('confirmRestart')
    check('firewall Challenge fresh and hints hidden',bridge.session.attempt['mode']=='Challenge' and bridge.session.attempt['hints']==0 and not window.findChild(QObject,'hintButton').property('visible'))
    activate('resetButton');activate('confirmRestart')
    rows,count,_=bridge.store.history(bridge.session.attempt['id'])
    check('firewall history retains all three prior attempts',count==3 and any(a['id']==assisted_id and a['hints']==3 for a in rows))
    key(Qt.Key_3,Qt.AltModifier);capture('firewall-history')
    key(Qt.Key_2,Qt.AltModifier);activate('firewallTab');replace('ruleSourceInput','192.168.50.20/32');tab_to('ruleActionInput');key(Qt.Key_End)
    firewall_attempt=bridge.session.attempt['id']
    key(Qt.Key_1,Qt.AltModifier);activate('openLab');activate('confirmSwitch')
    check('gateway retained across third lab',bridge.session.attempt['id']==gateway_attempt and bridge.session.attempt['draft']['gateway']=='192.168.50.1')
    key(Qt.Key_1,Qt.AltModifier);activate('openSubnet');activate('confirmSwitch')
    check('subnet retained across third lab',bridge.session.attempt['id']==subnet_attempt and bridge.session.attempt['draft']['prefix']=='24')
    key(Qt.Key_1,Qt.AltModifier);activate('openFirewall');activate('confirmSwitch')
    check('firewall resumes pending policy draft',bridge.session.attempt['id']==firewall_attempt and bridge.session.policy_draft()['rules'][0]['action']=='allow' and bridge.session.attempt['applied']['firewall']['rules'][0]['action']=='deny')
    activate('firewallTab');window.resize(1260,880);QTest.qWait(300);capture('firewall-settings-large')
    bridge.flush()
    report['result']='PASS'
except Exception as exc:
    report['result']='FAIL';report['error']=str(exc)
    try:capture('failure')
    except Exception:pass
finally:
    window.close();app.processEvents();lock.unlock()
    if report.get('result')=='PASS':
        restart=subprocess.run([sys.executable,'tests/restart_probe.py',str(Path(tmp.name)/'data'),str(Path(tmp.name)/'config'),bridge.session.attempt['id']],capture_output=True,text=True)
        report['fresh_process_restart']={'returncode':restart.returncode,'output':restart.stdout,'errors':restart.stderr}
        if restart.returncode:report['result']='FAIL'
    (out/f'{args.label}.json').write_text(json.dumps(report,indent=2))
    print(json.dumps({k:report.get(k) for k in ('label','result','error','device_pixel_ratio','fresh_process_restart','focus_blocker')} | {'checks':len(report['checks'])},indent=2))
    tmp.cleanup()
sys.exit(0 if report.get('result')=='PASS' else 1)
