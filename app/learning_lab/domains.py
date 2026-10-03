"""Only application-shipped domain implementations; packs cannot register code."""
from .networking import NetworkingDomain, NETWORKING_RUNTIME
from .linux_service.adapter import LinuxServiceDomain, RUNTIME as LINUX_RUNTIME, INTRO_RUNTIME
from .domain.validation import require
from .linux_navigation.adapter import NavigationDomain, RUNTIME as NAVIGATION_RUNTIME
from .linux_navigation.permissions_adapter import PermissionsDomain, RUNTIME as PERMISSIONS_RUNTIME, DIRECTORY_RUNTIME
from .linux_navigation.file_management_adapter import FileManagementDomain, RUNTIME as FILE_MANAGEMENT_RUNTIME

TRUSTED_ENGINES={
    'networking':(NETWORKING_RUNTIME,NetworkingDomain),
    'linux-navigation':(NAVIGATION_RUNTIME,NavigationDomain),
    'linux-service':(LINUX_RUNTIME,LinuxServiceDomain),
}


def resolve_engine(requirements):
    """Retain the original Linux runtime pin; new mechanics opt into contract 2."""
    require(requirements['id'] in TRUSTED_ENGINES,'Required engine is not installed. Packs cannot install code.')
    if requirements['id']=='linux-service' and type(requirements['contract_version']) is int and requirements['contract_version']==2:
        return INTRO_RUNTIME,LinuxServiceDomain
    if requirements['id']=='linux-navigation' and type(requirements['contract_version']) is int and requirements['contract_version']==2:
        return PERMISSIONS_RUNTIME,PermissionsDomain
    if requirements['id']=='linux-navigation' and type(requirements['contract_version']) is int and requirements['contract_version']==3:
        return DIRECTORY_RUNTIME,PermissionsDomain
    if requirements['id']=='linux-navigation' and type(requirements['contract_version']) is int and requirements['contract_version']==4:
        return FILE_MANAGEMENT_RUNTIME,FileManagementDomain
    return TRUSTED_ENGINES[requirements['id']]
