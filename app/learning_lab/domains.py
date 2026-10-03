"""Only application-shipped domain implementations; packs cannot register code."""
from .networking import NetworkingDomain, NETWORKING_RUNTIME
from .linux_service.adapter import LinuxServiceDomain, RUNTIME as LINUX_RUNTIME, INTRO_RUNTIME
from .domain.validation import require

TRUSTED_ENGINES={
    'networking':(NETWORKING_RUNTIME,NetworkingDomain),
    'linux-service':(LINUX_RUNTIME,LinuxServiceDomain),
}


def resolve_engine(requirements):
    """Retain the original Linux runtime pin; new mechanics opt into contract 2."""
    require(requirements['id'] in TRUSTED_ENGINES,'Required engine is not installed. Packs cannot install code.')
    if requirements['id']=='linux-service' and type(requirements['contract_version']) is int and requirements['contract_version']==2:
        return INTRO_RUNTIME,LinuxServiceDomain
    return TRUSTED_ENGINES[requirements['id']]
