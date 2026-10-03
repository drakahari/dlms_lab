"""Content identity only: no domain rules, hint count, Qt, or persistence."""
from dataclasses import dataclass
import hashlib
import json


CANONICALIZATION = 'oll-json-v1'
MAX_CONTENT_BYTES = 262144
MAX_DEPTH = 32


class IdentityError(ValueError):
    """Content cannot be represented by the declared canonicalization."""


@dataclass(frozen=True, slots=True)
class ScenarioIdentity:
    scenario_id: str
    content_version: str
    format_id: str
    format_version: int
    canonicalization: str
    content_digest: str


@dataclass(frozen=True, slots=True)
class EngineVersion:
    """A trusted runtime declaration, not provenance recovered from an attempt."""
    engine_id: str
    contract_version: int
    behavior_version: str


def canonical_content(value):
    """oll-json-v1 bytes; see docs/scenario-identity.md for the exact rules."""
    def check(item, depth):
        if depth > MAX_DEPTH:
            raise IdentityError('Content exceeds the canonical depth limit.')
        kind = type(item)
        if kind is str:
            try:
                item.encode('utf-8')
            except UnicodeEncodeError as exc:
                raise IdentityError('Content contains an unpaired Unicode surrogate.') from exc
        elif kind is int:
            if not -(2 ** 63) <= item < 2 ** 63:
                raise IdentityError('Canonical integers must fit signed 64 bits.')
        elif item is None or kind is bool:
            pass
        elif kind is list:
            for child in item:
                check(child, depth + 1)
        elif kind is dict:
            for key, child in item.items():
                if type(key) is not str:
                    raise IdentityError('Canonical object keys must be strings.')
                check(key, depth + 1)
                check(child, depth + 1)
        else:
            raise IdentityError('Canonical content allows only JSON values and integer numbers.')

    check(value, 0)
    raw = json.dumps(value, sort_keys=True, ensure_ascii=False,
                     separators=(',', ':'), allow_nan=False).encode('utf-8')
    if len(raw) > MAX_CONTENT_BYTES:
        raise IdentityError('Canonical content exceeds 256 KiB.')
    return raw


def content_digest(value):
    """Hash all content, with a versioned domain separator; arrays keep order."""
    raw = CANONICALIZATION.encode('ascii') + b'\x00' + canonical_content(value)
    return 'sha256:' + hashlib.sha256(raw).hexdigest()
