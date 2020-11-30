import copy
from typing import Any, Optional, Mapping

from ..kdata import KData_PersistentVolume, KData_PersistentVolume_Config, KData_PersistentVolume_Request, \
    KData_PersistentVolumeClaim, KData_PersistentVolumeClaim_Request
from ..merger import merger


class KData_PersistentVolume_AzureDisk(KData_PersistentVolume):
    """
    A AzureDisk PersistentVolume.
    """
    class Config(KData_PersistentVolume_Config):
        kind: Optional[str]
        diskName: Optional[str]
        diskURI: Optional[str]
        fsType: Optional[str]
        readOnly: Optional[bool]

        def __init__(self, kind: Optional[str] = None, diskName: Optional[str] = None,
                     diskURI: Optional[str] = None, fsType: Optional[str] = None, readOnly: Optional[bool] = None):
            super().__init__()
            self.kind = kind
            self.diskName = diskName
            self.diskURI = diskURI
            self.fsType = fsType
            self.readOnly = readOnly

    def internal_build(self, req: KData_PersistentVolume_Request) -> Mapping[Any, Any]:
        ret = copy.deepcopy(super().internal_build(req))
        ret['spec']['azureDisk'] = {}

        config = req.get_config(KData_PersistentVolume_AzureDisk.Config)
        if isinstance(config, KData_PersistentVolume_AzureDisk.Config):
            if config.kind is not None:
                ret['spec']['azureDisk']['kind'] = config.kind
            if config.diskName is not None:
                ret['spec']['azureDisk']['diskName'] = config.diskName
            if config.diskURI is not None:
                ret['spec']['azureDisk']['diskURI'] = config.diskURI
            if config.fsType is not None:
                ret['spec']['azureDisk']['fsType'] = config.fsType
            if config.readOnly is not None:
                ret['spec']['azureDisk']['readOnly'] = 'true' if config.readOnly else 'false'

        if 'diskURI' in ret['spec']['azureDisk'] and ret['spec']['azureDisk']['diskURI'] != '':
            ret['spec']['storageClassName'] = ''

        if config is not None and config.merge_config is not None:
            ret = merger.merge(ret, config.merge_config)
        return ret

    def build_claim(self, pvc: KData_PersistentVolumeClaim, req: KData_PersistentVolumeClaim_Request) -> Mapping[Any, Any]:
        ret = dict(super().build_claim(pvc, req))
        if req.pvreq is not None:
            pv = self.build(req.pvreq)
            if 'diskURI' in pv['spec']['azureDisk'] and pv['spec']['azureDisk']['diskURI'] != '':
                ret['spec']['storageClassName'] = ''
        return ret
