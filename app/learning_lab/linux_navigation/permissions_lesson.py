"""Contract-3 declarative lesson validation, guidance and bounded activity facts.

Trusted helpers for the existing permissions engine, not another engine.
"""
from ..domain.validation import keys, require, text, ValidationError
from ..linux_service.vfs import VirtualFS, canonical, parent
from .engine import relative_path

ACTIONS={'inspect','list','try-enter','try-read','repair','enter','read'}


def validate_lesson(value):
    d=value['domain'];nodes=d['filesystem'];lesson=d['lesson']
    keys(lesson,{'goal','steps'},'contract-3 lesson');text(lesson['goal'],'short goal',240)
    steps=lesson['steps'];require(isinstance(steps,list) and 1<=len(steps)<=16,'Expected 1–16 guided steps.')
    modes={o['params']['path'] for o in value['objectives'] if o['predicate']=='mode_equals'}
    read={o['params']['path'] for o in value['objectives'] if o['predicate']=='read_verified'}
    entered={o['params']['path'] for o in value['objectives'] if o['predicate']=='traversal_verified'}
    for step in steps:
        keys(step,{'action','path','explanation','expected'},'guided step')
        require(isinstance(step['action'],str) and step['action'] in ACTIONS,'Unknown guided action.')
        action=step['action'];path=step['path']
        require(isinstance(path,str) and path in nodes and canonical(path)==path,'Unknown guided path.')
        text(step['explanation'],'explanation',512);text(step['expected'],'expected result',512)
        if action in ('list','try-enter','enter'):require(nodes[path]['kind']=='directory','Expected guided directory.')
        if action in ('try-read','read'):require(nodes[path]['kind']=='file','Expected guided file.')
        if action=='inspect':require(path in d['permission_targets'],'Inspect must name a mutable target.')
        if action=='repair':require(path in modes,'Repair must reference a final-mode objective.')
        if action=='enter':require(path in entered,'Enter must reference a traversal objective.')
        if action=='read':require(path in read,'Read must reference a read objective.')
    require(modes <= {s['path'] for s in steps if s['action']=='repair'},'Every mode objective needs a repair step.')
    require(read <= {s['path'] for s in steps if s['action']=='read'},'Every read objective needs a verification step.')
    require(entered <= {s['path'] for s in steps if s['action']=='enter'},'Every traversal objective needs a verification step.')


def record_verification(state,op,args,starting_cwd,default_cwd):
    if op not in ('cat','cd') or any(a.startswith('-') for a in args):return
    if op=='cat' and len(args)!=1 or op=='cd' and len(args)>1:return
    fs=VirtualFS(state['filesystem']);raw=args[0] if args else default_cwd
    try:
        path=fs.resolve(raw,starting_cwd,'learner')
        if op=='cat':fs.read(raw,starting_cwd,'learner');kind='verified'
        else:fs.directory(raw,starting_cwd,'learner');kind='traversed'
    except ValidationError as exc:
        if not str(exc).startswith('Permission denied'):return
        try:path=canonical(raw,starting_cwd)
        except ValidationError:return
        if path not in fs.nodes:return
        kind='denied'
    state['activity'][kind]=sorted(set(state['activity'][kind])|{path})


def guide(pack,state):
    from .permissions import PermissionsEngine
    steps=pack['domain']['lesson']['steps'];facts=state['activity'];fs=VirtualFS(state['filesystem'])
    modes={o['params']['path']:o['params']['mode'] for o in pack['objectives'] if o['predicate']=='mode_equals'}
    def passed(step):
        action=step['action'];path=step['path']
        if action=='repair':return fs.nodes[path]['mode']==modes[path]
        if action in ('try-enter','try-read'):
            if path in facts['denied']:return True
            try:
                if action=='try-enter':fs.directory(path,'/','learner')
                else:fs.read(path,'/','learner')
                return True  # Never require an initial mistake after a repair.
            except ValidationError:return False
        return path in facts[{'inspect':'inspected','list':'listed','enter':'traversed','read':'verified'}[action]]
    complete=PermissionsEngine(pack,state).grade()['complete']
    index=len(steps)-1 if complete else next((i for i,s in enumerate(steps) if not passed(s)),len(steps)-1)
    step=steps[index];action=step['action'];path=step['path'];target=parent(path) if action=='inspect' else path
    try:fs.directory(state['cwd'],'/','learner');argument=relative_path(target,state['cwd'])
    except ValidationError:argument=target  # Recover from removing search while inside a directory.
    if action=='repair':
        old=int(fs.nodes[path]['mode'],8);desired=int(modes[path],8)
        modifier='u+r' if old|0o400==desired and old!=desired else 'u+x' if old|0o100==desired and old!=desired else modes[path][1:]
        command='chmod '+modifier+' '+argument
    else:command={'inspect':'ls -l','list':'ls','try-enter':'cd','try-read':'cat','enter':'cd','read':'cat'}[action]+' '+argument
    return {**step,'index':index,'total':len(steps),'command':command,'verified':complete,
            'completionMessage':'Permissions and verification objectives met. Submit when ready.'}
