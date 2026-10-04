"""Exact revision selection around the existing security/lifecycle controller."""
import copy
from .manager import Manager
from .image_catalog import production_catalog
from .policy import BACKEND
from .registry import LEGACY_ID


class CatalogManager(Manager):
    def __init__(self,home,profile_key,gate_root=None,*,lesson_id=None,catalog=None):
        self.catalog=catalog if catalog is not None else production_catalog()
        self.lesson_id=lesson_id or LEGACY_ID
        spec,lesson=self.catalog.defaults(self.lesson_id)
        super().__init__(home,profile_key,gate_root,spec=spec,lesson_id=self.lesson_id)
        self.lesson=lesson
        from .image_catalog import digest
        self.pin={'backend':BACKEND,'image':self.spec,'lesson_sha256':digest(lesson)}

    def current(self,profile):
        if profile.exists('current.json'):
            saved=profile.json('current.json')
            # Resolve only trusted bundled revisions. The inherited validator still
            # checks the entire record, and generation origin is checked at Start.
            image,lesson=self.catalog.resolve(saved.get('pin'),self.lesson_id)
            self.spec=image['descriptor'];self.lesson=lesson[1]
            self.pin=copy.deepcopy(saved['pin'])
        return super().current(profile)

    def _authorize(self,operation,session):
        self.catalog.allow(self.pin,self.lesson_id,operation)
