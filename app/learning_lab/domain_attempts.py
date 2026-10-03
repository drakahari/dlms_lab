"""Domain-neutral validation for new pinned attempt schema 4.

Legacy/networking schemas and their validation remain unchanged.
"""
from datetime import datetime
from uuid import UUID
import re
from .domain.validation import keys,require,ValidationError


def validate_attempt(a,pack,domain):
    try:
        keys(a,{'id','lab_id','content_version','mode','started','updated','ended','end_reason','applied','draft','revision','hints','console','commands','assessments'},'domain attempt')
        require(isinstance(a['id'],str) and str(UUID(a['id']))==a['id'],'Invalid attempt UUID.')
        require(a['lab_id']==pack['lab_id'] and a['content_version']==pack['content_version'],'Attempt scenario mismatch.')
        require(a['mode'] in ('Learn','Challenge'),'Invalid mode.')
        for field in ('started','updated','ended'):
            if field=='ended' and a[field] is None:continue
            require(isinstance(a[field],str) and len(a[field])<=64 and datetime.fromisoformat(a[field]).tzinfo is not None,'Invalid timestamp.')
        require(a['end_reason'] in (None,'reset','mode-change'),'Invalid attempt end reason.')
        require((a['ended'] is None)==(a['end_reason'] is None),'Inconsistent ended attempt.')
        require(type(a['revision']) is int and 0<=a['revision']<=999999999999,'Invalid state revision.')
        require(type(a['hints']) is int and 0<=a['hints']<=len(pack['hints']) and (a['mode']=='Learn' or a['hints']==0),'Invalid hint history.')
        domain.validate_state(a['applied']);domain.validate_draft(a['draft'])
        for field,limit,length in (('console',500,2048),('commands',100,512)):
            require(isinstance(a[field],list) and len(a[field])<=limit and all(isinstance(v,str) and len(v)<=length for v in a[field]),'Invalid console record.')
        require(isinstance(a['assessments'],dict),'Invalid assessments.')
        for revision,result in a['assessments'].items():
            require(isinstance(revision,str) and re.fullmatch(r'0|[1-9][0-9]{0,11}',revision) and int(revision)<=a['revision'],'Invalid submission revision.')
            keys(result,{'score','complete','objectives','revision','submitted','hints_at_submission','applied'},'assessment')
            require(type(result['revision']) is int and result['revision']==int(revision),'Submission revision mismatch.')
            require(type(result['hints_at_submission']) is int and 0<=result['hints_at_submission']<=a['hints'],'Invalid submitted hint usage.')
            require(isinstance(result['submitted'],str) and len(result['submitted'])<=64 and datetime.fromisoformat(result['submitted']).tzinfo is not None,'Invalid submission time.')
            domain.validate_state(result['applied'])
            if int(revision)==a['revision']:require(result['applied']==a['applied'],'Current submission state mismatch.')
            grade=domain.engine(result['applied']).grade()
            require(all(result[k]==grade[k] for k in ('score','complete','objectives')),'Saved rubric differs from pinned state.')
        return a
    except (ValueError,TypeError,KeyError,AttributeError,OverflowError) as exc:
        raise ValidationError('Invalid domain attempt: '+str(exc)) from exc
