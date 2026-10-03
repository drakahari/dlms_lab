"""Qt presentation bridge; simulation stays in the pure domain layer."""
from copy import deepcopy
import json
from PySide6.QtCore import QObject, Property, Signal, Slot, QTimer
from .domain.validation import ValidationError
from .session import Session, new_attempt
from .storage import atomic_write
from .theme import read_theme
from .workspace_state import load_workspace, save_workspace

class Bridge(QObject):
    changed = Signal()

    def __init__(self, pack, store, config_path, parent=None, domain=None):
        super().__init__(parent)
        self.pack, self.store, self.config_path = pack, store, config_path
        self.session = Session(pack, store.load(), domain)
        self.domain = self.session.domain
        self.diagnostics = []
        self.diagnostic_revision = -1
        self.command_draft = ""
        self.message = store.notice or f"Ready. Inspect the topology, then diagnose {self.domain.source}."
        try:
            workspace = load_workspace(store,self.session.attempt['id'])
            self.command_draft = workspace['command']
            self.diagnostics = workspace['diagnostics']
            self.diagnostic_revision = workspace['diagnostic_revision']
        except (OSError, ValueError, TypeError) as exc:
            store.read_only = True
            self.message = f'Workspace recovery required: {exc}. Original files are preserved.'
        self.page, self.history_page = 0, 0
        self.save_failed = False
        self.selected = self.domain.source
        self.rule_index = 0
        self.saved_best = None
        self.saved_complete = False
        self.history_cache = ([], 0, [])
        self.refresh_history(recount=True)
        self.force_fallback = self.config_readonly = False
        try:
            if config_path.exists():
                raw = config_path.read_bytes()
                if len(raw) > 4096:
                    raise ValueError("Preferences too large")
                config = json.loads(raw)
                if not isinstance(config, dict) or set(config) != {"schema_version", "fallback_theme"} or type(config['schema_version']) is not int or config['schema_version'] != 1 or type(config['fallback_theme']) is not bool:
                    raise ValueError("Unsupported preferences")
                self.force_fallback = config['fallback_theme']
        except (OSError, ValueError):
            self.config_readonly = True
            self.message += " Invalid or unsupported preferences preserved without modification."
        self.palette, self.theme_name = read_theme(force_fallback=self.force_fallback)
        self.timer = QTimer(self)
        self.timer.setSingleShot(True)
        self.timer.setInterval(300)
        self.timer.timeout.connect(self.flush)
        if not store.read_only:
            self.flush()

    @Property('QVariantMap', notify=changed)
    def view(self):
        a = self.session.attempt
        grade = a['assessments'].get(str(a['revision']))
        presentation = self.domain.presentation(a['applied'], self.selected)
        if 'firewall' in self.pack and self.selected == self.pack['firewall']['device']:
            presentation['deviceDetails'] += '\n' + self.policy_text(a['applied']['firewall'])
        archives, count, warnings = self.history_cache
        rows = []
        for attempt in ([a] if self.history_page == 0 else []) + archives:
            scores = list(attempt['assessments'].values())
            best = max((r['score'] for r in scores), default=None)
            rows.append({'id': attempt['id'], 'started': attempt['started'], 'mode': attempt['mode'],
                         'hints': attempt['hints'], 'score': '—' if best is None else str(best),
                         'status': attempt['end_reason'] or 'current', 'complete': any(r['complete'] for r in scores),
                         'assessments': len(scores),
                         'details': 'Applied: ' + json.dumps(attempt['applied']) + '\nDrafts: ' + json.dumps(attempt['draft']) + '\n' + ('\n'.join(f"Revision {r['revision']}: {r['score']}/100 · {r['hints_at_submission']} hints at submission\n" + '\n'.join(f"{o['earned']}/{o['possible']} {o['label']}: {o['evidence']}" for o in r['objectives']) for r in scores) or 'No submissions. Attempt preserved.')})
        scores = [r['score'] for r in a['assessments'].values()]
        if self.saved_best is not None:
            scores.append(self.saved_best)
        completed = self.saved_complete or any(r['complete'] for r in a['assessments'].values())
        started = count or a['revision'] or a['hints'] or a['draft'] or a['console'] or a['assessments']
        required_prefix = next((o['params']['value'] for o in self.pack['objectives'] if o['predicate'] == 'prefix_equals'), a['applied']['prefix'])
        source = self.session.engine.source
        firewall = 'firewall' in self.pack
        policy_draft = self.session.policy_draft() if firewall else {'default':'deny','rules':[]}
        rules = policy_draft['rules']
        selected_rule = rules[self.rule_index] if 0 <= self.rule_index < len(rules) else {'id':'','action':'deny','protocol':'tcp','source':'','destination':'','port':''}
        firewall_view = {'hasFirewall':firewall, 'firewallDevice':self.pack['firewall']['device'] if firewall else '', 'ruleIndex':self.rule_index, 'draftDefault':policy_draft['default'],
                         'ruleCount':len(rules), 'ruleInputs':selected_rule,
                         'ruleChoices':[f"{i+1}. {r['id']} · {r['action']} tcp {r['source']} → {r['destination']}:{r['port']}" for i,r in enumerate(rules)],
                         'appliedPolicy':self.policy_text(a['applied']['firewall']) if firewall else '',
                         'firewallDirty':'firewall' in a['draft']}
        links = ['%s: %s' % (segment, ' ↔ '.join(d['id'] for d in self.pack['topology']['devices'] if any(i['segment'] == segment for i in d['interfaces']))) for segment in self.pack['topology']['segments']]
        return {**presentation, **firewall_view, 'metadata': self.pack['metadata'], 'labId': self.pack['lab_id'],
                'editable': self.pack['editable_fields'][source],
                'devices': [d['id'] for d in self.pack['topology']['devices']], 'deviceLinks': '\n'.join(links),
                'objectives': self.pack['objectives'], 'rubricSummary': ' · '.join(o['label'] + ' ' + str(o['points']) for o in self.pack['objectives']),
                'attemptId': a['id'], 'mode': a['mode'], 'revision': a['revision'],
                'applied': deepcopy(a['applied']), 'inputs': {k: str(v) for k, v in {**a['applied'], **a['draft']}.items() if k != 'firewall'},
                'dirty': bool(a['draft']), 'hints': self.pack['hints'][:a['hints']] if a['mode'] == 'Learn' else [],
                'hintCount': a['hints'], 'hintTotal': len(self.pack['hints']), 'diagnostics': self.diagnostics, 'diagnosticRevision': self.diagnostic_revision, 'commandDraft': self.command_draft, 'console': '\n'.join(a['console']), 'grade': grade or {}, 'hasGrade': grade is not None,
                'message': self.message, 'readOnly': self.store.read_only, 'canRetry': self.save_failed, 'page': self.page, 'selected': self.selected,
                'palette': self.palette, 'themeName': self.theme_name,
                'fallback': self.force_fallback, 'history': rows, 'historyPage': self.history_page,
                'historyCount': count, 'historyWarnings': '\n'.join(warnings),
                'libraryBest': str(max(scores)) + '/100' if scores else 'No submissions',
                'libraryStatus': 'Completed' if completed else ('In progress' if started else 'Not started')}

    def refresh_history(self, recount=False):
        try:
            self.history_cache = self.store.history(self.session.attempt['id'], self.history_page)
            if recount:
                self.saved_best = None
                self.saved_complete = False
                for page in range((self.history_cache[1] + 24) // 25):
                    rows, _, _ = self.store.history(self.session.attempt['id'], page)
                    for attempt in rows:
                        for result in attempt['assessments'].values():
                            self.saved_best = max(self.saved_best or 0, result['score'])
                            self.saved_complete = self.saved_complete or result['complete']
        except OSError as exc:
            self.history_cache = ([], 0, [f'History cannot be read: {exc}. Files are preserved.'])

    @staticmethod
    def policy_text(value):
        lines = [f"Applied TCP policy · first match · default {value['default']}"]
        lines += [f"{i+1}. [{r['id']}] {r['action']} tcp {r['source']} → {r['destination']} port {r['port']}" for i,r in enumerate(value['rules'])]
        return '\n'.join(lines)

    def rule_action(self, callback):
        if self.store.read_only: return
        try:
            callback()
            self.message = 'Firewall draft updated. Apply validates the whole policy; tests still use applied rules.'
            self.timer.start()
        except ValidationError as exc:
            self.message = str(exc)
        self.changed.emit()

    @Slot(int)
    def selectRule(self, index):
        if 'firewall' in self.pack and 0 <= index < len(self.session.policy_draft()['rules']):
            self.rule_index = index
            self.changed.emit()

    @Slot(str, str)
    def editRule(self, field, value):
        self.rule_action(lambda: self.session.edit_rule(self.rule_index, field, value))

    @Slot(str)
    def editDefault(self, value): self.rule_action(lambda: self.session.edit_default(value))

    @Slot()
    def addRule(self):
        def add(): self.rule_index = self.session.add_rule()
        self.rule_action(add)

    @Slot()
    def removeRule(self):
        def remove():
            self.session.remove_rule(self.rule_index)
            self.rule_index = max(0,self.rule_index-1)
        self.rule_action(remove)

    @Slot(int)
    def moveRule(self, offset):
        def move(): self.rule_index = self.session.move_rule(self.rule_index, offset)
        self.rule_action(move)

    @Slot()
    def flush(self):
        self.timer.stop()
        if self.store.read_only:
            return
        try:
            self.store.save(self.session.attempt)
            save_workspace(self.store,self.session.attempt['id'],self.workspace_state())
            self.save_failed = False
        except (OSError, ValidationError) as exc:
            self.store.read_only = True
            self.save_failed = True
            self.message = f'Save failed; changes are only in memory. {exc}. Resolve storage access, then Retry save.'
        self.changed.emit()

    @Slot()
    def retrySave(self):
        if self.save_failed:
            self.store.read_only = False
            self.message = 'Progress saved after retry.'
            self.flush()

    def workspace_state(self):
        return {'command':self.command_draft,'diagnostic_revision':self.diagnostic_revision,'diagnostics':self.diagnostics}

    def edit_command(self, value):
        if self.store.read_only: return
        self.command_draft = value
        self.timer.start()

    def action(self, callback, message):
        if self.store.read_only:
            return
        try:
            result = callback()
            self.message = message
            self.flush()
            return result
        except ValidationError as exc:
            self.message = str(exc)
            self.changed.emit()

    @Slot(str, str)
    def edit(self, field, value):
        if self.store.read_only:
            return
        try:
            self.session.edit(field, value)
            self.timer.start()
            self.changed.emit()
        except ValidationError as exc:
            self.message = str(exc)
            self.changed.emit()

    @Slot()
    def apply(self):
        self.action(self.session.apply, 'Settings applied atomically. Tests and grading use this applied state.')

    @Slot(str)
    def execute(self, command):
        self.action(lambda: self.session.execute(command), 'Command evaluated in the bounded simulation.')

    @Slot()
    def test(self):
        def run():
            self.diagnostics = self.session.test()
            self.diagnostic_revision = self.session.attempt['revision']
        self.action(run, 'Tests finished on applied state. TCP results name the matching rule or default policy.' if 'firewall' in self.pack else 'Tests finished on applied state. Portal = DNS and reachability only.')

    @Slot()
    def hint(self):
        self.action(self.session.hint, 'Hint revealed and recorded. No score penalty.')

    @Slot()
    def submit(self):
        self.action(self.session.submit, 'Submission saved for this applied revision.' + (' Warning: drafts were excluded.' if self.session.attempt['draft'] else ''))

    @Slot(str)
    def restart(self, mode):
        if self.store.read_only or mode not in ('Learn', 'Challenge'):
            return
        try:
            self.timer.stop()
            save_workspace(self.store,self.session.attempt['id'],self.workspace_state())
            self.store.archive(self.session.archived('reset' if mode == self.session.attempt['mode'] else 'mode-change'))
            candidate = new_attempt(self.pack, mode)
            self.store.save(candidate)
            self.session = Session(self.pack, candidate, self.domain)
            self.diagnostics = []
            self.diagnostic_revision = -1
            self.command_draft = ""
            self.rule_index = 0
            self.message = 'New attempt started. Previous settings, drafts, hints and submissions were archived.'
            self.history_page = 0
            self.refresh_history(recount=True)
        except (OSError, ValidationError) as exc:
            self.message = f'Could not start a new attempt: {exc}. Previous records are preserved.'
            self.store.read_only = True
        self.changed.emit()

    @Slot(int)
    def navigate(self, page):
        if 0 <= page <= 2:
            self.page = page
            if page == 2:
                self.refresh_history()
            self.changed.emit()

    @Slot(str)
    def selectDevice(self, device):
        if device in self.session.engine.by_id:
            self.selected = device
            self.changed.emit()

    @Slot(int, result=str)
    def commandHistory(self, distance):
        history = self.session.attempt['commands']
        return history[-distance] if 0 < distance <= len(history) else ''

    @Slot(int)
    def historyPage(self, offset):
        _, count, _ = self.store.history(self.session.attempt['id'], self.history_page)
        self.history_page = max(0, min((max(count, 1) - 1) // 25, self.history_page + offset))
        self.refresh_history()
        self.changed.emit()

    @Slot()
    def refreshTheme(self):
        self.palette, self.theme_name = read_theme(force_fallback=self.force_fallback)
        self.changed.emit()

    @Slot(bool)
    def fallbackTheme(self, enabled):
        self.force_fallback = enabled
        if not self.config_readonly:
            try:
                atomic_write(self.config_path, json.dumps({'schema_version': 1, 'fallback_theme': enabled}).encode())
            except OSError as exc:
                self.message = f'Theme changed for this session only: {exc}'
        self.refreshTheme()
