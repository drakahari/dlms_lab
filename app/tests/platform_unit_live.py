"""STATIC developer fixture delivery to positively verified disposable guests.
Never an imported-lesson executor or application automation endpoint.
"""
import argparse,base64,gzip,hashlib,json,os,re,socket,subprocess,sys,time,uuid,tempfile
from pathlib import Path
p=argparse.ArgumentParser();p.add_argument('--family',choices=('rpm','foundation'),required=True);p.add_argument('--vm-home',type=Path,required=True);p.add_argument('--only');p.add_argument('--skip',nargs='*',default=[]);p.add_argument('--modes',nargs='+',choices=('Learn','Challenge'),default=['Learn','Challenge']);p.add_argument('--installed',action='store_true');a=p.parse_args()
if not a.installed:sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
sys.path.insert(0,str(Path(__file__).parent));sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools/vm_image/foundation'))
from preparation_visibility import require_no_guest
from learning_lab.vm_preview.sessions import Sessions
from learning_lab.vm_preview.registry import load_lesson,entry
from learning_lab.vm_preview.process import same_process,verify_launch
from learning_lab.vm_preview.files import sha256,Refused
from guest_screen import marker as acknowledgement,matches,locate_calibration
from platform_guest_fixtures import DATA
print(require_no_guest(),flush=True)
assert a.vm_home.is_absolute() and a.vm_home.parent.is_dir() and a.vm_home.parent.stat().st_uid==os.getuid()
out=Path(tempfile.mkdtemp(prefix='platform-'+a.family+'-native-',dir=a.vm_home.parent));(out/'executed-harness.py').write_bytes(Path(__file__).read_bytes());(out/'executed-fixtures.py').write_bytes(Path(__file__).with_name('platform_guest_fixtures.py').read_bytes())
sessions=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest());active=None;checks=[];command_sequence=0;glyphs=None;deferred=None
report={'family':a.family,'profile':sessions.profile,'results':[],'physical_keyboard':False,'accessibility':False}
def record_event(kind, **details):
    with (out / 'events.jsonl').open('a') as f:
        f.write(json.dumps({'at': time.monotonic_ns(), 'pid': os.getpid(), 'kind': kind, **details}) + '\n')

def runtime_event(kind):
    record_event(kind, record=json.loads((active.gate_root / 'running.json').read_text()), profile=active.profile, pin=active.pin)

def check(name, condition):
    if not condition:
        raise AssertionError(name)
    checks.append(name)
    print(name, flush=True)

def qmp(command, args=None):
    r = json.loads((active.gate_root / 'running.json').read_text())
    assert r['state'] == 'running' and r['profile'] == active.profile and (r['store'] == active.binding) and same_process(r), 'Not our verified guest; no developer control sent'
    verify_launch(r, str(active.gate_root / r['run'] / 'qmp'))
    with socket.socket(socket.AF_UNIX) as sock:
        sock.settimeout(5)
        sock.connect(str(active.gate_root / r['run'] / 'qmp'))
        f = sock.makefile('rwb')
        f.readline()

        def op(c, args):
            f.write((json.dumps({'execute': c, 'arguments': args or {}}) + '\n').encode())
            f.flush()
            while True:
                raw = f.readline()
                assert raw, 'QMP ended'
                v = json.loads(raw)
                if 'error' in v:
                    raise AssertionError(v)
                if 'return' in v:
                    return v['return']
        op('qmp_capabilities', {})
        return op(command, args)

def key(k):
    qmp('input-send-event', {'events': [{'type': 'key', 'data': {'down': False, 'key': {'type': 'qcode', 'data': c}}} for c in ('ctrl', 'ctrl_r', 'shift', 'shift_r', 'alt', 'alt_r')]})
    record_event('control-key', key=k, hold_ms=50)
    qmp('human-monitor-command', {'command-line': 'sendkey ' + k + ' 50'})
    time.sleep(0.08)
    qmp('input-send-event', {'events': [{'type': 'key', 'data': {'down': False, 'key': {'type': 'qcode', 'data': c}}} for c in ('ctrl', 'ctrl_r', 'shift', 'shift_r', 'alt', 'alt_r')]})
    time.sleep(0.02)

def text(t):
    basic = {' ': 'spc', '-': 'minus', '=': 'equal', '/': 'slash', '.': 'dot', ',': 'comma', "'": 'apostrophe', ';': 'semicolon', '[': 'bracket_left', ']': 'bracket_right', '\\': 'backslash', '`': 'grave_accent'}
    shifted = {'!': '1', '@': '2', '#': '3', '$': '4', '%': '5', '^': '6', '&': '7', '*': '8', '(': '9', ')': '0', '_': 'minus', '+': 'equal', ':': 'semicolon', '"': 'apostrophe', '<': 'comma', '>': 'dot', '?': 'slash', '|': 'backslash', '~': 'grave_accent', '{': 'bracket_left', '}': 'bracket_right'}
    for c in t:
        if c == '\n':
            key('ret'); continue
        k = ('shift-' + c.lower() if c.isupper() else c) if c.isascii() and c.isalnum() else basic[c] if c in basic else 'shift-' + shifted[c]
        qmp('human-monitor-command', {'command-line': 'sendkey ' + k + ' 5'})
        time.sleep(0.02)

def ocr_until(label, predicate, seconds=30, header=False):
    deadline = time.monotonic() + seconds
    while True:
        path = shot(label)
        ocr_path = path
        notice_line = False
        if header:
            from PySide6.QtGui import QImage
            im = QImage(str(path))
            ocr_path = out / (label + '-header.png')
            assert im.copy(0, 0, im.width(), 16).scaled(im.width() * 2, 32).save(str(ocr_path))
        elif label.startswith('command-'):
            from PySide6.QtGui import QImage
            from PySide6.QtCore import Qt
            im = QImage(str(path))
            im.invertPixels()
            im = im.scaled(im.width() * 3, im.height() * 3, Qt.IgnoreAspectRatio, Qt.FastTransformation)
            ocr_path = out / (label + '-ocr.png')
            assert im.save(str(ocr_path))
        elif label.startswith('notice-delivery-'):
            import csv, io
            from PySide6.QtGui import QImage
            tsv = subprocess.run(['/usr/bin/tesseract', str(path), 'stdout', '--psm', '6', 'tsv'], capture_output=True, text=True, check=True).stdout
            (out / (label + '.tsv')).write_text(tsv)
            rows = [row for row in csv.DictReader(io.StringIO(tsv), delimiter='\t') if row.get('text') == 'LL_PRACTICE_NOTICE:']
            if len(rows) == 1:
                im = QImage(str(path))
                top = int(rows[0]['top']) // 16 * 16
                assert im.width() == 800 and im.height() == 600 and (0 <= top <= 584)
                ocr_path = out / (label + '-line.png')
                assert im.copy(0, top, 800, 16).save(str(ocr_path))
                notice_line = True
        value = subprocess.run(['/usr/bin/tesseract', str(ocr_path), 'stdout', '--psm', '7' if header or notice_line else '6'], capture_output=True, text=True, check=True).stdout
        (out / (path.name + '.txt')).write_text(value)
        if predicate(value):
            return
        assert time.monotonic() < deadline, 'Guest readiness/completion timeout: ' + label
        time.sleep(0.1)

def boot_ready():
    global glyphs
    runtime_event('running')
    ocr_until('boot-ready-' + uuid.uuid4().hex[:8], lambda value: re.search(r'(?m)^\[?learner@[^\n]*\]?[$] ?$', value) is not None, 90)
    key('ctrl-u')
    text("printf '\\nPASSED\\n'")
    key('ret')
    deadline = time.monotonic() + 15
    label = 'font-calibration-' + uuid.uuid4().hex[:8]
    while True:
        path = shot(label)
        tsv = subprocess.run(['/usr/bin/tesseract', str(path), 'stdout', '--psm', '6', 'tsv'], capture_output=True, text=True, check=True).stdout
        (out / (label + '.tsv')).write_text(tsv)
        try:
            glyphs = locate_calibration(str(path), tsv)
            break
        except ValueError:
            assert time.monotonic() < deadline, 'Guest font calibration failed'
            time.sleep(0.1)
    record_event('font-calibrated', image=str(path), glyphs={k: [v.hex() for v in rows] for k, rows in glyphs.items()})

def await_ack(label, expected):
    deadline = time.monotonic() + 210
    while True:
        path = shot(label)
        if matches(str(path), expected, glyphs):
            record_event('command-complete', label=label, marker=expected, screenshot=str(path))
            return
        assert time.monotonic() < deadline, 'Exact guest acknowledgement absent: ' + label
        time.sleep(0.1)

def send_line(t, delay=0.45):
    global command_sequence
    command_sequence += 1
    label = 'command-' + str(command_sequence).zfill(4)
    record_event('guest-command', sequence=command_sequence, command=t)
    interactive = 'sensible-editor note.txt' in t
    marker = acknowledgement(command_sequence)
    text_to_send = t if interactive else 'if { ' + t + "\n}; then printf '\\n" + marker + "\\n'; else echo LOCAL_COMMAND_FAILED; fi"
    key('ctrl-u')
    text(text_to_send)
    key('ret')
    if interactive:
        ocr_until(label, lambda v: re.search('(?m)^"note[.]txt["”]\\s+1 line, 9 bytes\\s*$', v) is not None)
    else:
        await_ack(label, marker)

def shot(name):
    path = out / (name + '.png')
    qmp('screendump', {'filename': str(path), 'format': 'png'})
    return path

def assert_guest(command, label):
    if deferred is not None:
        deferred.append((command, label))
        return
    record_event('independent-assertion', label=label, command=command)
    line(command)
    check(label, True)

def clean(fixture):
    assert_guest(fixture['cleanup_command'], 'displayed preflight and exact cleanup ' + fixture['id'])
    assert_guest('! clean_family && test ! -e "$w" && test ! -L "$w"', 'repeated cleanup refuses missing workspace ' + fixture['id'])

def line(command):
    assert len(command.encode()) <= 16384 and '\x00' not in command
    payload = command + '\n'
    raw = payload.encode()
    encoded = base64.b64encode(gzip.compress(raw, mtime=0)).decode()
    digest = hashlib.sha256(raw).hexdigest()
    record_event('static-fixture-source', command=command, sha256=digest)
    (out / ('static-' + str(command_sequence + 1).zfill(4) + '.sh')).write_bytes(raw)
    assert re.fullmatch('[A-Za-z0-9+/=]+', encoded)
    transport = 'test -f "$dev" && test ! -L "$dev" && test "$(stat -c %U:%a:%h "$dev")" = learner:600:1 && printf %s ' + "'" + encoded + "'" + ' | base64 -d | gzip -d > "$dev" && test "$(sha256sum "$dev" | cut -d " " -f1)" = ' + digest + ' && . "$dev"'
    assert len(transport) < 4096
    send_line(transport)

def line_many(values):
    """Same-shell STATIC steps; pause after each exact acknowledgement for capture.
 Every original command is unchanged; its function status stops the batch on
 failure. No assertion is passed until its marker is observed. No set-e/retry.
 """
    global command_sequence
    values = list(values)
    while values:
        group = []
        script = ''
        for command, label in values:
            seq = command_sequence + len(group) + 1
            token = acknowledgement(seq)
            addition = 'fixed_developer_step() { ' + command + '\n}; if fixed_developer_step; then printf "\\n' + token + '\\n"; else echo LOCAL_COMMAND_FAILED; return 1; fi; '
            trial = script + addition + 'IFS= read -r _developer_continue || return 1; '
            encoded = base64.b64encode(gzip.compress(trial.encode(), mtime=0)).decode()
            if len(trial.encode()) > 16000 or len(encoded) + 550 >= 4096:
                assert group, 'One fixed step exceeds transport bounds'
                break
            script = trial
            group.append((command, label, seq, token))
        script = script.removesuffix('IFS= read -r _developer_continue || return 1; ') + '\n'
        raw = script.encode()
        digest = hashlib.sha256(raw).hexdigest()
        encoded = base64.b64encode(gzip.compress(raw, mtime=0)).decode()
        for command, label, seq, token in group:
            record_event('static-fixture-source', command=command, sha256=hashlib.sha256((command + '\n').encode()).hexdigest(), sequence=seq, label=label)
            (out / ('batch-step-' + str(seq).zfill(4) + '.sh')).write_text(command + '\n')
        (out / ('batch-' + str(group[0][2]).zfill(4) + '.sh')).write_bytes(raw)
        transport = 'if test -f "$dev" && test ! -L "$dev" && test "$(stat -c %U:%a:%h "$dev")" = learner:600:1 && printf %s ' + "'" + encoded + "'" + ' | base64 -d | gzip -d > "$dev" && test "$(sha256sum "$dev" | cut -d " " -f1)" = ' + digest + '; then . "$dev"; else echo LOCAL_COMMAND_FAILED; fi'
        assert len(transport) < 4096 and len(raw) <= 16384
        record_event('batch-transport', sha256=digest, command=transport, steps=[{'sequence': i, 'label': l} for _, l, i, _ in group])
        key('ctrl-u')
        text(transport)
        key('ret')
        for index, (command, label, seq, token) in enumerate(group):
            await_ack('batch-command-' + str(seq).zfill(4), token)
            command_sequence = seq
            check(label, True)
            if 'real-linux-operations-notices' in label and label.endswith('actual step 2'):
                ocr_until('notice-delivery-' + str(seq), lambda value: re.search('LL[_ ]PRACTICE[_ ]NOTICE', value) is not None and 'no action required' in value, 10)
                check(label + ' actual own-console notice delivery', True)
            if index < len(group) - 1:
                key('ret')
        values = values[len(group):]

def fresh_login():
    """Actual getty logout, with private developer-only shell-context evidence.
    No sourcing locale defaults to substitute for PAM/getty login behavior.
    """
    line('test ! -e "$HOME/developer-resume-platform.sh" && test ! -L "$HOME/developer-resume-platform.sh" && (umask 077; { printf "w=%q\\nrw=%q\\ndev=%q\\n" "$w" "$rw" "$dev"; declare -f here fresh regular; } > "$HOME/developer-resume-platform.sh") && test "$(stat -c %U:%a:%h "$HOME/developer-resume-platform.sh")" = learner:600:1')
    key('ctrl-u');text('exit');key('ret')
    boot_ready()
    send_line('test -f "$HOME/developer-resume-platform.sh" && test ! -L "$HOME/developer-resume-platform.sh" && test "$(stat -c %U:%a:%h "$HOME/developer-resume-platform.sh")" = learner:600:1 && . "$HOME/developer-resume-platform.sh" && cd "$w" && here && rm -- "$HOME/developer-resume-platform.sh"')
    record_event('actual-fresh-getty-login')

for fixture in DATA:
 if fixture['family']!=a.family or fixture['content']['id'] in a.skip or a.only and a.only!=fixture['content']['id']:continue
 ident=fixture['content']['id']
 for mode in a.modes:
  info={'id':ident,'mode':mode,'result':'INCOMPLETE','resource_sha256':fixture['resource_sha256'],'entry_sha256':fixture['entry_sha256']};running=False;active=sessions.manager(ident)
  try:
   assert active.lesson==fixture['content'] and entry(ident)==fixture['entry'],'Candidate changed; refuse stale fixture evidence'
   assert active.spec['image_id']==fixture['image_id']
   started=time.monotonic();saved=active.reset(mode,True);active.start(mode);running=True;boot_ready();runtime_event('native-start')
   if not report.get('cross_profile_refusal'):
    before=(active.gate_root/'running.json').read_bytes()
    competitor=Sessions(a.vm_home,hashlib.sha256(uuid.uuid4().bytes).hexdigest()).manager(ident)
    try:
     competitor.start(mode);raise AssertionError('Second profile started a concurrent guest')
    except Refused as error:
     assert 'running' in str(error).lower(),str(error)
     record_event('cross-profile-start-refused',error=str(error),owning_profile=active.profile)
    assert (active.gate_root/'running.json').read_bytes()==before
    report['cross_profile_refusal']=True
   send_line('dev=$(mktemp "$HOME/developer-static.XXXXXX") && test "$(stat -c %U:%a:%h "$dev")" = learner:600:1')
   selected=fixture['learn'] if mode=='Learn' else fixture['challenge']
   # Every literal in platform_guest_fixtures is a reviewed static developer
   # fixture. Runtime/lesson JSON cannot invoke this harness or its commands.
   pending=[]
   for i,command in enumerate(selected):
    if command=='exit':
     line_many(pending);pending=[];fresh_login();continue
    pending.append((command,ident+' '+mode+' step '+str(i)))
    if i==0 and fixture.get('negative_after_setup'):
     line_many(pending);pending=[]
     line_many([(c,ident+' '+mode+' preparation collision '+str(j)) for j,c in enumerate(fixture['negative_after_setup'])])
    if mode=='Learn' and i==1 and fixture.get('negative_after_job'):
     line_many(pending);pending=[]
     line_many([(c,ident+' real no-clobber result '+str(j)) for j,c in enumerate(fixture['negative_after_job'])])
   line_many(pending)
   if ident=='real-linux-foundation-locale-persistence':
    fresh_login()
    line('here && fresh "$w/restored-login.txt" && locale > restored-login.txt && cmp shell-before.txt restored-login.txt')
    check('actual fresh login after exact locale rollback '+mode,True)
   line_many([(command,ident+' factual assertion '+str(i)) for i,command in enumerate(fixture['assertions'])])
   line_many([(command,ident+' guarded cleanup '+str(i)) for i,command in enumerate(fixture['cleanup'])])
   if a.family=='rpm':
    repeated='rpm_repeated() { '+ '\n'.join(' { '+c+'\n}; rc=$?; test "$rc" = 0 || return "$rc";' for c in fixture['cleanup'])+'\n}; '
    line('here && fresh "$w/repeat-before.json" && sudo "$h" status > repeat-before.json && '+repeated+'if rpm_repeated; then false; else test $? -ne 0; fi && fresh "$w/repeat-after.json" && sudo "$h" status > repeat-after.json && cmp repeat-before.json repeat-after.json')
    check(ident+' repeat cleanup refuses without package-state change',True)
   if mode=='Learn':active.progress('next');active.progress('hint')
   else:
    for action in ('next','hint'):
     try:active.progress(action);raise AssertionError('Challenge exposes guidance')
     except Refused:pass
   active.progress('complete');record=active.status()['session'];assert record['completion']['kind']=='self-reviewed' and 'score' not in record
   shot(ident+'-'+mode+'-complete');assert active.stop()=='Cleanly stopped';running=False;runtime_event('clean-stop')
   assert Sessions(a.vm_home,sessions.profile).manager(ident).status()['session']==record
   with active.access() as (root,g,p):
    fd=active.image(root)
    try:assert sha256(fd)==active.spec['sha256']
    finally:os.close(fd)
   info.update(result='PASS',session=saved['session'],generation=saved['generation'],pin=saved['pin'],seconds=round(time.monotonic()-started,2));print('PASS',ident,mode,flush=True)
  except Exception as error:info.update(result='FAIL',error=repr(error));raise
  finally:
   if running:
    try:info['failure_cleanup']=active.stop()
    except Exception as error:info['failure_cleanup']='BLOCKED: '+str(error)
   report['results'].append(info);report['checks']=checks;(out/'report.json').write_text(json.dumps(report,indent=2)+'\n');print('Evidence',out,flush=True)
