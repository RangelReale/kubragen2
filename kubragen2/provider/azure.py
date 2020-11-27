from typing import Any, Optional, Dict

from ..kdata import KData_PersistentVolume


class KData_PersistentVolume_AzureDisk(KData_PersistentVolume):
    """
    A AzureDisk PersistentVolume.
    """
    kind: Optional[str]
    diskName: Optional[str]
    diskURI: Optional[str]
    fsType: Optional[str]
    readOnly: Optional[bool]

    def __init__(self, name: str, storageclass: Optional[str] = None, kind: Optional[str] = None,
                 diskName: Optional[str] = None, diskURI: Optional[str] = None, fsType: Optional[str] = None,
                 readOnly: Optional[bool] = None, merge_config: Optional[Any] = None):
        super().__init__(name=name, storageclass=storageclass, merge_config=merge_config)
        self.kind = kind
        self.diskName = diskName
        self.diskURI = diskURI
        self.fsType = fsType
        self.readOnly = readOnly

    def build(self) -> Any:
        ret: Dict[Any, Any] = super().build()
        ret['spec']['azureDisk'] = {}
        if self.kind is not None:
            ret['spec']['azureDisk']['kind'] = self.kind
        if self.diskName is not None:
            ret['spec']['azureDisk']['diskName'] = self.diskName
        if self.diskURI is not None:
            ret['spec']['azureDisk']['diskURI'] = self.diskURI
        if self.fsType is not None:
            ret['spec']['azureDisk']['fsType'] = self.fsType
        if self.readOnly is not None:
            ret['spec']['azureDisk']['readOnly'] = 'true' if self.readOnly else 'false'
        if self.kind is not None and self.kind == 'Managed':
            ret['spec']['storageClassName'] = ''
        return ret
