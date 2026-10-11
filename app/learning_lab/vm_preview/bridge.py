"""Optional Qt selection adapter; no image/QEMU requirement at core startup."""
import hashlib
import os
from pathlib import Path
import threading
from PySide6.QtCore import QObject, Property, Signal, Slot
from .policy import image_spec, QEMU, QEMU_IMG
from .registry import LEGACY_ID, units, unit_for_lesson, entry, load_lesson
from .sessions import Sessions

class VmBridge(QObject):
    changed=Signal()
    finished=Signal(object)
    def __init__(self,data_root,config_root,home=None,parent=None,*,gate_root=None):
        super().__init__(parent)
        profile=hashlib.sha256((str(Path(data_root).absolute())+'\0'+str(Path(config_root).absolute())).encode()).hexdigest()
        self.sessions=Sessions(home or Path.home()/'.local/share/learning-lab-vm/preview-v1',profile,gate_root)
        self._selected=LEGACY_ID; self._error=''; self._notice=''
        try:self._selected=self.sessions.selected()
        except (ValueError,OSError) as exc:self._error=str(exc)
        self._busy=False;self._refreshing=False;self._pending=None;self._state={'state':'not-started','session':None,'message':'','other_profile_running':False,
            'running_lesson_id':'','running_title':'','running_state':'','running_error':'','session_error':''}
        self.finished.connect(self._done)
    @property
    def manager(self): return self.sessions.manager(self._selected)
    @manager.setter
    def manager(self,value):
        # Dependency injection for isolated developer fixtures only.
        self.sessions.managers[self._selected]=value; self.sessions.gate_root=value.gate_root
    @Property('QVariantMap',notify=changed)
    def view(self):
        available=os.getuid()!=0 and all(os.access(p,os.X_OK) for p in (QEMU,QEMU_IMG)) and os.access('/dev/kvm',os.R_OK|os.W_OK)
        unit=unit_for_lesson(self._selected)
        return {**self._state,'busy':self._busy,'refreshing':self._refreshing,'error':self._error,'notice':self._notice,
                'selected_lesson_id':self._selected,'unit':unit,'units':[{'id':u['id'],'title':u['title']} for u in units()], 'support':entry(self._selected),
                'choices':[{'id':e['id'],'title':load_lesson(e['id'])['title']} for e in unit['entries']],
                'lesson':self.manager.lesson,'image':self.manager.spec,'prerequisites':available,'home':str(self.manager.home)}
    def _work(self,action,lesson_id=None,*,refresh=False,target=None):
        chosen=target or lesson_id or self._selected
        try:entry(chosen)
        except ValueError as exc:self._error=str(exc);self.changed.emit();return
        if self._busy:
            if not refresh and self._refreshing and self._pending is None:
                self._pending=(action,lesson_id,chosen)
            elif not refresh:
                self._notice='A VM operation is already in progress. Wait for it before trying again.';self.changed.emit()
            return
        self._refreshing=refresh;self._busy=True;self._error='';self.changed.emit()
        def work():
            result={'selected':chosen}
            try:
                notice=action(self.sessions.manager(chosen));result['notice']=notice if isinstance(notice,str) else ''
            except Exception as exc:
                result['error']=str(exc) or type(exc).__name__
                if lesson_id:result['selected']=self._selected
            try:result['state']=self.sessions.view(result['selected'])
            except Exception as exc:
                result['error']=result.get('error') or str(exc) or type(exc).__name__
                result['state']={**self._state,'state':'control-unavailable','session':None,'session_error':str(exc)}
            self.finished.emit(result)
        threading.Thread(target=work,name='LearningLabVM',daemon=True).start()
    @Slot(object)
    def _done(self,result):
        self._busy=False;self._refreshing=False
        if self._selected!=result['selected']:self._notice=''
        self._selected=result['selected'];self._state=result['state']
        self._error=result.get('error') or self._state.get('session_error','')
        self._notice=result.get('notice') or ('' if self._error else self._notice)
        self.changed.emit()
        if self._pending:
            action,lesson_id,target=self._pending;self._pending=None
            self._work(action,lesson_id,target=target)
    @Slot(str)
    def selectLesson(self,lesson_id):
        self._work(lambda m:self.sessions.select(lesson_id),lesson_id)
    @Slot(str)
    def selectUnit(self,unit_id):
        # Unit selection is derived from a lesson, never a new persistent record.
        for unit in units():
            if unit['id']==unit_id:
                self.selectLesson(unit['entries'][0]['id']);return
        self._error='Unknown bundled VM unit';self.changed.emit()
    @Slot()
    def refresh(self):self._work(lambda m:None,refresh=True)
    @Slot(str)
    def start(self,mode):
        def action(m):self.sessions.require_record(m);return m.start(mode)
        self._work(action)
    @Slot()
    def stop(self):self._work(lambda m:self.sessions.running_manager(m.lesson['id']).stop())
    @Slot(bool)
    def forceStop(self,confirmed):self._work(lambda m:self.sessions.running_manager(m.lesson['id']).stop(force=True,confirmed=confirmed))
    @Slot(str,bool)
    def reset(self,mode,confirmed):self._work(lambda m:m.reset(mode,confirmed))
    @Slot(str)
    def progress(self,kind):
        def action(m):self.sessions.require_record(m);return m.progress(kind)
        self._work(action)
