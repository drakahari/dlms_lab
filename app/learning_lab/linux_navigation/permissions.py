"""Contract 2: bounded mutable file modes; no host APIs or executable pack data."""
from copy import deepcopy
import re
from ..domain.validation import keys, require, text, ValidationError
from ..linux_service.vfs import VirtualFS, canonical, validate_nodes
from ..linux_service.engine import command_words
from .engine import NavigationEngine, relative_path

CAPABILITIES = {'virtual-filesystem', 'file-navigation', 'activity-evidence', 'mutable-permissions'}
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


def initial_state(pack):
    return {'filesystem': deepcopy(pack['domain']['filesystem']), 'cwd': pack['domain']['cwd'],
            'activity': {'inspected': [], 'denied': [], 'verified': []}}


def validate_pack(value):
    identity = value['identity']
    require(isinstance(identity['id'], str) and re.fullmatch('[a-z][a-z0-9-]{0,63}', identity['id']), 'Invalid scenario ID.')
    require(isinstance(identity['content_version'], str) and re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+', identity['content_version']), 'Invalid content version.')
    caps = value['engine']['required_capabilities']
    require(isinstance(caps,list) and all(isinstance(c,str) for c in caps) and len(caps)==len(set(caps)) and set(caps)==CAPABILITIES, 'Unsupported permission capabilities.')
    text(value['mission']['brief'],'brief')
    require(type(value['metadata']['minutes']) is int and 1<=value['metadata']['minutes']<=240,'Invalid duration.')
    require(isinstance(value['hints'],list) and len(value['hints'])<=32,'At most 32 hints.')
    for h in value['hints']:text(h,'hint')
    d=value['domain'];keys(d,{'schema_version','filesystem','cwd','permission_targets','lesson'},'permissions domain')
    require(type(d['schema_version']) is int and d['schema_version']==2,'Unsupported permissions data version.')
    validate_nodes(d['filesystem']);require(len(d['filesystem'])<=64,'At most 64 permission nodes.')
    fs=VirtualFS(d['filesystem'])
    require(isinstance(d['cwd'],str) and canonical(d['cwd'])==d['cwd'],'Expected canonical starting directory.')
    fs.directory(d['cwd'],'/','learner')
    targets=d['permission_targets']
    require(isinstance(targets,list) and 1<=len(targets)<=16 and all(isinstance(p,str) for p in targets) and len(targets)==len(set(targets)),'Expected 1–16 unique permission targets.')
    for path in targets:
        require(path.startswith('/') and canonical(path)==path,'Expected canonical target.')
        fs.resolve(path,'/','learner');node=fs.nodes[path]
        require(node['kind']=='file' and node['owner']=='learner','Permission targets must be learner-owned regular files.')
    objectives=value['objectives'];require(isinstance(objectives,list) and 1<=len(objectives)<=16,'Expected 1–16 objectives.')
    ids=set();modes={}
    for o in objectives:
        keys(o,{'id','label','points','predicate','params'},'permissions objective')
        text(o['id'],'objective ID',64);text(o['label'],'objective label',512)
        require(o['id'] not in ids,'Duplicate objective ID.');ids.add(o['id'])
        require(o['predicate'] in ('mode_equals','read_verified'),'Unsupported permissions predicate.')
        keys(o['params'],{'path','mode'} if o['predicate']=='mode_equals' else {'path'},'predicate parameters')
        path=o['params']['path'];require(path in targets,'Objective must name an enabled file.')
        if o['predicate']=='mode_equals':
            mode=o['params']['mode'];require(isinstance(mode,str) and re.fullmatch('0[0-7]{3}',mode),'Invalid required mode.')
            require(path not in modes or modes[path]==mode,'Conflicting required modes.');modes[path]=mode
        require(type(o['points']) is int and 1<=o['points']<=100,'Invalid points.')
    require(sum(o['points'] for o in objectives)==100,'Rubric must total 100.')
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
    keys(state,{'filesystem','cwd','activity'},'permissions state')
    nodes=state['filesystem'];validate_nodes(nodes);initial=pack['domain']['filesystem']
    require(set(nodes)==set(initial),'Virtual nodes must match the pinned tree.')
    for path,node in nodes.items():
        original=initial[path]
        require({**node,'mode':original['mode']}==original,'Only declared file modes may change.')
        if path not in pack['domain']['permission_targets']:require(node==original,'Fixed virtual mode changed.')
    require(isinstance(state['cwd'],str) and canonical(state['cwd'])==state['cwd'],'Invalid current directory.')
    fs=VirtualFS(nodes);fs.directory(state['cwd'],'/','learner')
    keys(state['activity'],{'inspected','denied','verified'},'permissions evidence')
    for kind,paths in state['activity'].items():
        require(isinstance(paths,list) and len(paths)<=len(pack['domain']['permission_targets']) and all(isinstance(p,str) for p in paths),'Invalid evidence paths.')
        require(paths==sorted(set(paths)) and all(p in pack['domain']['permission_targets'] for p in paths),'Invalid evidence target.')
        if kind=='verified':
            for path in paths:fs.read(path,'/','learner')
    return deepcopy(state)


class PermissionsEngine(NavigationEngine):
    help_text=HELP

    def __init__(self,pack,state=None):
        super().__init__(pack,state if state is not None else initial_state(pack))

    def validate(self,state):return validate_state(self.pack,state)
    def record(self,state,op,target):pass  # This contract records permission evidence below.

    def command(self,command):
        original=deepcopy(self.state)
        try:
            # Extend the existing tokenizer only for this exact symbolic form.
            # Existing engine contracts retain their original syntax boundary.
            if isinstance(command,str) and len(command)<=512 and re.fullmatch(r'[ \t]*chmod[ \t]+u\+r[ \t]+[A-Za-z0-9_./-]+[ \t]*',command):
                op,*args=command.split()
            else:op,*args=command_words(command)
            if op=='chmod':
                require(len(args)==2 and (args[0]=='u+r' or re.fullmatch('[0-7]{3}',args[0])), 'Supported: chmod u+r PATH or chmod NNN PATH (exactly three octal digits).')
                fs=VirtualFS(original['filesystem']);path=fs.resolve(args[1],original['cwd'],'learner');node=fs.nodes[path]
                require(node['owner']=='learner','Permission denied: only the virtual owner may change this mode.')
                require(path in self.pack['domain']['permission_targets'] and node['kind']=='file','Mode changes are not enabled for this virtual object.')
                mode=format(int(node['mode'],8)|0o400,'04o') if args[0]=='u+r' else '0'+args[0]
                if mode!=node['mode']:
                    node['mode']=mode;original['activity']['verified']=[]
                self.validate(original)
                return original,'Virtual mode changed: '+path+' '+mode+'. Use cat to verify read access.'
            state,output=super().command(command)
            fs=VirtualFS(state['filesystem']);targets=self.pack['domain']['permission_targets']
            if op=='ls' and args and args[0]=='-l' and not output.startswith('Simulation:'):
                path=fs.resolve(args[1] if len(args)>1 else '.',state['cwd'],'learner')
                found=[p for p in targets if p==path or (fs.nodes[path]['kind']=='directory' and p.rsplit('/',1)[0]==path.rstrip('/'))]
                state['activity']['inspected']=sorted(set(state['activity']['inspected'])|set(found))
            if op=='cat' and len(args)==1 and not args[0].startswith('-'):
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

    def checks(self):
        rows=[]
        for o in self.pack['objectives']:
            path=o['params']['path'];mode=self.state['filesystem'][path]['mode']
            if o['predicate']=='mode_equals':
                expected=o['params']['mode'];ok=mode==expected
                evidence='Final state: '+path+' mode '+mode+'; required '+expected+'. Owner rw only; execute and group/other access are unnecessary.'
            else:
                ok=path in self.state['activity']['verified']
                evidence='Verification action: successful cat after the last mode change '+('recorded.' if ok else 'still needed.')
            rows.append({'id':o['id'],'label':o['label'],'ok':ok,'evidence':evidence,'kind':o['predicate'],'hops':[]})
        return rows


def guide(pack,state):
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
