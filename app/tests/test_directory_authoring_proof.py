"""Content-only derivation and real catalog lifecycle in disposable profiles."""
from copy import deepcopy
import json
from pathlib import Path
import tempfile
import unittest
from PySide6.QtCore import QCoreApplication
from learning_lab.__main__ import load_bundled_scenarios
from learning_lab.catalog import CatalogBridge
from learning_lab.domain.validation import ValidationError
from learning_lab.linux_navigation.permissions import guide
from learning_lab.portable import load_portable, PackRepository, LIMIT

APP = QCoreApplication.instance() or QCoreApplication([])
ROOT = Path(__file__).resolve().parents[1]
PACK = ROOT/'examples/linux-archive-access.lab.json'
TARGET = '/srv/fieldwork/Archive'
NOTE = TARGET+'/handover.txt'


def derive_from_template():
    """Reproducible author edits: JSON fields only, no engine customization."""
    p = json.loads((ROOT/'templates/linux-permissions.lab.json').read_bytes())
    p['identity'] = {'id':'linux-archive-access','content_version':'1.0.0'}
    p['metadata'].update(title='Read the fieldwork handover', minutes=4,
                         topic='Linux directory access · private archives')
    p['mission'] = {
        'brief':'Your private Archive contains the next fieldwork handover. Keep its name-listing access, restore entry, then enter Archive and read handover.txt. You start in /srv/fieldwork.',
        'constraints':[
            'Archive must finish at 0500: owner read and execute, no write, group or other access. Broader access is unnecessary.',
            'Successful entry and reading the handover after the last mode change are verification objectives. Either order and equivalent supported paths count. An initial failure is not required.',
            'Only Archive permissions can change. Its note is already readable and ancestors are accessible. Changes apply immediately.',
            'This is virtual-only Linux: Command reference defines the supported syntax. Plain ls lists names with read permission; ls -l needs read and search here. No full shell, host access or file execution.'
        ]}
    p['objectives'] = [
        {'id':'private-archive','label':'Final state: Archive has owner read/search only','points':70,
         'predicate':'mode_equals','params':{'path':TARGET,'mode':'0500'}},
        {'id':'entered-archive','label':'Action evidence: enter Archive after the last mode change','points':15,
         'predicate':'traversal_verified','params':{'path':TARGET}},
        {'id':'read-handover','label':'Action evidence: read the handover after the last mode change','points':15,
         'predicate':'read_verified','params':{'path':NOTE}}]
    p['hints'] = [
        'Seeing handover.txt in a list proves you can list names, not that you can enter its parent or read it.',
        'The directory owner already has read permission. Search, represented by x, is the missing access; write and access for other people are not needed.',
        'From /srv/fieldwork, chmod u+x Archive or chmod 500 Archive restores the stated access. Read Archive/handover.txt and enter Archive to verify. Mode 777 fails the privacy goal.'
    ]
    d=p['domain']; del d['filesystem']['/home/learner/notes.txt']
    def node(kind,owner,mode,content=''):
        return {'kind':kind,'owner':owner,'group':owner,'mode':mode,'content':content}
    d['filesystem'].update({
        '/srv':node('directory','root','0755'),
        '/srv/fieldwork':node('directory','learner','0755'),
        TARGET:node('directory','learner','0400'),
        NOTE:node('file','learner','0600','Fieldwork handover\nMeet at the west gate at nine. Bring the paper map.\n')})
    d['cwd']='/srv/fieldwork';d['permission_targets']=[TARGET]
    d['lesson']={'goal':'Open your private Archive and read the fieldwork handover.', 'steps':[
        {'action':'inspect','path':TARGET,'explanation':'Inspect Archive in its parent listing. The owner has r for names but lacks x for entry and search.', 'expected':'Archive appears as dr--------, owned by learner.'},
        {'action':'list','path':TARGET,'explanation':'List the names already visible inside Archive. Directory read permission provides this limited access.', 'expected':'handover.txt is listed; listing alone does not verify reading it.'},
        {'action':'repair','path':TARGET,'explanation':'Add only owner search. Preserve read; do not grant write or access to other people.', 'expected':'Archive has mode 0500. Numeric 500 is also supported; 777 is too broad.'},
        {'action':'read','path':NOTE,'explanation':'Read the known file through its path. Search permission on Archive and read permission on the note work together.', 'expected':'The fieldwork meeting instructions are displayed.'},
        {'action':'enter','path':TARGET,'explanation':'Enter Archive to verify traversal too. Reading and entry may be performed in either order.', 'expected':'The prompt shows /srv/fieldwork/Archive. Submit when ready.'}
    ]}
    return p


class DirectoryAuthoringProof(unittest.TestCase):
    def test_exact_template_derivation_and_learn(self):
        lab=load_portable(PACK.read_bytes())
        self.assertEqual(lab.value(),derive_from_template())
        self.assertEqual(lab.value()['engine'],json.loads((ROOT/'templates/linux-permissions.lab.json').read_bytes())['engine'])
        s=lab.domain().session()
        for index,cmd in enumerate(('ls -l .','ls Archive','chmod u+x Archive','cat Archive/handover.txt','cd Archive')):
            g=guide(s.pack,s.attempt['applied']);self.assertEqual((g['index'],g['command']),(index,cmd));s.execute(cmd)
        self.assertEqual(s.submit()['score'],100)

    def test_challenge_equivalence_and_wrong_fixes(self):
        lab=load_portable(PACK.read_bytes())
        for modifier,score in [('u+x',100),('500',100),('600',0),('777',30)]:
            s=lab.domain().session(mode='Challenge')
            self.assertEqual(s.domain.view_state(s,None,0)['guide'],{})
            s.execute('chmod '+modifier+' ./Archive')
            s.execute('cd /srv/fieldwork/../fieldwork/Archive');s.execute('cat '+NOTE)
            self.assertEqual(s.submit()['score'],score)
            if score==100:self.assertEqual(s.attempt['applied']['activity']['denied'],[])

    def test_catalog_import_reset_reopen_and_export_reimport(self):
        lab=load_portable(PACK.read_bytes())
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);catalogs=[]
            def build(name):
                config=root/name/'config';config.mkdir(parents=True,exist_ok=True)
                b=CatalogBridge(load_bundled_scenarios()[0],root/name/'data',config);catalogs.append(b);return b
            try:
                b=build('first');self.assertTrue(b.importPack(str(PACK)));b.selectLab(lab.key,True)
                for _ in range(5):b.execute(b.view['guide']['command'])
                b.submit();self.assertEqual(b.view['grade']['score'],100)
                completed=b.session.attempt['id'];b.restart('Learn')
                self.assertEqual(b.session.engine.grade()['score'],0)
                self.assertEqual(b.session.attempt['applied']['filesystem'][TARGET]['mode'],'0400')
                self.assertEqual(b.view['historyCount'],1)
                reset=deepcopy(b.session.attempt);b.flush()
                for entry in b.labs.values():entry.timer.stop()
                b=build('first');self.assertEqual(b.session.attempt,reset)
                b.restart('Challenge')
                for cmd in ('chmod 500 Archive','cd Archive','cat handover.txt'):b.execute(cmd)
                b.submit();self.assertEqual(b.view['grade']['score'],100)
                exported=root/'archive.lab.json';b.exportScenario(str(exported))
                self.assertEqual(exported.read_bytes(),PACK.read_bytes())
                other=build('second');self.assertTrue(other.importPack(str(exported)));other.selectLab(lab.key,True)
                self.assertEqual(other.view['historyCount'],0)
                self.assertEqual(other.session.engine.grade()['score'],0)
                self.assertEqual(other.portables[lab.key].pin,lab.pin)
                for _ in range(5):other.execute(other.view['guide']['command'])
                other.submit();self.assertEqual(other.view['grade']['score'],100)
                personal=root/'history.json';b.exportAttempt(str(personal),completed)
                with self.assertRaises(ValidationError):load_portable(personal.read_bytes())
            finally:
                for b in catalogs:
                    for entry in b.labs.values():entry.timer.stop()

    def test_invalid_imports_preserve_repository_and_source(self):
        with tempfile.TemporaryDirectory() as temp:
            root=Path(temp);repo=PackRepository(root/'packs');repo.import_file(PACK)
            before={p.name:p.read_bytes() for p in repo.root.iterdir()}
            variants=[b'PKarchive',b' '* (LIMIT+1),b'{"format":1,"format":2}']
            for mutate in (
                lambda p:p['engine'].update(contract_version=True),
                lambda p:p['engine'].update(supported_behavior_versions=['future']),
                lambda p:p['engine']['required_capabilities'].append('shell'),
                lambda p:p['domain'].update(schema_version=2),
                lambda p:p['domain']['lesson']['steps'][0].update(action='shell'),
                lambda p:p['domain']['filesystem'][TARGET].update(owner='root'),
                lambda p:p['objectives'][0]['params'].update(mode='0400'),
                lambda p:p.update(assets=['../../private']),
                lambda p:p['domain'].update(command='exec(code)'),
                lambda p:p['metadata'].update(title='Conflicting unchanged version'),
            ):
                p=derive_from_template();mutate(p);variants.append(json.dumps(p).encode())
            for raw in variants:
                source=root/'invalid.json';source.write_bytes(raw)
                with self.assertRaises(ValidationError):repo.import_file(source)
                self.assertEqual(source.read_bytes(),raw)
                self.assertEqual({p.name:p.read_bytes() for p in repo.root.iterdir()},before)
