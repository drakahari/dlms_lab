"""Checkpoint 1 adapter for the bundled gateway/DNS format; performs no I/O."""
from dataclasses import dataclass, field

from .domain.engine import load_pack
from .domain.validation import ValidationError, decode
from .scenario_identity import (
    CANONICALIZATION, MAX_CONTENT_BYTES, EngineVersion, IdentityError,
    ScenarioIdentity, content_digest,
)


LEGACY_FORMAT = 'omarchy-learning-lab.legacy-network'
# These describe the reviewed runtime starting at checkpoint 1. They were not
# recorded by earlier attempts, and are never inserted into legacy records.
NETWORK_ENGINE = EngineVersion('networking', 1, 'legacy-1')


class CompatibilityError(ValueError):
    pass


@dataclass(frozen=True, slots=True)
class LegacyGatewayScenario:
    identity: ScenarioIdentity
    runtime: EngineVersion
    original_bytes: bytes = field(repr=False)

    def legacy_pack(self):
        """Return a fresh original-order dictionary for the unchanged app API."""
        return decode(self.original_bytes)


def adapt_gateway_dns(raw, *, runtime=NETWORK_ENGINE):
    """Validate and identify an existing pack without adding or changing keys.

    Runtime requirements are supplied by trusted application code. Legacy pack
    JSON contains no engine-contract/behavior declaration. No newer portable
    format, registry, record migration, or content-version selection is implied.
    """
    if (not isinstance(runtime, EngineVersion)
            or type(runtime.contract_version) is not int
            or runtime != NETWORK_ENGINE):
        raise CompatibilityError('Unsupported networking engine contract or behavior version.')
    if type(raw) is not bytes or len(raw) > MAX_CONTENT_BYTES:
        raise CompatibilityError('Legacy scenario must be UTF-8 bytes, at most 256 KiB.')
    try:
        # Explicit UTF-8 prevents json.loads(bytes) accepting UTF-16/32 or a BOM.
        text = raw.decode('utf-8')
        pack = decode(text)
        if not isinstance(pack, dict) or type(pack.get('schema_version')) is not int or pack['schema_version'] != 1:
            raise CompatibilityError('Gateway adapter supports legacy pack format version 1 only.')
        if pack.get('lab_id') != 'gateway-dns':
            raise CompatibilityError('This checkpoint adapter supports gateway-dns only.')
        digest = content_digest(pack)
        # Retain existing structural, capability, hint, and feasibility rules.
        # In particular, three hints is a legacy format rule, not an identity rule.
        load_pack(text)
    except (UnicodeError, ValidationError, IdentityError) as exc:
        raise CompatibilityError(f'Invalid legacy gateway scenario: {exc}') from exc
    identity = ScenarioIdentity(
        scenario_id=pack['lab_id'], content_version=pack['content_version'],
        format_id=LEGACY_FORMAT, format_version=pack['schema_version'],
        canonicalization=CANONICALIZATION, content_digest=digest,
    )
    return LegacyGatewayScenario(identity, runtime, raw)
