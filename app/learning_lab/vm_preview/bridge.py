"""Optional Qt adapter; no QEMU dependency at import or simulated-app startup."""
import hashlib
import os
from pathlib import Path
import threading
from PySide6.QtCore import QObject, Property, Signal, Slot
from .manager import Manager
from .policy import lesson, image_spec, QEMU, QEMU_IMG

class VmBridge(QObject):
    changed=Signal()
    finished=Signal(object)
    def __init__(self,data_root,config_root,home=None,parent=None):
        super().__init__(parent)
        profile=hashlib.sha256((str(Path(data_root).absolute())+'\0'+str(Path(config_root).absolute())).encode()).hexdigest()
        self.manager=Manager(home or Path.home()/'.local/share/learning-lab-vm/preview-v1',profile)
        self._busy=False;self._state={'state':'not-started','session':None,'message':'','other_profile_running':False};self._error='';self._notice=''
        self.finished.connect(self._done)
    @Property('QVariantMap',notify=changed)
    def view(self):
        available=os.getuid()!=0 and all(os.access(p,os.X_OK) for p in (QEMU,QEMU_IMG)) and os.access('/dev/kvm',os.R_OK|os.W_OK)
        return {**self._state,'busy':self._busy,'error':self._error,'notice':self._notice,'lesson':lesson(),'image':image_spec(),'prerequisites':available,'home':str(self.manager.home)}
    def _work(self,action):
        if self._busy:return
        self._busy=True;self._error='';self.changed.emit()
        def work():
            try:
                notice=action();value={'state':self.manager.status(),'notice':notice if isinstance(notice,str) else ''}
            except Exception as exc:
                value={'error':str(exc) or type(exc).__name__}
            self.finished.emit(value)
        threading.Thread(target=work,name='LearningLabVM',daemon=True).start()
    @Slot(object)
    def _done(self,result):
        self._busy=False
        if 'error' in result:self._error=result['error']
        else:self._state=result['state'];self._notice=result['notice'] or self._notice
        self.changed.emit()
    @Slot()
    def refresh(self):self._work(lambda:None)
    @Slot(str)
    def start(self,mode):self._work(lambda:self.manager.start(mode))
    @Slot()
    def stop(self):self._work(lambda:self.manager.stop())
    @Slot(bool)
    def forceStop(self,confirmed):self._work(lambda:self.manager.stop(force=True,confirmed=confirmed))
    @Slot(str,bool)
    def reset(self,mode,confirmed):self._work(lambda:self.manager.reset(mode,confirmed))
    @Slot(str)
    def progress(self,kind):self._work(lambda:self.manager.progress(kind))
