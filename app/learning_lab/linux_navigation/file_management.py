"""Contract 4: bounded dictionary mutations, trusted parsing and grading only."""
from copy import deepcopy
import re
from ..domain.validation import require, keys, text, ValidationError
from ..linux_service.vfs import VirtualFS, canonical, parent, permitted, validate_nodes, parts
from ..linux_service.engine import command_words
from .engine import NavigationEngine

CAPABILITIES = {'virtual-filesystem', 'file-navigation', 'activity-evidence', 'bounded-file-management'}
OPERATIONS = ('pwd', 'ls', 'cd', 'cat', 'find')
PREDICATES = {'node_exists', 'file_matches_initial', 'original_preserved', 'node_absent', 'cwd_equals', 'activity_observed'}
HELP = '''Simulated Linux terminal — bounded virtual file management.
help
pwd
ls [-l] [PATH]
cd [PATH]                       no path returns to the starting directory
cat PATH
mkdir [-p] PATH
cp -n SOURCE DEST               one regular file; skip existing target
mv -n SOURCE DEST               one regular file; skip existing target
find PATH [-type f|d] [-name NAME]  exact basename, filters in either order
rm PATH                         one regular file only
rmdir PATH                      one empty directory only
Relative/absolute paths and . or .. work; above-root traversal is rejected.
No quotes, wildcards, shell expansion, pipes, redirects, chaining, host commands,
recursive deletion/copy, links, archives or other options. cp/mv require -n.
Directory destinations append the source basename. Existing target files are
skipped; target directories/files of the wrong kind report an error.
Only descendants of the declared mutable roots may change; root nodes stay fixed.
Parent write/search governs creation/removal/moves; cp also needs source read.
New directories are learner:learner 0755. Copies are learner-owned with ordinary
source mode filtered by fixed 0022; mv preserves metadata. No umask command.
find needs read/search to descend directories; any denial reports an error
without partial discovery evidence (a simplification of real Linux find).
Commands apply immediately, atomically. Every actual filesystem mutation clears
read/discovery verification: inspect the final result again. No-op skips do not.
128 nodes, 8 KiB/file, 64 KiB text total. No host I/O or processes are accessed.'''


def parse(command):
    op, *args = command_words(command)
    valid = (op in ('help', 'pwd') and not args or
             op == 'ls' and (len(args) <= 1 and not any(a.startswith('-') for a in args) or
                             len(args) in (1, 2) and args[0] == '-l' and not any(a.startswith('-') for a in args[1:])) or
             op == 'cd' and len(args) <= 1 and not any(a.startswith('-') for a in args) or
             op in ('cat', 'rm', 'rmdir') and len(args) == 1 and not args[0].startswith('-') or
             op == 'mkdir' and (len(args) == 1 and not args[0].startswith('-') or
                                len(args) == 2 and args[0] == '-p' and not args[1].startswith('-')) or
             op in ('cp', 'mv') and len(args) == 3 and args[0] == '-n' and not any(a.startswith('-') for a in args[1:]))
    if op == 'find':
        valid = bool(args) and not args[0].startswith('-') and len(args) in (1, 3, 5)
        seen = set()
        for i in range(1, len(args), 2):
            if i+1 >= len(args): valid = False; break
            option, value = args[i:i+2]
            valid = valid and option in ('-type', '-name') and option not in seen
            seen.add(option)
            valid = valid and (value in ('f', 'd') if option == '-type' else bool(re.fullmatch('[A-Za-z0-9_.-]+', value)) and not value.startswith('-'))
    require(valid, 'Unsupported command/options. Supported: mkdir [-p] PATH; cp/mv -n SOURCE DEST; find PATH [-type f|d] [-name NAME]; rm PATH; rmdir PATH. Type help for navigation syntax. No host command is run.')
    return op, args


def mutable(pack, path):
    return any(path.startswith(root.rstrip('/')+'/') for root in pack['domain']['mutable_roots'])


def initial_state(pack):
    return {'filesystem':deepcopy(pack['domain']['filesystem']), 'cwd':pack['domain']['cwd'],
            'activity':{op:[] for op in OPERATIONS}}


def target(fs, path, cwd):
    tokens = parts(path)
    # Resolve the entire parent walk before canonicalizing the leaf; inaccessible
    # or nonexistent ancestors cannot be bypassed with '..'.
    if tokens[-1] in ('', '.', '..'):
        return fs.resolve(path, cwd, 'learner')
    prefix = '/'.join(tokens[:-1]) or ('/' if path.startswith('/') else '.')
    directory = fs.directory(prefix, cwd, 'learner')
    return directory.rstrip('/')+'/'+tokens[-1]


def writable_parent(pack, fs, path):
    require(mutable(pack, path), 'Mutation is outside the declared virtual workspace: '+path)
    fs.directory(parent(path), '/', 'learner', 3)


def destination(fs, source, path, cwd):
    dest = target(fs, path, cwd)
    if dest in fs.nodes and fs.nodes[dest]['kind']=='directory':
        fs.directory(dest, '/', 'learner')
        dest = dest.rstrip('/')+'/'+source.rsplit('/', 1)[-1]
    return dest


def validate_state(pack, state):
    keys(state, {'filesystem', 'cwd', 'activity'}, 'file-management state')
    nodes = state['filesystem']; validate_nodes(nodes)
    initial = pack['domain']['filesystem']
    for path, node in initial.items():
        if not mutable(pack, path):require(nodes.get(path)==node, 'Pinned outside/root node was changed.')
    originals = [n for n in initial.values() if n['kind']=='file']
    copies = [{**n, 'owner':'learner', 'group':'learner', 'mode':f"0{int(n['mode'],8)&~0o022:03o}"} for n in originals]
    new_directory = {'kind':'directory', 'owner':'learner', 'group':'learner', 'mode':'0755', 'content':''}
    for path, node in nodes.items():
        if path in initial and node==initial[path]:continue
        require(mutable(pack, path), 'New node is outside mutable roots.')
        require(node==new_directory if node['kind']=='directory' else node in originals+copies,
                'File-management state contains unsupported metadata/content.')
    fs=VirtualFS(nodes); fs.directory(state['cwd'], '/', 'learner')
    keys(state['activity'], set(OPERATIONS), 'file-management evidence')
    for op, paths in state['activity'].items():
        require(isinstance(paths, list) and len(paths)<=128 and all(isinstance(p,str) for p in paths), 'Invalid activity evidence.')
        require(paths==sorted(set(paths)), 'Activity evidence must be unique and sorted.')
        for path in paths:
            require(path in nodes and canonical(path)==path, 'Evidence references a missing/noncanonical node.')
            if op=='cat':fs.read(path, '/', 'learner')
            elif op in ('pwd', 'cd'):fs.directory(path, '/', 'learner')
            elif op=='ls':fs.listing(path, '/', 'learner')
            else:fs.resolve(path, '/', 'learner')
    return deepcopy(state)


class FileManagementEngine(NavigationEngine):
    help_text = HELP

    def __init__(self, pack, state=None):
        super().__init__(pack, state if state is not None else initial_state(pack))

    def validate(self, state):return validate_state(self.pack, state)

    def command(self, command):
        state=deepcopy(self.state)
        try:
            op,args=parse(command)
            if op in ('help','pwd','ls','cd','cat'):
                return super().command(command)
            fs=VirtualFS(state['filesystem']);nodes=fs.nodes;cwd=state['cwd'];before=deepcopy(nodes)
            if op=='mkdir':
                parents=len(args)==2;path=args[-1]
                if not parents:
                    dest=target(fs,path.rstrip('/') or '/',cwd)
                    require(dest not in nodes,'Directory already exists: '+dest)
                    writable_parent(self.pack,fs,dest)
                    nodes[dest]={'kind':'directory','owner':'learner','group':'learner','mode':'0755','content':''}
                    output='Virtual directory ready: '+dest
                    state['activity']['cat']=[];state['activity']['find']=[]
                    self.validate(state)
                    return state,output
                tokens=parts(path);current='/' if path.startswith('/') else cwd
                for i, token in enumerate(tokens):
                    fs.directory(current,'/','learner')
                    if token in ('','.','..'):
                        if token=='..':require(current!='/', 'Path would escape the virtual root; traversal rejected.');current=parent(current)
                        continue
                    dest=current.rstrip('/')+'/'+token
                    if dest in nodes:
                        require(nodes[dest]['kind']=='directory', 'Not a virtual directory: '+dest)
                        require(parents or any(t for t in tokens[i+1:] if t not in ('','.')), 'Directory already exists: '+dest)
                    else:
                        require(parents or not any(t for t in tokens[i+1:] if t not in ('','.')), 'No such virtual parent directory: '+dest)
                        writable_parent(self.pack,fs,dest)
                        nodes[dest]={'kind':'directory','owner':'learner','group':'learner','mode':'0755','content':''}
                    current=dest
                if nodes==before:require(parents,'Directory already exists.')
                output='Virtual directory ready: '+current
            elif op in ('cp','mv'):
                source=fs.resolve(args[1],cwd,'learner');node=nodes[source]
                require(node['kind']=='file','Only one regular virtual file may be copied/moved.')
                dest=destination(fs,source,args[2],cwd)
                writable_parent(self.pack,fs,dest)
                if op=='cp':fs.read(source,'/','learner')
                else:writable_parent(self.pack,fs,source)
                if dest in nodes:
                    require(nodes[dest]['kind']=='file','Target is not a regular file: '+dest)
                    output='Skipped existing target (-n): '+dest
                else:
                    nodes[dest]=deepcopy(node)
                    if op=='cp':nodes[dest].update(owner='learner',group='learner',mode=f"0{int(node['mode'],8)&~0o022:03o}")
                    else:del nodes[source]
                    output=('Copied ' if op=='cp' else 'Moved ')+source+' → '+dest
            elif op in ('rm','rmdir'):
                path=fs.resolve(args[0],cwd,'learner');writable_parent(self.pack,fs,path)
                if op=='rm':require(nodes[path]['kind']=='file','rm supports one regular file; no recursive deletion.')
                else:
                    require(nodes[path]['kind']=='directory','rmdir needs a directory.')
                    require(not (cwd==path or cwd.startswith(path+'/')), 'Cannot remove current directory or ancestor.')
                    require(not any(parent(p)==path for p in nodes if p!=path), 'Directory is not empty: '+path)
                del nodes[path];output='Removed virtual '+('file: ' if op=='rm' else 'empty directory: ')+path
            else:
                start=fs.resolve(args[0],cwd,'learner');options=dict(zip(args[1::2],args[2::2]));matches=[]
                def visit(path):
                    node=nodes[path]
                    if (options.get('-type',node['kind'][0])==node['kind'][0] and options.get('-name',path.rsplit('/',1)[-1] or '/')==(path.rsplit('/',1)[-1] or '/')):matches.append(path)
                    if node['kind']=='directory':
                        fs.directory(path,'/','learner',5)
                        for child in sorted(p for p in nodes if p!=path and parent(p)==path):visit(child)
                visit(start)
                state['activity']['find']=sorted(set(state['activity']['find'])|set(matches))
                output='\n'.join(matches) or '(no matching virtual paths)'
            if nodes!=before:
                state['activity']['cat']=[];state['activity']['find']=[]
                for kind in ('pwd','ls','cd'):state['activity'][kind]=[p for p in state['activity'][kind] if p in nodes]
            self.validate(state)
            return state,output[:16384]+('\n[simulated output truncated]' if len(output)>16384 else '')
        except ValidationError as exc:
            return deepcopy(self.state),'Simulation: '+str(exc)

    def checks(self):
        rows=[];nodes=self.state['filesystem'];initial=self.pack['domain']['filesystem']
        for o in self.pack['objectives']:
            p=o['params'];path=p['path'];kind=o['predicate'];node=nodes.get(path)
            if kind=='node_exists':ok=node is not None and node['kind']==p['kind']
            elif kind=='file_matches_initial':ok=node is not None and node['kind']=='file' and node['content']==initial[p['source']]['content']
            elif kind=='original_preserved':ok=node==initial[path]
            elif kind=='node_absent':ok=node is None
            elif kind=='cwd_equals':ok=self.state['cwd']==path
            else:ok=path in self.state['activity'][p['operation']]
            evidence=('Action evidence' if kind=='activity_observed' else 'Final state')+': '+kind+' at '+path+(' satisfied.' if ok else ' not yet satisfied.')
            rows.append({'id':o['id'],'label':o['label'],'ok':ok,'evidence':evidence,'kind':kind,'hops':[]})
        return rows


def guide(pack,state):
    passed={r['id']:r['ok'] for r in FileManagementEngine(pack,state).checks()}
    steps=pack['domain']['lesson']['steps'];index=next((i for i,s in enumerate(steps) if not passed[s['objective']]),len(steps)-1)
    return {**steps[index],'index':index,'total':len(steps),'verified':all(passed.values()),'completionMessage':'File-management objectives met. Submit when ready.'}


def validate_pack(value):
    require(re.fullmatch('[a-z][a-z0-9-]{0,63}',value['identity']['id']) is not None,'Invalid scenario ID.')
    require(re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+',value['identity']['content_version']) is not None,'Invalid content version.')
    caps=value['engine']['required_capabilities'];require(isinstance(caps,list) and all(isinstance(c,str) for c in caps) and len(caps)==len(set(caps)) and set(caps)==CAPABILITIES,'Unsupported file-management capabilities.')
    text(value['mission']['brief'],'brief');require(type(value['metadata']['minutes']) is int and 1<=value['metadata']['minutes']<=240,'Invalid duration.')
    require(isinstance(value['hints'],list) and len(value['hints'])<=32,'At most 32 hints.')
    for h in value['hints']:text(h,'hint')
    d=value['domain'];keys(d,{'schema_version','filesystem','cwd','mutable_roots','lesson'},'file-management domain')
    require(type(d['schema_version']) is int and d['schema_version']==2,'Unsupported file-management data version.')
    validate_nodes(d['filesystem']);require(len(d['filesystem'])<=64,'At most 64 initial nodes.')
    roots=d['mutable_roots'];require(isinstance(roots,list) and 1<=len(roots)<=8 and len(set(roots))==len(roots),'Expected unique mutation roots.')
    fs=VirtualFS(d['filesystem'])
    for path in roots:
        require(isinstance(path,str) and canonical(path)==path and path!='/' and fs.directory(path,'/','learner',3)==path and fs.nodes[path]['owner']=='learner','Mutation roots must be accessible learner-owned directories.')
        require(not any(path.startswith(other+'/') for other in roots if other!=path),'Mutation roots must not overlap.')
    require(canonical(d['cwd'])==d['cwd'],'Initial cwd must be canonical.');fs.directory(d['cwd'],'/','learner')
    objectives=value['objectives'];require(isinstance(objectives,list) and 1<=len(objectives)<=16,'Expected 1–16 objectives.');ids=set()
    for o in objectives:
        keys(o,{'id','label','points','predicate','params'},'file-management objective');text(o['id'],'objective ID',64);text(o['label'],'objective label',512)
        require(o['id'] not in ids,'Duplicate objective.');ids.add(o['id']);require(o['predicate'] in PREDICATES,'Unsupported file-management predicate.')
        kind=o['predicate'];p=o['params'];keys(p,{'path'}|({'source'} if kind=='file_matches_initial' else {'kind'} if kind=='node_exists' else {'operation'} if kind=='activity_observed' else set()),'predicate parameters')
        require(isinstance(p['path'],str) and p['path'].startswith('/') and canonical(p['path'])==p['path'],'Expected canonical objective path.')
        if kind=='node_exists':require(p['kind'] in ('file','directory'),'Invalid node kind.')
        if kind=='activity_observed':require(p['operation'] in OPERATIONS,'Unsupported evidence operation.')
        if kind in ('node_absent','original_preserved'):require(p['path'] in fs.nodes,'Objective needs an initial node.')
        if kind=='file_matches_initial':require(p['source'] in fs.nodes and fs.nodes[p['source']]['kind']=='file','Unknown reference file.')
        require(type(o['points']) is int and 1<=o['points']<=100,'Invalid points.')
    require(sum(o['points'] for o in objectives)==100,'Rubric must total 100.')
    lesson=d['lesson'];keys(lesson,{'goal','steps'},'file-management lesson');text(lesson['goal'],'goal',240)
    require(isinstance(lesson['steps'],list) and len(lesson['steps'])==len(objectives),'One Learn step per objective.');seen=set()
    for step in lesson['steps']:
        keys(step,{'objective','command','explanation','expected'},'guided step');require(step['objective'] in ids and step['objective'] not in seen,'Unknown/duplicate guided objective.');seen.add(step['objective'])
        text(step['command'],'guided command',512);parse(step['command']);text(step['explanation'],'explanation',512);text(step['expected'],'expected',512)
    # Trusted, bounded simulation proves the supplied route can meet every goal.
    pack={'domain':d,'objectives':objectives};state=initial_state(pack);validate_state(pack,state)
    for _ in range(64):
        engine=FileManagementEngine(pack,state)
        if engine.grade()['complete']:return
        proposed,output=engine.command(guide(pack,state)['command'])
        require(proposed!=state,'Learn route cannot progress: '+output)
        state=proposed
    raise ValidationError('Learn route did not meet goals within 64 actions.')
