"""Trusted lesson selection around the unchanged VM lifecycle/security controller."""
from pathlib import Path
from .files import Directory, Refused, require
from .manager import Manager
from .registry import LEGACY_ID, catalog, entry, session_binding

class Sessions:
    def __init__(self, home, profile, gate_root=None):
        self.home = Path(home).absolute(); self.profile = profile; self.gate_root = gate_root
        self.managers = {}
    def manager(self, lesson_id):
        entry(lesson_id)
        if lesson_id not in self.managers:
            self.managers[lesson_id] = Manager(self.home, session_binding(self.profile, lesson_id),
                                               self.gate_root, lesson_id=lesson_id)
        return self.managers[lesson_id]
    def selected(self):
        # Lazy read, never create VM storage during core app startup.
        if not self.home.exists(): return LEGACY_ID
        with Directory.absolute(self.home) as root:
            if not root.exists('selections'): return LEGACY_ID
            with root.child('selections') as choices:
                if not choices.exists(self.profile+'.json'): return LEGACY_ID
                return self._selection(choices.json(self.profile+'.json'))
    def _selection(self, value):
        require(isinstance(value, dict) and set(value) == {'schema_version','lesson_id'} and
                type(value['schema_version']) is int and value['schema_version'] == 1,
                'Unsupported VM selection record; preserved without replacement')
        entry(value['lesson_id']); return value['lesson_id']
    def select(self, lesson_id):
        m = self.manager(lesson_id)
        with m.access() as (root, gate, profile):
            with root.child('selections', create=True) as choices:
                name = self.profile+'.json'
                if choices.exists(name): self._selection(choices.json(name))
                choices.write(name, {'schema_version':1,'lesson_id':lesson_id}, replace=True)
    def require_record(self, m):
        with m.access() as (_, gate, profile):
            if not profile.exists('current.json'):
                require(not profile.names(), 'VM session record is missing but retained evidence exists. Resume is blocked; confirmed Reset can create a fresh session without deleting disks.')
    def view(self, lesson_id):
        m = self.manager(lesson_id)
        # Discovery delegates process verification to the approved controller. It
        # does not infer exit from sockets or signal a PID itself.
        with m.access() as (_, gate, profile): record = m.reconcile(gate)
        running_id = ''; foreign = False
        if record and record['state'] == 'running':
            if record['store'] == m.binding:
                running_id = next((e['id'] for e in catalog()['entries']
                    if session_binding(self.profile,e['id']) == record['profile']), '')
            foreign = not bool(running_id)
        error = ''
        try:
            self.require_record(m); state = m.status()
        except (ValueError, OSError) as exc:
            state = {'state':'session-unavailable','session':None,'message':str(exc)}; error = str(exc)
        running_state = ''; running_error = ''
        if running_id:
            try:
                owner = self.manager(running_id); self.require_record(owner)
                running_state = owner.status()['state']
            except (ValueError,OSError) as exc:
                # A verified running process can still be stopped safely even if
                # its progress record was lost. Never fabricate its progress.
                running_state = 'control-only'; running_error = str(exc)
        return {**state,'other_profile_running':foreign,'running_lesson_id':running_id,
                'running_title':self.manager(running_id).lesson['title'] if running_id else '',
                'running_state':running_state,'running_error':running_error,'session_error':error}
    def running_manager(self, selected_id):
        info = self.view(selected_id)
        require(bool(info['running_lesson_id']), 'No verified running lesson in this application profile; no Stop sent')
        return self.manager(info['running_lesson_id'])
