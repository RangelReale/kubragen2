from typing import Any, Optional, Dict

from ..kdata import KData_PersistentVolume, KData_PersistentVolume_CSI


class KData_PersistentVolume_GCEPersistentDisk(KData_PersistentVolume):
    volumeID: Optional[str]
    fsType: Optional[str]
    readOnly: Optional[bool]

    def __init__(self, name: str, storageclass: Optional[str] = None, volumeID: Optional[str] = None,
                 fsType: Optional[str] = None, readOnly: Optional[bool] = None, merge_config: Optional[Any] = None):
        super().__init__(name=name, storageclass=storageclass, merge_config=merge_config)
        self.volumeID = volumeID
        self.fsType = fsType
        self.readOnly = readOnly

    def build(self) -> Any:
        ret: Dict[Any, Any] = super().build()
        ret['spec']['awsElasticBlockStore'] = {}

        if self.volumeID is not None:
            ret['spec']['awsElasticBlockStore']['volumeID'] = self.volumeID
        if self.fsType is not None:
            ret['spec']['awsElasticBlockStore']['fsType'] = self.fsType
        if self.readOnly is not None:
            ret['spec']['awsElasticBlockStore']['readOnly'] = 'true' if self.readOnly else 'false'
        if self.volumeID is not None:
            ret['spec']['storageClassName'] = ''
        return ret


class KData_PersistentVolume_CSI_AWSEBS(KData_PersistentVolume_CSI):
    nodriver: bool

    def __init__(self, name: str, csi: Any, storageclass: Optional[str] = None,
                 nodriver: bool = False, merge_config: Optional[Any] = None):
        super().__init__(name=name, csi=csi, storageclass=storageclass, merge_config=merge_config)
        self.nodriver = nodriver

    def build(self) -> Any:
        ret = super().build()
        if not self.nodriver:
            ret['spec']['csi']['driver'] = 'ebs.csi.aws.com'
        return ret


class KData_PersistentVolume_CSI_AWSEFS(KData_PersistentVolume_CSI):
    nodriver: bool

    def __init__(self, name: str, csi: Any, storageclass: Optional[str] = None,
                 nodriver: bool = False, merge_config: Optional[Any] = None):
        super().__init__(name=name, csi=csi, storageclass=storageclass, merge_config=merge_config)
        self.nodriver = nodriver

    def build(self) -> Any:
        ret = super().build()
        if not self.nodriver:
            ret['spec']['csi']['driver'] = 'efs.csi.aws.com'
        return ret
