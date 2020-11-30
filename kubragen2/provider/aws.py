import copy
from typing import Any, Optional, Dict, Mapping

from ..kdata import KData_PersistentVolume, KData_PersistentVolume_CSI, KData_PersistentVolume_Config, \
    KData_PersistentVolume_Request, KData_PersistentVolumeClaim, KData_PersistentVolumeClaim_Request
from ..merger import merger


class KData_PersistentVolume_AWSElasticBlockStore(KData_PersistentVolume):
    """
    A KData_PersistentVolume_AWSElasticBlockStore PersistentVolume.
    """
    convert_csi: bool

    class Config(KData_PersistentVolume_Config):
        volumeID: Optional[str]
        fsType: Optional[str]
        readOnly: Optional[bool]

        def __init__(self, volumeID: Optional[str] = None,
                     fsType: Optional[str] = None, readOnly: Optional[bool] = None):
            super().__init__()
            self.volumeID = volumeID
            self.fsType = fsType
            self.readOnly = readOnly

    def __init__(self, convert_csi: bool = True):
        super().__init__()
        self.convert_csi = convert_csi

    def internal_build(self, req: KData_PersistentVolume_Request) -> Mapping[Any, Any]:
        ret = copy.deepcopy(super().internal_build(req))
        ret['spec']['awsElasticBlockStore'] = {}

        config = req.get_config(KData_PersistentVolume_AWSElasticBlockStore.Config)
        if isinstance(config, KData_PersistentVolume_AWSElasticBlockStore.Config):
            if config.volumeID is not None:
                ret['spec']['awsElasticBlockStore']['volumeID'] = config.volumeID
            if config.fsType is not None:
                ret['spec']['awsElasticBlockStore']['fsType'] = config.fsType
            if config.readOnly is not None:
                ret['spec']['awsElasticBlockStore']['readOnly'] = 'true' if config.readOnly else 'false'
        elif self.convert_csi:
            config = req.get_config(KData_PersistentVolume_CSI.Config)
            if isinstance(config, KData_PersistentVolume_CSI.Config):
                if isinstance(config.csi, Mapping):
                    if 'volumeHandle' in config.csi:
                        ret['spec']['awsElasticBlockStore']['volumeID'] = config.csi['volumeHandle']
                    if 'fsType' in config.csi:
                        ret['spec']['awsElasticBlockStore']['fsType'] = config.csi['fsType']
                    if 'readOnly' in config.csi:
                        ret['spec']['awsElasticBlockStore']['readOnly'] = 'true' if config.csi['readOnly'] else 'false'

        if 'volumeID' in ret['spec']['awsElasticBlockStore'] and ret['spec']['awsElasticBlockStore']['volumeID'] != '':
            ret['spec']['storageClassName'] = ''

        if config is not None and config.merge_config is not None:
            ret = merger.merge(ret, config.merge_config)
        return ret

    def build_claim(self, pvc: KData_PersistentVolumeClaim, req: KData_PersistentVolumeClaim_Request) -> Mapping[Any, Any]:
        ret = dict(super().build_claim(pvc, req))
        if req.pvreq is not None:
            pv = self.build(req.pvreq)
            if 'volumeID' in pv['spec']['awsElasticBlockStore'] and pv['spec']['awsElasticBlockStore']['volumeID'] != '':
                ret['spec']['storageClassName'] = ''
        return ret


class KData_PersistentVolume_CSI_AWSEBS(KData_PersistentVolume_CSI):
    """
    A CSI AWS EBS PersistentVolume.
    """
    nodriver: bool

    def __init__(self, clear_storageclass_if_volumehandle: bool = True, nodriver: bool = False):
        super().__init__(clear_storageclass_if_volumehandle=clear_storageclass_if_volumehandle)
        self.nodriver = nodriver

    def internal_build(self, req: KData_PersistentVolume_Request) -> Mapping[Any, Any]:
        ret = dict(super().internal_build(req))
        if not self.nodriver:
            ret['spec']['csi']['driver'] = 'ebs.csi.aws.com'
        return ret


class KData_PersistentVolume_CSI_AWSEFS(KData_PersistentVolume_CSI):
    """
    A CSI AWS EFS PersistentVolume.
    """
    nodriver: bool

    def __init__(self, clear_storageclass_if_volumehandle: bool = True, nodriver: bool = False):
        super().__init__(clear_storageclass_if_volumehandle=clear_storageclass_if_volumehandle)
        self.nodriver = nodriver

    def internal_build(self, req: KData_PersistentVolume_Request) -> Mapping[Any, Any]:
        ret = dict(super().internal_build(req))
        if not self.nodriver:
            ret['spec']['csi']['driver'] = 'efs.csi.aws.com'
        return ret
