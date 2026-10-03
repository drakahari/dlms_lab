"""Navigation lifecycle and presentation for the existing Linux terminal workspace."""
from ..domain.validation import require, ValidationError
from ..scenario_identity import EngineVersion
from ..session import Session, new_attempt, now
from .engine import NavigationEngine, initial_state, validate_state, guide, HELP

RUNTIME = EngineVersion('linux-navigation', 1, 'linux-navigation-1')


class NavigationSession(Session):
    def __init__(self, pack, attempt=None, domain=None, mode='Learn'):
        super().__init__(pack, attempt or new_attempt(pack, mode, initial=initial_state(pack)), domain)

    def edit(self, field, value):
        raise ValidationError('Navigation virtual files are read-only; no editor is needed.')

    def apply(self):
        raise ValidationError('Navigation actions take effect immediately; there are no drafts to apply.')

    def execute(self, command):
        require(isinstance(command, str), 'Commands must be text.')
        if len(command) <= 512 and command.strip():
            self.attempt['commands'] = (self.attempt['commands'] + [command])[-100:]
        self.log('> ' + command[:512])
        state, output = self.engine.command(command)
        if state != self.attempt['applied']:
            self.attempt['applied'] = state
            self.attempt['revision'] += 1
        self.attempt['updated'] = now()
        for line in output.splitlines():
            for offset in range(0, max(1, len(line)), 2048): self.log(line[offset:offset+2048])


class NavigationDomain:
    # Historical workspace identifier; selecting this UI does not require a service.
    workspace = 'linux-service'
    test_message = 'Checks finished on retained simulated activity and the current directory.'

    def __init__(self, pack, diagnostics=None, constraints=None):
        self.pack = pack; self.source = 'virtual filesystem'; self.constraints = constraints or []

    def session(self, attempt=None, mode='Learn'): return NavigationSession(self.pack, attempt, self, mode)
    def engine(self, applied): return NavigationEngine(self.pack, applied)
    def validate_state(self, state): return validate_state(self.pack, state)
    def validate_draft(self, draft): require(isinstance(draft, dict) and not draft, 'Navigation has no editable drafts.')
    def diagnose(self, applied): return self.engine(applied).checks()

    def presentation(self, applied, selected):
        return {'workspaceKind': self.workspace, 'workspaceTools': ['terminal'], 'sourceDevice': self.source,
                'constraints': self.constraints, 'taskSummary': self.pack['metadata']['brief'],
                'consolePrompt': 'learner · ' + applied['cwd'], 'serviceCwd': applied['cwd'], 'terminalHelp': HELP,
                'simulationNotice': 'Simulated Linux and read-only virtual files. No host commands, processes, filesystem access or network traffic.'}

    def view_state(self, session, selected, rule_index):
        return {'hasFirewall': False, 'editable': [], 'devices': [], 'deviceLinks': '', 'inputs': {},
                'virtualFilePath': '', 'virtualFileApplied': '', 'virtualFileDraft': '', 'canEditVirtualFile': False,
                'missionGoal': self.pack['domain']['lesson']['goal'], 'conciseObjectives': [],
                'guide': guide(self.pack, session.attempt['applied']) if session.attempt['mode'] == 'Learn' else {}}
