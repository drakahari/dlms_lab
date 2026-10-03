"""Versioned permissions opt-in using the existing terminal and session lifecycle."""
from ..scenario_identity import EngineVersion
from ..session import Session, new_attempt
from .adapter import NavigationDomain, NavigationSession
from .permissions import PermissionsEngine, initial_state, validate_state, guide, HELP

RUNTIME=EngineVersion('linux-navigation',2,'linux-permissions-1')


class PermissionsSession(NavigationSession):
    def __init__(self,pack,attempt=None,domain=None,mode='Learn'):
        Session.__init__(self,pack,attempt or new_attempt(pack,mode,initial=initial_state(pack)),domain)


class PermissionsDomain(NavigationDomain):
    test_message='Checks finished on current virtual permissions and read-verification evidence.'

    def session(self,attempt=None,mode='Learn'):return PermissionsSession(self.pack,attempt,self,mode)
    def engine(self,applied):return PermissionsEngine(self.pack,applied)
    def validate_state(self,state):return validate_state(self.pack,state)

    def presentation(self,applied,selected):
        return {**super().presentation(applied,selected),'terminalHelp':HELP,
                'simulationNotice':'Simulated Linux. Only declared virtual file modes may change; file content is fixed. No host commands or network access.'}

    def view_state(self,session,selected,rule_index):
        # The navigation view is intentionally not called: its predicates differ.
        return {'hasFirewall':False,'editable':[],'devices':[],'deviceLinks':'','inputs':{},
                'virtualFilePath':'','virtualFileApplied':'','virtualFileDraft':'','canEditVirtualFile':False,
                'missionGoal':self.pack['domain']['lesson']['goal'],'conciseObjectives':[],
                'guide':guide(self.pack,session.attempt['applied']) if session.attempt['mode']=='Learn' else {}}
