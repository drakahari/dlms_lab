"""Trusted Linux domain adapter and attempt actions; no Qt or persistence I/O."""
from copy import deepcopy
from ..scenario_identity import EngineVersion
from ..session import Session, new_attempt, now
from ..domain.validation import require, ValidationError
from .engine import ServiceEngine, initial_state, validate_state, help_text, command_words
from .vfs import VirtualFS, MAX_FILE

RUNTIME=EngineVersion('linux-service',1,'linux-service-1')
INTRO_RUNTIME=EngineVersion('linux-service',2,'linux-service-2')


class LinuxSession(Session):
    def __init__(self,pack,attempt=None,domain=None,mode='Learn'):
        super().__init__(pack,attempt or new_attempt(pack,mode,initial=initial_state(pack)),domain)

    def edit(self,field,value):
        require(field in self.pack['domain']['editable_files'],'That virtual file is not editable.')
        require(isinstance(value,str) and len(value.encode('utf-8'))<=MAX_FILE,'Virtual file draft exceeds 8 KiB.')
        if value==self.attempt['applied']['filesystem'][field]['content']:self.attempt['draft'].pop(field,None)
        else:self.attempt['draft'][field]=value
        self.attempt['updated']=now()

    def commit_state(self,candidate):
        validate_state(self.pack,candidate)
        if candidate!=self.attempt['applied']:
            self.attempt['applied']=candidate;self.attempt['revision']+=1
        self.attempt['updated']=now()

    def apply(self):
        candidate=deepcopy(self.attempt['applied']);fs=VirtualFS(candidate['filesystem'])
        for path,value in self.attempt['draft'].items():fs.write(path,value,'learner')
        self.commit_state(candidate);self.attempt['draft']={}

    def execute(self,command):
        require(isinstance(command,str),'Commands must be text.')
        if len(command)<=512 and command.strip():self.attempt['commands']=(self.attempt['commands']+[command])[-100:]
        if self.attempt['draft']:self.log('Warning: virtual file drafts are unapplied. The terminal uses applied virtual files.')
        self.log('> '+command[:512])
        state,output=self.engine.command(command)
        self.commit_state(state)
        for line in output.splitlines():
            for offset in range(0,max(1,len(line)),2048):self.log(line[offset:offset+2048])


class LinuxServiceDomain:
    workspace='linux-service'
    def __init__(self,pack,diagnostics=None,constraints=None):
        self.pack=pack;self.source=pack['domain']['service']['name'];self.constraints=constraints or []

    def session(self,attempt=None,mode='Learn'):return LinuxSession(self.pack,attempt,self,mode)
    def engine(self,applied):return ServiceEngine(self.pack,applied)
    def validate_state(self,state):return validate_state(self.pack,state)
    def validate_draft(self,draft):
        require(isinstance(draft,dict) and set(draft)<=set(self.pack['domain']['editable_files']),'Invalid virtual-file drafts.')
        require(all(isinstance(v,str) and len(v.encode('utf-8'))<=MAX_FILE for v in draft.values()),'Invalid virtual-file draft text.')
    def diagnose(self,applied):
        return [{'id':name,'label':name.replace('_',' '),'ok':ok,'evidence':message,'kind':name,'hops':[]} for name,(ok,message) in self.engine(applied).checks().items()]
    def presentation(self,applied,selected):
        state=applied;service=state['service']
        try: listing=VirtualFS(state['filesystem']).listing(state['cwd'],'/','learner',True)
        except ValidationError as exc: listing=str(exc)
        return {'workspaceKind':self.workspace,'workspaceTools':['service','virtual-file-editor','terminal'],'sourceDevice':self.source,
                'constraints':self.constraints,'taskSummary':self.pack['metadata']['brief'],
                'consolePrompt':'learner · '+state['cwd'],
                'simulationNotice':'Simulated Linux terminal and virtual files only. No host commands, processes, filesystem access, or network traffic.',
                'serviceStatus':self.source+' · '+service['status']+'\n'+(service['error'] or 'Loaded: '+str(service['loaded'])),
                'virtualListing':listing,
                'terminalHelp':help_text(self.pack),'serviceCwd':state['cwd']}
    def view_state(self,session,selected,rule_index):
        a=session.attempt;editable=self.pack['domain']['editable_files'];path=editable[0] if editable else ''
        applied=a['applied']['filesystem'][path]['content'] if path else ''
        lesson=self.pack['domain'].get('lesson');guide={}
        if lesson and a['mode']=='Learn':
            commands=[]
            for command in a['commands']:
                try:commands.append(command_words(command))
                except ValidationError:commands.append([])
            names=(self.source,self.source.removesuffix('.service'))
            statuses=[i for i,c in enumerate(commands) if len(c)==3 and c[:2]==['systemctl','status'] and c[2] in names]
            starts=[i for i,c in enumerate(commands) if len(c)==3 and c[0]=='systemctl' and c[1] in ('start','restart') and c[2] in names]
            active=a['applied']['service']['status']=='active'
            index=2 if active else 1 if statuses else 0
            guide={**lesson['steps'][index],'index':index,'total':3,
                   'command':'systemctl '+lesson['steps'][index]['action']+' '+self.source.removesuffix('.service'),
                   'verified':bool(active and statuses and starts and statuses[-1]>starts[-1])}
        return {'hasFirewall':False,'editable':[],'devices':[],'deviceLinks':'','inputs':{},
                'virtualFilePath':path,'virtualFileApplied':applied,'virtualFileDraft':a['draft'].get(path,applied),'canEditVirtualFile':bool(editable),
                'missionGoal':lesson['goal'] if lesson else 'Get '+self.source+' running with an accessible document root.',
                'conciseObjectives':[{'configuration_valid':'Keep valid configuration.','document_root_accessible':'Make the document root accessible.',
                                      'service_running_current_config':'Run the service with the intended configuration.'}[o['predicate']] for o in self.pack['objectives']],
                'guide':guide}
