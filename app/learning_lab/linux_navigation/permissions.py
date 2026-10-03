"""Versioned bounded mutable modes; no host APIs or executable pack data."""
from copy import deepcopy
import re
from ..domain.validation import keys, require, text, ValidationError
from ..linux_service.vfs import VirtualFS, canonical, validate_nodes, permitted, parent
from ..linux_service.engine import command_words
from .engine import NavigationEngine, relative_path

CAPABILITIES = {'virtual-filesystem', 'file-navigation', 'activity-evidence', 'mutable-permissions'}
DIRECTORY_CAPABILITIES = CAPABILITIES | {'directory-permissions', 'traversal-evidence', 'directory-name-listing'}
HELP = '''Simulated Linux terminal — virtual file permissions only.
help
pwd
ls [-l] [PATH]
cd [PATH]                  no path returns to the starting directory
cat PATH
chmod u+r PATH             add owner-read, preserving all other mode bits
chmod NNN PATH             replace all ordinary bits; exactly 3 octal digits 0–7
Examples: chmod u+r notes.txt; chmod 600 notes.txt (separate commands).
Only pack-enabled, learner-owned regular files may have their mode changed.
No directory mode changes, other symbolic forms, 4-digit modes, options,
recursion, multiple targets, special bits, ACLs, groups changes or host chmod.
This is a small simulation, not full Linux chmod compatibility.
Owner/group/other are separate permission classes: the owner class wins first,
then the matching group, otherwise other. Permissions are not combined.
For files: r reads contents, w permits writing, x permits execution in Linux.
This lab neither writes nor executes files. On directories, x allows traversal;
r with x allows listing. Numeric bits: read=4, write=2, execute=1.
600 is owner rw only. 777 grants everyone rwx and fails least privilege here.
Paths may be relative or absolute; . and .. work within the virtual root.
Going above / is rejected (unlike a real shell staying at /). No ~, quoting,
wildcards, variables, pipelines, redirection, command chaining or host actions.
Changes take effect immediately. Verification means a successful cat after the
last permission change; changing any enabled mode clears verification evidence.'''

DIRECTORY_HELP = '''Simulated Linux terminal — declared virtual permissions only.
help
pwd
ls [-l] [PATH]
cd [PATH]                  no argument returns to the starting directory
cat PATH
chmod u+r PATH             add owner-read, preserving other bits
chmod u+x PATH             add owner-execute/search, preserving other bits
chmod NNN PATH             replace ordinary bits; exactly 3 octal digits 0–7
Only pack-enabled learner-owned files/directories may have modes changed.
For directories: r lists names; x allows entry/search and access to known children.
ls lists names with r even without x. ls -l needs r+x for child metadata; this
simulation reports an error rather than emulating Linux's partial metadata rows.
Use ls -l on the accessible parent to inspect the target directory's own mode.
For files, r reads content; w and x are modeled bits, not permission to run host
file writes or executables. Owner/group/other classes are selected, never combined.
No recursion, other symbolic forms, 4-digit modes, special bits, ACLs or chown.
Relative/absolute paths and . or .. are supported within the virtual root.
Traversal above / is rejected. Resolution is conservative: intermediate . and
trailing / require search permission; use an unadorned directory path for r-only
name listing. There is no symlink, supplementary-group or full Linux shell model.
No ~, quoting, wildcards, variables, redirection, pipes, chaining or host actions.
Changes apply immediately. Any mode change clears read/traversal verification;
repeat successful cd/cat as required by the rubric. 777 grants unnecessary access.
No learner command touches host files, processes or networks.'''


def extended(pack): return pack['domain']['schema_version'] == 3


def initial_state(pack):
    return {'filesystem': deepcopy(pack['domain']['filesystem']), 'cwd': pack['domain']['cwd'],
            'activity': {k: [] for k in (('inspected','denied','verified','traversed','listed') if extended(pack) else ('inspected','denied','verified'))}}


def validate_pack(value):
    newer = value['engine']['contract_version'] == 3
    identity = value['identity']
    require(isinstance(identity['id'], str) and re.fullmatch('[a-z][a-z0-9-]{0,63}', identity['id']), 'Invalid scenario ID.')
    require(isinstance(identity['content_version'], str) and re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', identity['content_version']), 'Invalid content version.')
    caps = value['engine']['required_capabilities']
    require(isinstance(caps,list) and all(isinstance(c,str) for c in caps) and len(caps)==len(set(caps)) and set(caps)==(DIRECTORY_CAPABILITIES if newer else CAPABILITIES), 'Unsupported permission capabilities.')
    text(value['mission']['brief'],'brief')
    require(type(value['metadata']['minutes']) is int and 1<=value['metadata']['minutes']<=240,'Invalid duration.')
    require(isinstance(value['hints'],list) and len(value['hints'])<=32,'At most 32 hints.')
    for h in value['hints']:text(h,'hint')
    d=value['domain'];keys(d,{'schema_version','filesystem','cwd','permission_targets','lesson'},'permissions domain')
    require(type(d['schema_version']) is int and d['schema_version']==(3 if newer else 2),'Unsupported permissions data version.')
    validate_nodes(d['filesystem']);require(len(d['filesystem'])<=64,'At most 64 permission nodes.')
    fs=VirtualFS(d['filesystem'])
    require(isinstance(d['cwd'],str) and canonical(d['cwd'])==d['cwd'],'Expected canonical starting directory.')
    fs.directory(d['cwd'],'/','learner')
    targets=d['permission_targets']
    require(isinstance(targets,list) and 1<=len(targets)<=16 and all(isinstance(p,str) for p in targets) and len(targets)==len(set(targets)),'Expected 1–16 unique permission targets.')
    for path in targets:
        require(path.startswith('/') and canonical(path)==path,'Expected canonical target.')
        fs.resolve(path,'/','learner');node=fs.nodes[path]
        require(node['owner']=='learner' and (node['kind']=='file' or newer and path!='/'), 'Permission targets must be learner-owned supported objects (never /).')
    objectives=value['objectives'];require(isinstance(objectives,list) and 1<=len(objectives)<=16,'Expected 1–16 objectives.')
    ids=set();modes={}
    for o in objectives:
        keys(o,{'id','label','points','predicate','params'},'permissions objective')
        text(o['id'],'objective ID',64);text(o['label'],'objective label',512)
        require(o['id'] not in ids,'Duplicate objective ID.');ids.add(o['id'])
        require(o['predicate'] in (('mode_equals','read_verified','traversal_verified') if newer else ('mode_equals','read_verified')),'Unsupported permissions predicate.')
        keys(o['params'],{'path','mode'} if o['predicate']=='mode_equals' else {'path'},'predicate parameters')
        path=o['params']['path']
        require(isinstance(path,str) and path in d['filesystem'],'Objective must name a known virtual object.')
        require(newer and o['predicate']!='mode_equals' or path in targets,'Mode objective must name an enabled target.')
        if newer and o['predicate']!='mode_equals':
            require(d['filesystem'][path]['kind']==('file' if o['predicate']=='read_verified' else 'directory'),'Verification objective has wrong node type.')
        if o['predicate']=='mode_equals':
            mode=o['params']['mode'];require(isinstance(mode,str) and re.fullmatch('0[0-7]{3}',mode),'Invalid required mode.')
            require(path not in modes or modes[path]==mode,'Conflicting required modes.');modes[path]=mode
        require(type(o['points']) is int and 1<=o['points']<=100,'Invalid points.')
    require(sum(o['points'] for o in objectives)==100,'Rubric must total 100.')
    if newer:
        require(set(modes)==set(targets),'Every mutable target needs an exact final-mode objective.')
        solved=deepcopy(d['filesystem'])
        for path,mode in modes.items():solved[path]['mode']=mode
        goal_fs=VirtualFS(solved)
        for o in objectives:
            path=o['params']['path']
            if o['predicate']=='read_verified':goal_fs.read(path,'/','learner')
            if o['predicate']=='traversal_verified':goal_fs.directory(path,'/','learner')
        from .permissions_lesson import validate_lesson
        validate_lesson(value)
        return
    for o in objectives:
        path=o['params']['path']
        if o['predicate']=='read_verified' and path in modes:
            require(int(modes[path],8)&0o400,'Verification requires owner-read in the target mode.')
    lesson=d['lesson'];keys(lesson,{'goal','target','steps'},'permissions lesson');text(lesson['goal'],'short goal',240)
    require(lesson['target'] in targets,'Unknown lesson target.')
    require(modes.get(lesson['target'])=='0600' and any(o['predicate']=='read_verified' and o['params']['path']==lesson['target'] for o in objectives),'Beginner lesson requires mode 0600 and read verification.')
    steps=lesson['steps'];require(isinstance(steps,list) and len(steps)==4,'Expected inspection, denied-read, repair and verification steps.')
    for step,action in zip(steps,('inspect','denied-read','repair','verify')):
        keys(step,{'action','explanation','expected'},'guided step');require(step['action']==action,'Unsupported guided action.')
        text(step['explanation'],'step explanation',512);text(step['expected'],'expected result',512)


def validate_state(pack,state):
    newer=extended(pack)
    keys(state,{'filesystem','cwd','activity'},'permissions state')
    nodes=state['filesystem'];validate_nodes(nodes);initial=pack['domain']['filesystem']
    require(set(nodes)==set(initial),'Virtual nodes must match the pinned tree.')
    for path,node in nodes.items():
        original=initial[path]
        require({**node,'mode':original['mode']}==original,'Only declared file modes may change.')
        if path not in pack['domain']['permission_targets']:require(node==original,'Fixed virtual mode changed.')
    require(isinstance(state['cwd'],str) and canonical(state['cwd'])==state['cwd'],'Invalid current directory.')
    fs=VirtualFS(nodes)
    if newer:
        # A directory can lose search while it is cwd; keep that state recoverable
        # via an absolute path rather than rejecting the learner's mode change.
        require(state['cwd'] in nodes and nodes[state['cwd']]['kind']=='directory','Invalid current directory.')
    else:fs.directory(state['cwd'],'/','learner')
    keys(state['activity'],{'inspected','denied','verified'} | ({'traversed','listed'} if newer else set()),'permissions evidence')
    for kind,paths in state['activity'].items():
        allowed = set(nodes) if newer else set(pack['domain']['permission_targets'])
        require(isinstance(paths,list) and len(paths)<=len(allowed) and all(isinstance(p,str) for p in paths),'Invalid evidence paths.')
        require(paths==sorted(set(paths)) and all(p in allowed for p in paths),'Invalid evidence target.')
        if kind=='verified':
            for path in paths:fs.read(path,'/','learner')
        if kind in ('listed','traversed'):
            for path in paths:
                require(nodes[path]['kind']=='directory','Expected directory evidence.')
                if kind=='traversed':fs.directory(path,'/','learner')
    return deepcopy(state)


class PermissionsEngine(NavigationEngine):
    help_text=HELP

    def __init__(self,pack,state=None):
        super().__init__(pack,state if state is not None else initial_state(pack))
        if extended(pack):self.help_text=DIRECTORY_HELP

    def validate(self,state):return validate_state(self.pack,state)
    def record(self,state,op,target):pass  # This contract records permission evidence below.

    def command(self,command):
        original=deepcopy(self.state)
        try:
            # Extend the existing tokenizer only for this exact symbolic form.
            # Existing engine contracts retain their original syntax boundary.
            symbolic = r'u\+[rx]' if extended(self.pack) else r'u\+r'
            if isinstance(command,str) and len(command)<=512 and re.fullmatch(r'[ \t]*chmod[ \t]+'+symbolic+r'[ \t]+[A-Za-z0-9_./-]+[ \t]*',command):
                op,*args=command.split()
            else:op,*args=command_words(command)
            if op=='chmod':
                require(len(args)==2 and (args[0] in (('u+r','u+x') if extended(self.pack) else ('u+r',)) or re.fullmatch('[0-7]{3}',args[0])), 'Supported: chmod u+r PATH'+(' / chmod u+x PATH' if extended(self.pack) else '')+' or chmod NNN PATH (exactly three octal digits).')
                fs=VirtualFS(original['filesystem']);path=fs.resolve(args[1],original['cwd'],'learner');node=fs.nodes[path]
                require(node['owner']=='learner','Permission denied: only the virtual owner may change this mode.')
                require(path in self.pack['domain']['permission_targets'] and (node['kind']=='file' or extended(self.pack)),'Mode changes are not enabled for this virtual object.')
                mode=format(int(node['mode'],8)|({'u+r':0o400,'u+x':0o100}[args[0]]),'04o') if args[0].startswith('u+') else '0'+args[0]
                if mode!=node['mode']:
                    node['mode']=mode;original['activity']['verified']=[]
                    if extended(self.pack):original['activity']['traversed']=[]
                self.validate(original)
                return original,'Virtual mode changed: '+path+' '+mode+('. Repeat the traversal/read checks required by this lab.' if extended(self.pack) else '. Use cat to verify read access.')
            if extended(self.pack) and op=='ls':
                state,output=self.list_directory(original,args)
            else:state,output=super().command(command)
            fs=VirtualFS(state['filesystem']);targets=self.pack['domain']['permission_targets']
            if op=='ls' and args and args[0]=='-l' and not output.startswith('Simulation:'):
                path=fs.resolve(args[1] if len(args)>1 else '.',state['cwd'],'learner')
                found=[p for p in targets if p==path or (fs.nodes[path]['kind']=='directory' and p.rsplit('/',1)[0]==path.rstrip('/'))]
                state['activity']['inspected']=sorted(set(state['activity']['inspected'])|set(found))
            if extended(self.pack):
                from .permissions_lesson import record_verification
                record_verification(state,op,args,self.state['cwd'],self.pack['domain']['cwd'])
            elif op=='cat' and len(args)==1 and not args[0].startswith('-'):
                path=fs.resolve(args[0],state['cwd'],'learner')
                if path in targets:
                    try:
                        fs.read(args[0],state['cwd'],'learner');kind='verified'
                    except ValidationError as exc:
                        kind='denied' if str(exc).startswith('Permission denied (read)') else None
                    if kind:state['activity'][kind]=sorted(set(state['activity'][kind])|{path})
            self.validate(state)
            return state,output
        except ValidationError as exc:return deepcopy(self.state),'Simulation: '+str(exc)

    def list_directory(self,state,args):
        long=bool(args and args[0]=='-l');args=args[1:] if long else args
        require(len(args)<=1 and not any(a.startswith('-') for a in args),'Supported: ls [-l] [PATH]')
        fs=VirtualFS(state['filesystem']);path=fs.resolve(args[0] if args else '.',state['cwd'],'learner');node=fs.nodes[path]
        if node['kind']=='directory':
            require(permitted(node,'learner',4),'Permission denied (list names): '+path)
            require(not long or permitted(node,'learner',1),'Permission denied (child metadata): '+path+'. Plain ls can list names with read permission; -l also needs search (x).')
            state['activity']['listed']=sorted(set(state['activity']['listed'])|{path})
        if long:output=fs.listing(path,'/','learner',True)
        elif node['kind']=='file':output=path
        else:output='\n'.join(p.rsplit('/',1)[1] for p in sorted(fs.nodes) if p!=path and parent(p)==path) or '(empty virtual directory)'
        return state,output[:16384]+ ('\n[simulated output truncated]' if len(output)>16384 else '')

    def checks(self):
        rows=[]
        for o in self.pack['objectives']:
            path=o['params']['path'];mode=self.state['filesystem'][path]['mode']
            if o['predicate']=='mode_equals':
                expected=o['params']['mode'];ok=mode==expected
                evidence='Final state: '+path+' mode '+mode+'; required '+expected+('. Match the lab\'s declared least-privilege goal.' if extended(self.pack) else '. Owner rw only; execute and group/other access are unnecessary.')
            elif o['predicate']=='traversal_verified':
                ok=path in self.state['activity']['traversed']
                evidence='Verification action: successful cd into '+path+' after the last mode change '+('recorded.' if ok else 'still needed.')
            else:
                ok=path in self.state['activity']['verified']
                evidence='Verification action: successful cat after the last mode change '+('recorded.' if ok else 'still needed.')
            rows.append({'id':o['id'],'label':o['label'],'ok':ok,'evidence':evidence,'kind':o['predicate'],'hops':[]})
        return rows


def guide(pack,state):
    if extended(pack):
        from .permissions_lesson import guide as extended_guide
        return extended_guide(pack,state)
    lesson=pack['domain']['lesson'];target=lesson['target'];mode=state['filesystem'][target]['mode'];activity=state['activity']
    complete=PermissionsEngine(pack,state).grade()['complete']
    if mode=='0600':index=3
    elif target not in activity['inspected']:index=0
    elif not int(mode,8)&0o400 and target not in activity['denied']:index=1
    else:index=2
    path=relative_path(target,state['cwd'])
    command=('ls -l '+path,'cat '+path,'chmod '+('u+r' if mode=='0200' else '600')+' '+path,'cat '+path)[index]
    return {**lesson['steps'][index],'command':command,'index':index,'total':4,'verified':complete,
            'completionMessage':'Private read/write access verified. Submit when ready.'}
