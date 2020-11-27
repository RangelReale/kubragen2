from typing import Any, Optional, Dict

from ..kdata import KData_PersistentVolume, KData_PersistentVolume_CSI


class KData_PersistentVolume_GCEPersistentDisk(KData_PersistentVolume):
    """
    A GCEPersistentDisk PersistentVolume.
    """
    pdName: Optional[str]
    fsType: Optional[str]
    readOnly: Optional[bool]

    def __init__(self, name: str, storageclass: Optional[str] = None, pdName: Optional[str] = None,
                 fsType: Optional[str] = None,
                 readOnly: Optional[bool] = None, merge_config: Optional[Any] = None):
        super().__init__(name=name, storageclass=storageclass, merge_config=merge_config)
        self.pdName = pdName
        self.fsType = fsType
        self.readOnly = readOnly

    def build(self) -> Any:
        ret: Dict[Any, Any] = super().build()
        ret['spec']['gcePersistentDisk'] = {}
        if self.pdName is not None:
            ret['spec']['gcePersistentDisk']['pdName'] = self.pdName
        if self.fsType is not None:
            ret['spec']['gcePersistentDisk']['fsType'] = self.fsType
        if self.readOnly is not None:
            ret['spec']['gcePersistentDisk']['readOnly'] = 'true' if self.readOnly else 'false'
        if self.pdName is not None:
            ret['spec']['storageClassName'] = ''
        return ret


class KData_PersistentVolume_CSI_GCEPD(KData_PersistentVolume_CSI):
    """
    A CSI GCEPD PersistentVolume.
    """
    nodriver: bool

    def __init__(self, name: str, csi: Any, storageclass: Optional[str] = None,
                 nodriver: bool = False, merge_config: Optional[Any] = None):
        super().__init__(name=name, csi=csi, storageclass=storageclass, merge_config=merge_config)
        self.nodriver = nodriver

    def build(self) -> Any:
        ret = super().build()
        if not self.nodriver:
            ret['spec']['csi']['driver'] = 'pd.csi.storage.gke.io'
        return ret
