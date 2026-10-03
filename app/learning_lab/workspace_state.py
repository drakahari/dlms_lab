"""Bounded per-attempt workspace sidecars; legacy attempt bytes stay unchanged."""
import json
from uuid import UUID
from .domain.validation import decode, keys, require
from .storage import atomic_write


EMPTY = {'command': '', 'diagnostic_revision': -1, 'diagnostics': []}


def path_for(store, attempt_id):
    require(str(UUID(attempt_id)) == attempt_id, 'Invalid workspace attempt ID.')
    return store.root / 'workspace' / (attempt_id + '.json')


def validate(value):
    keys(value, {'schema_version','command','diagnostic_revision','diagnostics'}, 'workspace state')
    require(type(value['schema_version']) is int and value['schema_version'] == 1, 'Unsupported workspace state; original is preserved.')
    require(isinstance(value['command'],str) and len(value['command'])<=512, 'Invalid pending command.')
    require(type(value['diagnostic_revision']) is int and value['diagnostic_revision']>=-1, 'Invalid diagnostic revision.')
    rows=value['diagnostics']
    require(isinstance(rows,list) and len(rows)<=128, 'Too many saved diagnostics.')
    for row in rows:
        keys(row, {'id','label','ok','evidence','kind','hops'}, 'diagnostic evidence')
        require(type(row['ok']) is bool, 'Invalid diagnostic result.')
        require(all(isinstance(row[k],str) and len(row[k])<=2048 for k in ('id','label','evidence','kind')), 'Invalid diagnostic text.')
        require(isinstance(row['hops'],list) and len(row['hops'])<=32 and all(isinstance(h,str) and len(h)<=32 for h in row['hops']), 'Invalid diagnostic path.')
    return {k:v for k,v in value.items() if k!='schema_version'}


def load_workspace(store, attempt_id):
    path=path_for(store,attempt_id)
    if not path.exists(): return dict(EMPTY)
    with path.open('rb') as stream: raw=stream.read(262145)
    return validate(decode(raw))


def save_workspace(store, attempt_id, state):
    value={'schema_version':1,**state}
    validate(value)
    path=path_for(store,attempt_id)
    if state==EMPTY and not path.exists(): return
    raw=json.dumps(value,ensure_ascii=False,indent=2).encode()
    require(len(raw)<=262144,'Workspace state exceeds 256 KiB; existing file preserved.')
    path.parent.mkdir(exist_ok=True)
    atomic_write(path,raw)
