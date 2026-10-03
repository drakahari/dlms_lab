"""Pure navigation actions and retained activity facts; no host I/O."""
from copy import deepcopy
import re
from ..domain.validation import ValidationError, require, keys, text
from ..linux_service.vfs import VirtualFS, canonical, validate_nodes
from ..linux_service.engine import command_words

CAPABILITIES = {'virtual-filesystem', 'file-navigation', 'activity-evidence'}
OPERATIONS = ('pwd', 'ls', 'cd', 'cat')
HELP = '''Simulated Linux terminal — navigation inside the virtual filesystem only.
help
pwd                         show the current virtual directory
ls [-l] [PATH]              list a virtual directory or file
cd [PATH]                   change directory; no argument returns to the start
cat PATH                    read one virtual text file
Relative paths begin at your current directory; absolute paths begin at /.
. means here; .. means the parent. Traversal above / is rejected without change
(the existing simulation boundary, unlike a full Linux shell).
Paths and commands are case sensitive. No ~, quoting, globbing, pipes,
redirection, variables, substitutions, chaining, or host commands are supported.
There are no service actions, file edits or filesystem writes in this lab.
Successful actions record bounded activity facts; final-directory grading uses
where you are now. Help, diagnostics, failures and reading instructions earn no
activity evidence. No host shell, filesystem, process or network is accessed.'''


def initial_state(pack):
    d = pack['domain']
    return {'filesystem': deepcopy(d['filesystem']), 'cwd': d['cwd'],
            'activity': {op: [] for op in OPERATIONS}}


def target_path(fs, op, path):
    require(isinstance(path, str) and path.startswith('/') and canonical(path) == path,
            'Expected a canonical absolute virtual path.')
    if op in ('pwd', 'cd', 'cwd'):
        return fs.directory(path, '/', 'learner')
    if op == 'cat':
        fs.read(path, '/', 'learner')
    else:
        fs.listing(path, '/', 'learner')
    return path


def validate_pack(value):
    identity = value['identity']
    require(isinstance(identity['id'], str) and re.fullmatch('[a-z][a-z0-9-]{0,63}', identity['id']), 'Invalid scenario ID.')
    require(isinstance(identity['content_version'], str) and re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', identity['content_version']), 'Invalid content version.')
    caps = value['engine']['required_capabilities']
    require(isinstance(caps, list) and all(isinstance(c, str) for c in caps)
            and len(caps) == len(set(caps)) and set(caps) == CAPABILITIES, 'Unsupported navigation capabilities.')
    text(value['mission']['brief'], 'brief')
    require(type(value['metadata']['minutes']) is int and 1 <= value['metadata']['minutes'] <= 240, 'Invalid duration.')
    require(isinstance(value['hints'], list) and len(value['hints']) <= 32, 'At most 32 hints.')
    for hint in value['hints']: text(hint, 'hint')
    d = value['domain']
    keys(d, {'schema_version', 'filesystem', 'cwd', 'lesson'}, 'navigation domain')
    require(type(d['schema_version']) is int and d['schema_version'] == 1, 'Unsupported navigation data version.')
    validate_nodes(d['filesystem'])
    require(len(d['filesystem']) <= 64, 'At most 64 navigation nodes.')
    fs = VirtualFS(d['filesystem'])
    target_path(fs, 'cwd', d['cwd'])
    objectives = value['objectives']
    require(isinstance(objectives, list) and 1 <= len(objectives) <= 16, 'Expected 1–16 objectives.')
    ids = set()
    for o in objectives:
        keys(o, {'id', 'label', 'points', 'predicate', 'params'}, 'navigation objective')
        text(o['id'], 'objective ID', 64); text(o['label'], 'objective label', 512)
        require(o['id'] not in ids, 'Duplicate objective ID.'); ids.add(o['id'])
        require(o['predicate'] in ('activity_observed', 'cwd_equals'), 'Unsupported navigation predicate.')
        keys(o['params'], {'operation', 'path'} if o['predicate'] == 'activity_observed' else {'path'}, 'predicate parameters')
        op = o['params'].get('operation', 'cwd')
        require(op in OPERATIONS if o['predicate'] == 'activity_observed' else op == 'cwd', 'Unsupported activity operation.')
        target_path(fs, op, o['params']['path'])
        require(type(o['points']) is int and 1 <= o['points'] <= 100, 'Invalid points.')
    require(sum(o['points'] for o in objectives) == 100, 'Rubric must total 100.')
    # Multiple final directories would make the final-state rubric impossible.
    require(len({o['params']['path'] for o in objectives if o['predicate'] == 'cwd_equals'}) <= 1, 'Conflicting final directories.')
    lesson = d['lesson']; keys(lesson, {'goal', 'steps'}, 'navigation lesson')
    text(lesson['goal'], 'short goal', 240)
    require(isinstance(lesson['steps'], list) and len(lesson['steps']) == len(objectives), 'One guided step per objective.')
    seen = set()
    for step in lesson['steps']:
        keys(step, {'objective', 'path_style', 'explanation', 'expected'}, 'guided step')
        require(step['objective'] in ids and step['objective'] not in seen, 'Unknown or duplicate guided objective.')
        seen.add(step['objective'])
        require(step['path_style'] in ('relative', 'absolute'), 'Unsupported guided path style.')
        text(step['explanation'], 'explanation', 512); text(step['expected'], 'expected result', 512)


def validate_state(pack, state):
    keys(state, {'filesystem', 'cwd', 'activity'}, 'navigation state')
    require(state['filesystem'] == pack['domain']['filesystem'], 'Navigation filesystem is read-only and pinned.')
    fs = VirtualFS(state['filesystem']); target_path(fs, 'cwd', state['cwd'])
    keys(state['activity'], set(OPERATIONS), 'activity evidence')
    for op, paths in state['activity'].items():
        require(isinstance(paths, list) and len(paths) <= len(state['filesystem'])
                and all(isinstance(p, str) for p in paths), 'Invalid activity facts.')
        require(paths == sorted(set(paths)), 'Activity facts must be unique and canonical.')
        for path in paths: target_path(fs, op, path)
    return deepcopy(state)


class NavigationEngine:
    help_text = HELP

    def __init__(self, pack, state=None):
        self.pack = pack
        self.state = deepcopy(state if state is not None else initial_state(pack))

    def validate(self, state):
        return validate_state(self.pack, state)

    def record(self, state, op, target):
        state['activity'][op] = sorted(set(state['activity'][op]) | {target})

    def command(self, command):
        state = deepcopy(self.state)
        try:
            op, *args = command_words(command)
            fs = VirtualFS(state['filesystem']); cwd = state['cwd']; target = None
            if op == 'help' and not args: output = self.help_text
            elif op == 'pwd' and not args: target = cwd; output = cwd
            elif op == 'ls':
                long = bool(args and args[0] == '-l'); args = args[1:] if long else args
                require(len(args) <= 1 and not any(a.startswith('-') for a in args), 'Supported: ls [-l] [PATH]')
                path = args[0] if args else '.'
                output = fs.listing(path, cwd, 'learner', long)
                target = fs.resolve(path, cwd, 'learner')
            elif op == 'cd' and len(args) <= 1 and not any(a.startswith('-') for a in args):
                target = fs.directory(args[0] if args else self.pack['domain']['cwd'], cwd, 'learner')
                state['cwd'] = target; output = target
            elif op == 'cat' and len(args) == 1 and not args[0].startswith('-'):
                output = fs.read(args[0], cwd, 'learner') or '(empty virtual file)'
                target = fs.resolve(args[0], cwd, 'learner')
            else:
                raise ValidationError('Unsupported navigation command or options. Type help for pwd, ls, cd and cat. No host command is run.')
            if target is not None:
                self.record(state, op, target)
            self.validate(state)
            return state, output[:16384] + ('\n[simulated output truncated]' if len(output) > 16384 else '')
        except ValidationError as exc:
            return deepcopy(self.state), 'Simulation: ' + str(exc)

    def checks(self):
        rows = []
        for o in self.pack['objectives']:
            path = o['params']['path']
            if o['predicate'] == 'activity_observed':
                op = o['params']['operation']; ok = path in self.state['activity'][op]
                evidence = 'Action evidence: ' + op + ' at ' + path + (' recorded successfully.' if ok else ' has not been recorded.')
            else:
                ok = self.state['cwd'] == path
                evidence = 'Final state: current directory is ' + self.state['cwd'] + '; required ' + path + '.'
            rows.append({'id': o['id'], 'label': o['label'], 'ok': ok, 'evidence': evidence, 'kind': o['predicate'], 'hops': []})
        return rows

    def grade(self):
        rows = [{k: r[k] for k in ('id', 'label', 'ok', 'evidence')} |
                {'possible': o['points'], 'earned': o['points'] if r['ok'] else 0}
                for o, r in zip(self.pack['objectives'], self.checks())]
        score = sum(r['earned'] for r in rows)
        return {'score': score, 'complete': score == 100, 'objectives': rows}


def relative_path(target, cwd):
    dest = [p for p in target.split('/') if p]; source = [p for p in cwd.split('/') if p]
    n = 0
    while n < min(len(dest), len(source)) and dest[n] == source[n]: n += 1
    return '/'.join(['..'] * (len(source) - n) + dest[n:]) or '.'


def guide(pack, state):
    by_id = {o['id']: o for o in pack['objectives']}
    passed = {r['id']: r['ok'] for r in NavigationEngine(pack, state).checks()}
    steps = pack['domain']['lesson']['steps']
    index = next((i for i, s in enumerate(steps) if not passed[s['objective']]), len(steps)-1)
    step = steps[index]; objective = by_id[step['objective']]; params = objective['params']
    op = params.get('operation', 'cd'); target = params['path']; cwd = state['cwd']
    result = {**step, 'index': index, 'total': len(steps), 'verified': all(passed.values()),
              'completionMessage': 'Navigation objectives met. Submit when ready.'}
    if op == 'pwd' and cwd != target:
        result.update(command='cd ' + target, explanation='Return to the starting directory, then inspect it with pwd.', expected='Current directory becomes ' + target + '.')
    else:
        path = relative_path(target, cwd) if step['path_style'] == 'relative' else target
        result['command'] = op if op == 'pwd' or (op == 'ls' and path == '.') else op + ' ' + path
    return result
