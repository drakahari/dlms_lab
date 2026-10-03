"""Separate portable-attempt envelopes; no conversion of legacy files."""
import json
from .domain.validation import decode, keys, require
from .storage import Store, MAX_RECORD, NewerSchema, encode, validate_record


class PinnedStore(Store):
    def __init__(self, root, scenario):
        self.scenario = scenario
        self.version = 3 if scenario.pin["engine"]["engine_id"] == "networking" else 4
        super().__init__(root, scenario.legacy_pack())

    def encode_record(self, attempt):
        return json.dumps({'schema_version': self.version, 'pin': self.scenario.pin, 'attempt': attempt},
                          ensure_ascii=False, indent=2).encode()

    def validate_record(self, raw):
        data = decode(raw, MAX_RECORD)
        require(isinstance(data,dict), 'Malformed portable progress.')
        if type(data.get('schema_version')) is int and data['schema_version'] > self.version:
            raise NewerSchema('Newer portable progress schema; original files are preserved read-only.')
        keys(data, {'schema_version','pin','attempt'}, 'portable progress')
        require(type(data['schema_version']) is int and data['schema_version'] == self.version, 'Unsupported portable progress schema.')
        if data['pin'] != self.scenario.pin:
            raise NewerSchema('This attempt needs different scenario content or engine behavior. Preserved read-only; no backup downgrade.')
        if self.version == 4:
            from .domain_attempts import validate_attempt
            return validate_attempt(data['attempt'],self.pack,self.scenario.domain())
        return validate_record(encode(data['attempt']), self.pack, hint_limit=len(self.pack['hints']))
