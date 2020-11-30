import copy
from typing import Any, Optional, Dict, Mapping

from ..kdata import KData_PersistentVolume, KData_PersistentVolume_CSI, KData_PersistentVolume_Request, \
    KData_PersistentVolume_Config, KData_PersistentVolumeClaim, KData_PersistentVolumeClaim_Request
from ..merger import merger


class KData_PersistentVolume_GCEPersistentDisk(KData_PersistentVolume):
    """
    A GCEPersistentDisk PersistentVolume.
    """
    convert_csi: bool

    class Config(KData_PersistentVolume_Config):
        pdName: Optional[str]
        fsType: Optional[str]
        readOnly: Optional[bool]

        def __init__(self, pdName: Optional[str] = None,
                 fsType: Optional[str] = None,
                 readOnly: Optional[bool] = None, merge_config: Optional[Any] = None):
            super().__init__(merge_config=merge_config)
            self.pdName = pdName
            self.fsType = fsType
            self.readOnly = readOnly

    def __init__(self, convert_csi: bool = True):
        super().__init__()
        self.convert_csi = convert_csi

    def internal_build(self, req: KData_PersistentVolume_Request) -> Mapping[Any, Any]:
        ret = copy.deepcopy(super().internal_build(req))
        ret['spec']['gcePersistentDisk'] = {}

        config = req.get_config(KData_PersistentVolume_GCEPersistentDisk.Config)
        if isinstance(config, KData_PersistentVolume_GCEPersistentDisk.Config):
            if config.pdName is not None:
                ret['spec']['gcePersistentDisk']['pdName'] = config.pdName
            if config.fsType is not None:
                ret['spec']['gcePersistentDisk']['fsType'] = config.fsType
            if config.readOnly is not None:
                ret['spec']['gcePersistentDisk']['readOnly'] = 'true' if config.readOnly else 'false'
        elif self.convert_csi:
            config = req.get_config(KData_PersistentVolume_CSI.Config)
            if isinstance(config, KData_PersistentVolume_CSI.Config):
                if isinstance(config.csi, Mapping):
                    if 'volumeHandle' in config.csi:
                        ret['spec']['gcePersistentDisk']['pdName'] = config.csi['volumeHandle']
                    if 'fsType' in config.csi:
                        ret['spec']['gcePersistentDisk']['fsType'] = config.csi['fsType']
                    if 'readOnly' in config.csi:
                        ret['spec']['gcePersistentDisk']['readOnly'] = 'true' if config.csi['readOnly'] else 'false'

        if 'pdName' in ret['spec']['gcePersistentDisk'] and ret['spec']['gcePersistentDisk']['pdName'] != '':
            ret['spec']['storageClassName'] = ''

        if config is not None and config.merge_config is not None:
            ret = merger.merge(ret, config.merge_config)
        return ret

    def build_claim(self, pvc: KData_PersistentVolumeClaim, req: KData_PersistentVolumeClaim_Request) -> Mapping[Any, Any]:
        ret = dict(super().build_claim(pvc, req))
        if req.pvreq is not None:
            pv = self.build(req.pvreq)
            if 'pdName' in pv['spec']['gcePersistentDisk'] and pv['spec']['gcePersistentDisk']['pdName'] != '':
                ret['spec']['storageClassName'] = ''
        return ret


class KData_PersistentVolume_CSI_GCEPD(KData_PersistentVolume_CSI):
    """
    A CSI GCEPD PersistentVolume.
    """
    nodriver: bool

    def __init__(self, clear_storageclass_if_volumehandle: bool = True, nodriver: bool = False):
        super().__init__(clear_storageclass_if_volumehandle=clear_storageclass_if_volumehandle)
        self.nodriver = nodriver

    def internal_build(self, req: KData_PersistentVolume_Request) -> Mapping[Any, Any]:
        ret = dict(super().internal_build(req))
        if not self.nodriver:
            ret['spec']['csi']['driver'] = 'pd.csi.storage.gke.io'
        return ret
