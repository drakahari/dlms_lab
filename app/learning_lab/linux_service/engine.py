"""Pure stateful service model and allowlisted terminal; no host I/O APIs."""
from copy import deepcopy
import re
from ..domain.validation import ValidationError, require, keys, text
from .vfs import VirtualFS, validate_nodes, canonical, parent, permitted

CAPABILITIES={'virtual-filesystem','virtual-file-editor','service-lifecycle','service-journal'}
PREDICATES={'configuration_valid','document_root_accessible','service_running_current_config'}
HELP='''Simulated Linux terminal — only the in-memory lab filesystem and service.
help
pwd
ls [-l] [PATH]
cd [PATH]                     (no argument: scenario working directory)
cat PATH
mkdir [-p] PATH               (new directories: learner:learner, 0755)
systemctl status|start|restart UNIT
journalctl [-u UNIT] [-n N]   (1–100 entries; default 20)
Use the Virtual file editor to edit permitted files, then Apply changes.
No real shell, commands, filesystem, network, sudo, chmod, vim or nano.
No pipes, redirection, chaining, quoting, substitutions, globbing or variables.
Service control is an explicit lab permission. Unix owner/group/other rwx bits
are modeled; ACLs, links, device nodes and full systemd behavior are not.
mkdir and service commands take effect immediately in simulated applied state.
File drafts remain separate until Apply. Apply does not restart a service.'''


def help_text(pack):
    if pack['domain']['schema_version']==1:return HELP
    return HELP.replace('Use the Virtual file editor to edit permitted files, then Apply changes.',
                        'This beginner lesson has no configuration fault; its configuration is read-only.').replace(
                        'File drafts remain separate until Apply. Apply does not restart a service.',
                        'No file editor or configuration repair is needed in this lesson.')


def command_words(command):
    """One syntax boundary shared by execution and instructional progress."""
    require(isinstance(command,str) and len(command)<=512,'Command exceeds 512 characters.')
    require(bool(re.fullmatch(r'[A-Za-z0-9_./ \t-]+',command)),'Unsupported shell syntax. This is a simulated allowlisted terminal; type help.')
    words=command.split();require(bool(words),'Type help for supported simulated commands.')
    return words


def config(pack,state):
    service=pack['domain']['service'];fs=VirtualFS(state['filesystem'])
    raw=fs.read(service['config'],'/','www-data');values={}
    for line in raw.splitlines():
        line=line.strip()
        if not line or line.startswith('#'):continue
        key,sep,value=line.partition('=')
        require(sep and key in ('DocumentRoot','Port') and key not in values,'Configuration requires unique DocumentRoot and Port assignments.')
        values[key]=value.strip()
    require(set(values)=={'DocumentRoot','Port'},'Configuration needs DocumentRoot and Port.')
    path=values['DocumentRoot'];require(path.startswith('/'),'DocumentRoot must be an absolute virtual path.')
    normalized=canonical(path)
    allowed=service['document_root_base']
    require(normalized==allowed or normalized.startswith(allowed+'/'),'DocumentRoot must stay within '+allowed+'.')
    require(values['Port']==str(service['port']),'This scenario requires Port='+str(service['port'])+'.')
    return {'document_root':path,'port':service['port']}


def ready_config(pack,state):
    parsed=config(pack,state)
    parsed['document_root']=VirtualFS(state['filesystem']).directory(parsed['document_root'],'/','www-data',5)
    return parsed


def event(state,message):
    require(state['sequence']<1000000000,'Simulation event limit reached; reset to start a new attempt.')
    state['sequence']+=1
    state['journal']=(state['journal']+[{'sequence':state['sequence'],'message':message[:512]}])[-100:]


def start(pack,state,restart=False):
    name=pack['domain']['service']['name']
    if state['service']['status']=='active' and not restart:return name+' already active; use restart to load changed configuration.'
    if restart and state['service']['status']=='active':event(state,'Stopped '+name+' for restart.')
    try:
        loaded=ready_config(pack,state)
        state['service']={'status':'active','loaded':loaded,'error':''}
        event(state,'Started '+name+'; DocumentRoot='+loaded['document_root']+'; Port='+str(loaded['port'])+'.')
        return name+' active (simulated). No process or listener was created.'
    except ValidationError as exc:
        state['service']={'status':'failed','loaded':None,'error':str(exc)}
        event(state,'Failed '+name+': '+str(exc))
        return name+' failed: '+str(exc)+' Inspect journalctl.'


def initial_state(pack):
    state={'filesystem':deepcopy(pack['domain']['filesystem']),'cwd':pack['domain']['cwd'],
           'service':{'status':'inactive','loaded':None,'error':''},'journal':[],'sequence':0}
    if pack['domain']['schema_version']==2:
        event(state,pack['domain']['service']['name']+' is stopped; no startup has been attempted.')
    else:start(pack,state)
    return state


def validate_pack(value):
    identity=value['identity'];require(isinstance(identity['id'],str) and re.fullmatch('[a-z][a-z0-9-]{0,63}',identity['id']),'Invalid scenario ID.')
    require(isinstance(identity['content_version'],str) and re.fullmatch(r'[0-9]+\.[0-9]+\.[0-9]+',identity['content_version']),'Invalid content version.')
    intro=value['engine']['contract_version']==2
    required=CAPABILITIES|({'service-basics'} if intro else set())
    caps=value['engine']['required_capabilities'];require(isinstance(caps,list) and all(isinstance(c,str) for c in caps) and len(caps)==len(set(caps)) and set(caps)==required,'Unsupported or missing Linux-service capabilities.')
    text(value['mission']['brief'],'brief');require(type(value['metadata']['minutes']) is int and 1<=value['metadata']['minutes']<=240,'Invalid duration.')
    require(isinstance(value['hints'],list) and len(value['hints'])<=32,'At most 32 hints.')
    for hint in value['hints']:text(hint,'hint')
    d=value['domain'];keys(d,{'schema_version','filesystem','cwd','editable_files','service'}|({'initial_service','lesson'} if intro else set()),'Linux-service domain')
    require(type(d['schema_version']) is int and d['schema_version']==(2 if intro else 1),'Unsupported Linux-service data version.')
    validate_nodes(d['filesystem']);require(len(d['filesystem'])<=64,'At most 64 initial virtual nodes.')
    fs=VirtualFS(d['filesystem']);require(canonical(d['cwd'])==d['cwd'] and d['cwd'].startswith('/'),'Invalid initial working directory.')
    fs.directory(d['cwd'],'/','learner')
    service=d['service'];keys(service,{'name','config','port','document_root_base'},'service declaration')
    require(isinstance(service['name'],str) and re.fullmatch(r'[a-z][a-z0-9-]{0,31}\.service',service['name']),'Invalid service name.')
    require(type(service['port']) is int and 1<=service['port']<=65535,'Invalid required simulated port.')
    base=service['document_root_base'];require(base.startswith('/') and canonical(base)==base and base!='/','Document-root base must be a canonical virtual subdirectory.')
    fs.directory(base,'/','www-data',5)
    cfg=service['config'];require(cfg.startswith('/') and canonical(cfg)==cfg,'Configuration path must be canonical and virtual.')
    fs.read(cfg,'/','www-data');fs.read(cfg,'/','learner')
    require(d['editable_files']==([] if intro else [cfg]),'This contract fixes the editable virtual files.')
    if not intro:require(permitted(d['filesystem'][cfg],'learner',2),'The learner must have virtual write permission on configuration.')
    if intro:
        require(d['initial_service']=='inactive','Introductory services must initially be stopped.')
        lesson=d['lesson'];keys(lesson,{'goal','steps'},'beginner lesson');text(lesson['goal'],'short goal',240)
        require(isinstance(lesson['steps'],list) and len(lesson['steps'])==3,'Service basics has inspect, start and verify steps.')
        for step,action in zip(lesson['steps'],('status','start','status')):
            keys(step,{'action','explanation','expected'},'lesson step')
            require(step['action']==action,'Unsupported beginner lesson action.')
            text(step['explanation'],'command explanation',512);text(step['expected'],'expected result',512)
        # A stopped-service exercise must not hide a configuration fault.
        ready_config({'domain':d},{'filesystem':d['filesystem']})
    objectives=value['objectives'];require(isinstance(objectives,list) and 1<=len(objectives)<=16,'Invalid objectives.')
    ids=set()
    for o in objectives:
        keys(o,{'id','label','points','predicate','params'},'service objective');text(o['id'],'objective ID',64);text(o['label'],'objective label',512)
        require(o['id'] not in ids,'Duplicate objective ID.');ids.add(o['id'])
        require(o['predicate'] in PREDICATES and o['params']=={},'Unsupported service predicate or parameters.')
        require(type(o['points']) is int and 1<=o['points']<=100,'Invalid objective weight.')
    require(sum(o['points'] for o in objectives)==100,'Rubric must total 100 points.')


def validate_state(pack,state):
    keys(state,{'filesystem','cwd','service','journal','sequence'},'service state')
    nodes=state['filesystem'];validate_nodes(nodes)
    initial=pack['domain']['filesystem'];editable=pack['domain']['editable_files']
    require(set(initial)<=set(nodes),'Initial virtual nodes cannot be removed.')
    for path,node in initial.items():
        expected=deepcopy(node)
        if path in editable:expected['content']=nodes[path]['content']
        require(nodes[path]==expected,'Immutable virtual node/permissions changed.')
    fs=VirtualFS(nodes)
    for path in set(nodes)-set(initial):
        require(nodes[path]=={'kind':'directory','owner':'learner','group':'learner','mode':'0755','content':''},'Only ordinary learner-created directories may be added.')
        fs.directory(parent(path),'/','learner',3)
    require(state['cwd'].startswith('/') and canonical(state['cwd'])==state['cwd'],'Invalid saved virtual cwd.')
    fs.directory(state['cwd'],'/','learner')
    service=state['service'];keys(service,{'status','loaded','error'},'service runtime')
    require(service['status'] in ('active','failed','inactive'),'Invalid service status.')
    require(isinstance(service['error'],str) and len(service['error'])<=512,'Invalid service failure text.')
    if service['status']=='active':
        loaded=service['loaded'];keys(loaded,{'document_root','port'},'loaded service configuration')
        base=pack['domain']['service']['document_root_base'];path=loaded['document_root']
        require(isinstance(path,str) and path.startswith('/') and canonical(path)==path and (path==base or path.startswith(base+'/')),'Invalid loaded document root.')
        fs.directory(path,'/','www-data',5)
        require(type(loaded['port']) is int and loaded['port']==pack['domain']['service']['port'] and service['error']=='','Invalid loaded service values.')
    else:require(service['loaded'] is None,'Inactive/failed service cannot have loaded configuration.')
    require(type(state['sequence']) is int and 0<=state['sequence']<=1000000000,'Invalid event sequence.')
    journal=state['journal'];require(isinstance(journal,list) and len(journal)<=100,'Journal exceeds 100 retained events.')
    previous=0
    for row in journal:
        keys(row,{'sequence','message'},'journal event')
        require(type(row['sequence']) is int and previous<row['sequence']<=state['sequence'],'Invalid journal event order.')
        text(row['message'],'journal message',512);previous=row['sequence']
    require((not journal and state['sequence']==0) or (journal and previous==state['sequence']),'Journal sequence mismatch.')
    return deepcopy(state)


class ServiceEngine:
    def __init__(self,pack,state=None):self.pack=pack;self.state=deepcopy(state if state is not None else initial_state(pack))

    def command(self,command):
        state=deepcopy(self.state)
        try:
            words=command_words(command)
            op,*args=words;fs=VirtualFS(state['filesystem']);cwd=state['cwd'];unit=self.pack['domain']['service']['name']
            def valid_unit(value):require(value in (unit,unit.removesuffix('.service')),'Unknown simulated service: '+value)
            if op=='help' and not args:output=help_text(self.pack)
            elif op=='pwd' and not args:output=cwd
            elif op=='ls':
                long=bool(args and args[0]=='-l');args=args[1:] if long else args
                require(len(args)<=1 and not any(a.startswith('-') for a in args),'Supported: ls [-l] [PATH]')
                output=fs.listing(args[0] if args else '.',cwd,'learner',long)
            elif op=='cd' and len(args)<=1:
                state['cwd']=fs.directory(args[0] if args else self.pack['domain']['cwd'],cwd,'learner');output=state['cwd']
            elif op=='cat' and len(args)==1 and not args[0].startswith('-'):output=fs.read(args[0],cwd,'learner') or '(empty virtual file)'
            elif op=='mkdir':
                parents=bool(args and args[0]=='-p');args=args[1:] if parents else args
                require(len(args)==1 and not args[0].startswith('-'),'Supported: mkdir [-p] PATH')
                output='Virtual directory ready: '+fs.mkdir(args[0],cwd,'learner',parents)
            elif op=='systemctl' and len(args)==2 and args[0] in ('status','start','restart'):
                valid_unit(args[1])
                if args[0]=='status':
                    detail=state['service']['error'] or str(state['service']['loaded'])
                    if self.pack['domain']['schema_version']==2 and state['service']['status']=='inactive':detail='Stopped, with a healthy configuration. No configuration fault is present.'
                    output=unit+' — '+state['service']['status']+' (simulated)\n'+detail
                else:output=start(self.pack,state,args[0]=='restart')
            elif op=='journalctl':
                limit=20;seen=set()
                while args:
                    require(len(args)>=2 and args[0] in ('-u','-n') and args[0] not in seen,'Supported: journalctl [-u UNIT] [-n N]')
                    flag,val,*args=args;seen.add(flag)
                    if flag=='-u':valid_unit(val)
                    else:
                        require(val.isdigit() and 1<=int(val)<=100,'Journal count must be 1–100.');limit=int(val)
                output='\n'.join(f"{r['sequence']:06d} {unit}: {r['message']}" for r in state['journal'][-limit:]) or '(no simulated journal entries)'
            else:raise ValidationError('Unsupported command, action, or options. Type help. Use the Virtual file editor for changes; no host command is run.')
            validate_state(self.pack,state)
            return state,output[:16384]+('\n[simulated output truncated]' if len(output)>16384 else '')
        except ValidationError as exc:return deepcopy(self.state),'Simulation: '+str(exc)

    def checks(self):
        state=self.state
        try:config(self.pack,state);config_ok=True;config_msg='Configuration syntax and declared port/root constraints are valid.'
        except ValidationError as exc:config_ok=False;config_msg=str(exc)
        try:ready=ready_config(self.pack,state);root_ok=True;root_msg='Service user can read and traverse '+ready['document_root']+'.'
        except ValidationError as exc:ready=None;root_ok=False;root_msg=str(exc)
        running=root_ok and state['service']['status']=='active' and state['service']['loaded']==ready
        return {'configuration_valid':(config_ok,config_msg),'document_root_accessible':(root_ok,root_msg),
                'service_running_current_config':(running,'Service is active with the current applied configuration.' if running else 'Start/restart must succeed with the current applied configuration. Status: '+state['service']['status']+'.')}

    def grade(self):
        checks=self.checks();rows=[]
        for objective in self.pack['objectives']:
            ok,evidence=checks[objective['predicate']]
            rows.append({'id':objective['id'],'label':objective['label'],'possible':objective['points'],'earned':objective['points'] if ok else 0,'ok':ok,'evidence':evidence})
        score=sum(r['earned'] for r in rows)
        return {'score':score,'complete':score==100,'objectives':rows}
