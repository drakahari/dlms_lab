"""New runtime pin, reused terminal/lifecycle; no UI or storage extension."""
from ..scenario_identity import EngineVersion
from ..session import Session, new_attempt
from ..linux_navigation.adapter import NavigationSession, NavigationDomain
from .engine import TextEngine, initial_state, validate_state, guide, HELP

RUNTIME=EngineVersion('linux-navigation',5,'linux-text-streams-1')

class TextSession(NavigationSession):
    def __init__(self,pack,attempt=None,domain=None,mode='Learn'):
        Session.__init__(self,pack,attempt or new_attempt(pack,mode,initial=initial_state(pack)),domain)

class TextDomain(NavigationDomain):
    test_message='Checks finished on final virtual reports and retained text-output evidence.'
    def session(self,attempt=None,mode='Learn'):return TextSession(self.pack,attempt,self,mode)
    def engine(self,applied):return TextEngine(self.pack,applied)
    def validate_state(self,state):return validate_state(self.pack,state)
    def presentation(self,applied,selected):
        return {**super().presentation(applied,selected),'terminalHelp':HELP,
                'simulationNotice':'Simulated Linux. Bounded virtual UTF-8 streams; no host shell, files, processes or network.'}
    def view_state(self,session,selected,rule_index):
        return {'hasFirewall':False,'editable':[],'devices':[],'deviceLinks':'','inputs':{},
                'virtualFilePath':'','virtualFileApplied':'','virtualFileDraft':'','canEditVirtualFile':False,
                'missionGoal':self.pack['domain']['lesson']['goal'],'conciseObjectives':[],
                'guide':guide(self.pack,session.attempt['applied']) if session.attempt['mode']=='Learn' else {}}
