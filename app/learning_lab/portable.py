"""Strict, data-only portable scenarios and an immutable local repository."""
from dataclasses import dataclass, field, asdict
import json
from pathlib import Path
import re

from .domain.engine import load_pack
from .domain.validation import ValidationError, decode, keys, require, text
from .networking import NETWORKING_RUNTIME
from .domains import TRUSTED_ENGINES, resolve_engine
from .scenario_identity import ScenarioIdentity, CANONICALIZATION, content_digest, canonical_content
from .storage import atomic_write


FORMAT = 'learning-lab.scenario'
LIMIT = 262144
MAX_PACKS = 256


def engine_pack(value):
    domain = value['domain']
    if value['engine']['id'] in ('linux-service', 'linux-navigation'):
        return {'engine_id':value['engine']['id'],'lab_id':value['identity']['id'],'content_version':value['identity']['content_version'],
                'metadata':{**value['metadata'],'brief':value['mission']['brief']},'objectives':value['objectives'],
                'hints':value['hints'],'required_capabilities':value['engine']['required_capabilities'],'domain':domain}
    result = {'schema_version': 2 if 'firewall' in domain else 1,
              'lab_id': value['identity']['id'], 'content_version': value['identity']['content_version'],
              'required_capabilities': value['engine']['required_capabilities'],
              'metadata': {**value['metadata'], 'brief': value['mission']['brief']},
              'objectives': value['objectives'], 'hints': value['hints']}
    result.update({k: domain[k] for k in ('topology', 'initial_state', 'editable_fields')})
    if 'firewall' in domain:
        result.update(firewall=domain['firewall'], tcp_services=domain['tcp_services'])
    return result


@dataclass(frozen=True, slots=True)
class PortableScenario:
    identity: ScenarioIdentity
    original_bytes: bytes = field(repr=False)

    @property
    def key(self): return 'pack:' + self.identity.content_digest.split(':')[1]

    @property
    def pin(self):
        return {'scenario': asdict(self.identity), 'engine': asdict(resolve_engine(self.value()['engine'])[0])}

    def value(self): return decode(self.original_bytes)

    def legacy_pack(self): return engine_pack(self.value())

    def domain(self):
        value = self.value()
        return resolve_engine(value['engine'])[1](self.legacy_pack(), value['domain'].get('diagnostics'), value['mission']['constraints'])


def load_portable(raw):
    try:
        require(type(raw) is bytes and len(raw) <= LIMIT, 'Pack exceeds 256 KiB or is not byte data.')
        require(not raw.startswith((b'PK', b'\x1f\x8b')), 'Only self-contained JSON packs are supported; archives are not accepted.')
        value = decode(raw.decode('utf-8'))
        keys(value, {'format','schema_version','identity','engine','metadata','mission','objectives','hints','assets','domain'}, 'portable pack')
        require(value['format'] == FORMAT and type(value['schema_version']) is int and value['schema_version'] == 1,
                'Unsupported portable pack format/version; original file is preserved.')
        digest = content_digest(value)
        keys(value['identity'], {'id','content_version'}, 'identity')
        engine = value['engine']
        keys(engine, {'id','contract_version','supported_behavior_versions','required_capabilities'}, 'engine requirements')
        require(engine['id'] in TRUSTED_ENGINES, 'Required engine is not installed. Packs cannot install code.')
        runtime, _ = resolve_engine(engine)
        require(type(engine['contract_version']) is int and engine['contract_version'] == runtime.contract_version,
                'Unsupported engine contract version.')
        versions = engine['supported_behavior_versions']
        require(isinstance(versions,list) and 1 <= len(versions) <= 8 and all(isinstance(v,str) and len(v)<=64 for v in versions)
                and len(set(versions)) == len(versions) and runtime.behavior_version in versions, 'Required engine behavior is unavailable.')
        keys(value['metadata'], {'title','topic','difficulty','minutes'}, 'metadata')
        for field,limit in (('title',120),('topic',80),('difficulty',40)):
            text(value['metadata'][field],field,limit)
        keys(value['mission'], {'brief','constraints'}, 'mission')
        constraints = value['mission']['constraints']
        require(isinstance(constraints,list) and len(constraints)<=32, 'Too many constraints.')
        for constraint in constraints: text(constraint,'constraint')
        require(value['assets'] == [], 'Assets, paths, URLs, and archives are not supported by this format version.')
        if engine['id']=='linux-navigation':
            if engine['contract_version']==2:
                from .linux_navigation.permissions import validate_pack as validate_navigation, initial_state, validate_state
            else:
                from .linux_navigation.engine import validate_pack as validate_navigation, initial_state, validate_state
            validate_navigation(value)
            pack=engine_pack(value)
            validate_state(pack,initial_state(pack))
            return PortableScenario(ScenarioIdentity(value['identity']['id'],value['identity']['content_version'],FORMAT,1,CANONICALIZATION,digest),raw)
        if engine['id']=='linux-service':
            from .linux_service.engine import validate_pack as validate_service, initial_state, validate_state
            validate_service(value)
            pack=engine_pack(value)
            validate_state(pack,initial_state(pack))
            return PortableScenario(ScenarioIdentity(value['identity']['id'],value['identity']['content_version'],FORMAT,1,CANONICALIZATION,digest),raw)
        domain = value['domain']
        require(isinstance(domain,dict), 'Invalid networking domain.')
        keys(domain, {'schema_version','source_device','topology','initial_state','editable_fields','diagnostics'} |
             ({'firewall','tcp_services'} if 'firewall' in domain else set()), 'networking domain')
        require(type(domain['schema_version']) is int and domain['schema_version']==1, 'Unsupported networking data version.')
        pack = load_pack(json.dumps(engine_pack(value),ensure_ascii=False), hint_limit=32, candidate_limit=128)
        require(domain['source_device'] == next(iter(pack['initial_state'])), 'Source device differs from the editable workstation.')
        for objective in pack['objectives']: text(objective['label'],'objective label',512)
        checks = domain['diagnostics']
        require(isinstance(checks,list) and 1<=len(checks)<=32, 'Expected 1–32 diagnostics.')
        seen=set()
        ips={i['address'] for d in pack['topology']['devices'] for i in d['interfaces']}
        names={n for d in pack['topology']['devices'] for n in d['records']}
        endpoints={n for d in pack['topology']['devices'] for n in d['endpoints']}
        for check in checks:
            require(isinstance(check,dict), 'Malformed diagnostic.')
            op=check.get('operation')
            require(op in ('reach','resolve','portal','connect'), 'Unsupported diagnostic action.')
            fields={'id','label','operation'} | ({'target','port','expected'} if op=='connect' else {'target'} if op=='reach' else {'hostname'})
            keys(check,fields,'diagnostic')
            require(isinstance(check['id'],str) and re.fullmatch('[a-zA-Z0-9_-]{1,64}',check['id']) and check['id'] not in seen,'Invalid/duplicate diagnostic ID.')
            seen.add(check['id']); text(check['label'],'diagnostic label',512)
            if op in ('reach','connect'): require(check['target'] in ips,'Unknown diagnostic target.')
            else: require(check['hostname'] in (endpoints if op=='portal' else names),'Unknown diagnostic hostname.')
            if op=='connect':
                require('tcp-connect' in pack['required_capabilities'],'Diagnostic needs TCP capability.')
                require(type(check['port']) is int and 1<=check['port']<=65535 and check['expected'] in ('connected','denied'),'Invalid TCP diagnostic.')
        return PortableScenario(ScenarioIdentity(value['identity']['id'],value['identity']['content_version'],FORMAT,1,CANONICALIZATION,digest),raw)
    except (ValueError, TypeError, KeyError, AttributeError, OverflowError) as exc:
        raise ValidationError('Portable pack rejected: '+str(exc)) from exc


def portable_from_legacy(pack):
    """Reviewed data conversion for bundled examples; never touches records."""
    from .networking import NetworkingDomain
    adapter=NetworkingDomain(pack)
    domain={k:pack[k] for k in ('topology','initial_state','editable_fields')}
    domain.update(schema_version=1,source_device=adapter.source,diagnostics=adapter.diagnostics)
    if 'firewall' in pack: domain.update(firewall=pack['firewall'],tcp_services=pack['tcp_services'])
    value={'format':FORMAT,'schema_version':1,'identity':{'id':pack['lab_id'],'content_version':pack['content_version']},
           'engine':{'id':'networking','contract_version':1,'supported_behavior_versions':[NETWORKING_RUNTIME.behavior_version],
                     'required_capabilities':pack['required_capabilities']},
           'metadata':{k:v for k,v in pack['metadata'].items() if k!='brief'},
           'mission':{'brief':pack['metadata']['brief'],'constraints':adapter.constraints},
           'objectives':pack['objectives'],'hints':pack['hints'],'assets':[],'domain':domain}
    return load_portable(json.dumps(value,ensure_ascii=False,indent=2).encode())


class PackRepository:
    def __init__(self, root): self.root=Path(root)

    def scan(self):
        scenarios=[]; warnings=[]; versions={}
        paths=sorted(self.root.glob('*.json'))
        if len(paths)>MAX_PACKS:
            return [], ['Pack repository exceeds the 256-file limit; files are preserved.']
        for path in paths:
            try:
                require(path.is_file() and not path.is_symlink(), 'Pack must be a regular file, not a symlink.')
                with path.open('rb') as f: raw=f.read(LIMIT+1)
                scenario=load_portable(raw)
                require(path.stem==scenario.key[5:], 'Pack filename/content digest mismatch.')
                version=(scenario.identity.scenario_id,scenario.identity.content_version)
                require(version not in versions,'Conflicting content for the same scenario version.')
                versions[version]=scenario.key; scenarios.append(scenario)
            except (OSError,ValidationError) as exc: warnings.append(f'Preserved unavailable pack {path.name}: {exc}')
        return scenarios,warnings

    def install(self, raw):
        scenario=load_portable(raw)
        existing,warnings=self.scan()
        if len(list(self.root.glob('*.json')))>=MAX_PACKS and not any(s.key==scenario.key for s in existing):
            raise ValidationError('Pack repository capacity reached; nothing was removed.')
        for old in existing:
            if (old.identity.scenario_id,old.identity.content_version)==(scenario.identity.scenario_id,scenario.identity.content_version):
                require(old.key==scenario.key,'Same ID/version has different content; publish a new content version.')
                return old,False
        path=self.root/(scenario.key[5:]+'.json')
        require(not path.exists() and not path.is_symlink(),'Existing content file is unavailable; it will not be overwritten.')
        self.root.mkdir(parents=True,exist_ok=True)
        atomic_write(path,scenario.original_bytes)
        return scenario,True

    def import_file(self,path):
        require(Path(path).is_file(), 'Choose a regular JSON file; devices, directories, and pipes are not supported.')
        with Path(path).open('rb') as stream: raw=stream.read(LIMIT+1)
        return self.install(raw)
