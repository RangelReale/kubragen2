import copy
from typing import Optional, Mapping, Any, Dict, Sequence, Type

from .data import Data
from .exception import InvalidParamError
from .merger import merger


class KData(Data):
    """
    Base data for Kubernetes objects
    """
    pass


class KData_Manual(KData):
    """
    A :class:`KData` that merges value manually.

    :param merge_config: A Mapping to merge on the result.
    """
    merge_config: Mapping[Any, Any]

    def __init__(self, merge_config: Mapping[Any, Any] = None):
        self.merge_config = merge_config


class KData_Value(KData):
    """
    A :class:`KData` with a constant value.

    :param value: the data value
    """
    value: Any

    def __init__(self, value: Any):
        self.value = value


class KData_ConfigMap(KData):
    """
    A :class:`KData` that represents a Kubernetes ConfigMap item.

    :param configmapName: ConfigMap name
    :param configmapData: ConfigMap data name
    """
    configmapName: str
    configmapData: str

    def __init__(self, configmapName: str, configmapData: str):
        self.configmapName = configmapName
        self.configmapData = configmapData


class KData_Secret(KData):
    """
    A :class:`KData` that represents a Kubernetes Secret item.

    :param secretName: Secret name
    :param secretData: Secret data name
    """
    secretName: str
    secretData: str

    def __init__(self, secretName: str, secretData: str):
        self.secretName = secretName
        self.secretData = secretData


class KData_Env(KData):
    """
    A :class:`KData` that represents a Kubernetes `container.env` value.

    :param name: Env name
    :param value: Env value. Can be another :class:`KData`.
    """
    name: str
    value: Any

    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value


class KData_StorageClass(KData):
    """
    A :class:`KData` that represents a Kubernetes storage class.

    :param name: Storage class name
    """
    name: str

    def __init__(self, name: str):
        self.name = name

    def get_value(self) -> Any:
        return {
            'apiVersion': 'storage.k8s.io/v1',
            'kind': 'StorageClass',
            'metadata': {
                'name': self.name,
            },
        }


class KData_PersistentVolume_Config:
    merge_config: Optional[Mapping[Any, Any]]

    def __init__(self, merge_config: Optional[Mapping[Any, Any]] = None):
        self.merge_config = merge_config


class KData_PersistentVolume_Request:
    name: str
    selector_labels: Optional[Mapping[str, Any]]
    storageclassname: Optional[str]
    storage: Optional[str]
    access_modes: Optional[Sequence[str]]
    merge_config: Optional[Mapping[Any, Any]]
    configs: Optional[Sequence[KData_PersistentVolume_Config]]

    def __init__(self, name: str, selector_labels: Optional[Mapping[str, Any]] = None,
                 storageclassname: Optional[str] = None, storage: Optional[str] = None,
                 access_modes: Optional[Sequence[str]] = None,
                 merge_config: Optional[Mapping[Any, Any]] = None,
                 configs: Optional[Sequence[KData_PersistentVolume_Config]] = None):
        self.name = name
        self.selector_labels = selector_labels
        self.storageclassname = storageclassname
        self.storage = storage
        self.access_modes = access_modes
        self.merge_config = merge_config
        self.configs = configs

    def get_config(self, cls: Type[KData_PersistentVolume_Config]) -> Optional[KData_PersistentVolume_Config]:
        if self.configs is not None:
            for c in self.configs:
                if isinstance(c, cls):
                    return c
        return None


class KData_PersistentVolume(KData):
    """
    A :class:`KData` that represents a Kubernetes PersistentVolume.

    :param name: Persistent volume name
    :param storageclass: storage class
    :param merge_config: A Mapping to merge on the result.
    """
    def internal_build(self, req: KData_PersistentVolume_Request) -> Mapping[Any, Any]:
        ret: Dict[Any, Any] = {
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': req.name,
            },
            'spec': {
            },
        }
        if req.storageclassname is not None:
            ret['spec']['storageClassName'] = req.storageclassname
        if req.selector_labels is not None:
            ret['metadata']['labels'] = req.selector_labels
        if req.storage is not None:
            ret['spec']['capacity'] = {
                'storage': req.storage,
            }
        if req.access_modes is not None:
            ret['spec']['accessModes'] = req.access_modes
        return ret

    def build(self, req: KData_PersistentVolume_Request) -> Mapping[Any, Any]:
        return merger.merge(copy.deepcopy(self.internal_build(req)), req.merge_config if req.merge_config is not None else {})

    def build_claim(self, pvc: 'KData_PersistentVolumeClaim', req: 'KData_PersistentVolumeClaim_Request') -> Mapping[Any, Any]:
        return pvc.build(req)


class KData_PersistentVolume_EmptyDir(KData_PersistentVolume):
    """
    A :class:`KData` that represents a Kubernetes PersistentVolume of type EmptyDir.
    """
    def internal_build(self, req: KData_PersistentVolume_Request) -> Mapping[Any, Any]:
        return merger.merge(self.internal_build(req), {
            'spec': {
                'emptyDir': {}
            },
        })


class KData_PersistentVolume_HostPath(KData_PersistentVolume):
    """
    A :class:`KData` that represents a Kubernetes PersistentVolume of type HostPath.

    :param name: Persistent volume name
    :param hostpath: the hostPath path, normally a Mapping with a `path` key.
    :param storageclass: storage class
    :param merge_config: A Mapping to merge on the result.
    """
    class Config(KData_PersistentVolume_Config):
        hostpath: Mapping[Any, Any]

        def __init__(self, hostpath: Mapping[Any, Any], merge_config: Optional[Mapping[Any, Any]] = None):
            super().__init__(merge_config=merge_config)
            self.hostpath = hostpath

    def internal_build(self, req: KData_PersistentVolume_Request) -> Mapping[Any, Any]:
        config = req.get_config(KData_PersistentVolume_HostPath.Config)
        if not isinstance(config, KData_PersistentVolume_HostPath.Config):
            raise InvalidParamError('Could not find configuration for PersistentVolume type hostPath')

        ret = merger.merge(copy.deepcopy(super().internal_build(req)), {
            'spec': {
                'hostPath': config.hostpath,
            },
        })
        return ret


class KData_PersistentVolume_NFS(KData_PersistentVolume):
    """
    A :class:`KData` that represents a Kubernetes PersistentVolume of type NFS.

    :param name: Persistent volume name
    :param hostpath: the nfs configuration, normally a Mapping
    :param storageclass: storage class
    :param merge_config: A Mapping to merge on the result.
    """
    class Config(KData_PersistentVolume_Config):
        nfs: Any

        def __init__(self, nfs: Any, merge_config: Optional[Mapping[Any, Any]] = None):
            super().__init__(merge_config=merge_config)
            self.nfs = nfs

    def internal_build(self, req: KData_PersistentVolume_Request) -> Mapping[Any, Any]:
        config = req.get_config(KData_PersistentVolume_NFS.Config)
        if not isinstance(config, KData_PersistentVolume_NFS.Config):
            raise InvalidParamError('Could not find configuration for PersistentVolume type nfs')

        ret = merger.merge(copy.deepcopy(super().internal_build(req)), {
            'spec': {
                'nfs': config.nfs
            },
        })
        return ret


class KData_PersistentVolume_CSI(KData_PersistentVolume):
    """
    A :class:`KData` that represents a Kubernetes PersistentVolume of type CSI.

    :param name: Persistent volume name
    :param hostpath: the CSI configuration, normally a Mapping
    :param storageclass: storage class
    :param merge_config: A Mapping to merge on the result.
    """
    clear_storageclass_if_volumehandle: bool

    def __init__(self, clear_storageclass_if_volumehandle: bool = True):
        self.clear_storageclass_if_volumehandle = clear_storageclass_if_volumehandle

    class Config(KData_PersistentVolume_Config):
        csi: Mapping[Any, Any]

        def __init__(self, csi: Mapping[Any, Any], merge_config: Optional[Mapping[Any, Any]] = None):
            super().__init__(merge_config=merge_config)
            self.csi = csi

    def internal_build(self, req: KData_PersistentVolume_Request) -> Mapping[Any, Any]:
        config = req.get_config(KData_PersistentVolume_CSI.Config)
        if not isinstance(config, KData_PersistentVolume_CSI.Config):
            raise InvalidParamError('Could not find configuration for PersistentVolume type CSI')

        ret = merger.merge(copy.deepcopy(super().internal_build(req)), {
            'spec': {
                'csi': config.csi
            },
        })

        if self.clear_storageclass_if_volumehandle and 'volumeHandle' in ret['spec']['csi'] and ret['spec']['csi']['volumeHandle'] != '':
            ret['spec']['storageClassName'] = ''

        return ret

    def build_claim(self, pvc: 'KData_PersistentVolumeClaim', req: 'KData_PersistentVolumeClaim_Request') -> Mapping[Any, Any]:
        ret = dict(super().build_claim(pvc, req))
        if req.pvreq is not None:
            pv = self.build(req.pvreq)
            if self.clear_storageclass_if_volumehandle and 'volumeHandle' in pv['spec']['csi'] and \
                    pv['spec']['csi']['volumeHandle'] != '':
                ret['spec']['storageClassName'] = ''
        return ret


class KData_PersistentVolumeClaim_Request:
    name: str
    namespace: Optional[str]
    pvreq: Optional[KData_PersistentVolume_Request]
    selector_labels: Optional[Mapping[str, Any]]
    storageclassname: Optional[str]
    storage: Optional[str]
    access_modes: Optional[Sequence[str]]
    volume_name: Optional[str]
    merge_config: Optional[Mapping[Any, Any]]

    def __init__(self, name: str, namespace: Optional[str], pvreq: Optional[KData_PersistentVolume_Request] = None,
                 selector_labels: Optional[Mapping[str, Any]] = None,
                 storageclassname: Optional[str] = None, storage: Optional[str] = None,
                 access_modes: Optional[Sequence[str]] = None, volume_name: Optional[str] = None,
                 merge_config: Optional[Mapping[Any, Any]] = None):
        self.name = name
        self.namespace = namespace
        self.pvreq = pvreq
        self.selector_labels = selector_labels
        self.storageclassname = storageclassname
        self.storage = storage
        self.access_modes = access_modes
        self.volume_name = volume_name
        self.merge_config = merge_config


class KData_PersistentVolumeClaim(KData):
    """
    A :class:`KData` that represents a Kubernetes PersistentVolumeClaim.

    :param name: Persistent volume name
    :param storageclass: storage class
    :param namespace: claim namespace
    :param merge_config: A Mapping to merge on the result.
    """
    def internal_build(self, req: KData_PersistentVolumeClaim_Request) -> Mapping[Any, Any]:
        ret: Dict[Any, Any] = {
            'apiVersion': 'v1',
            'kind': 'PersistentVolumeClaim',
            'metadata': {
                'name': req.name,
            },
            'spec': {
            },
        }

        if req.storageclassname is not None:
            ret['spec']['storageClassName'] = req.storageclassname
        elif req.pvreq is not None and req.pvreq.storageclassname is not None:
            ret['spec']['storageClassName'] = req.pvreq.storageclassname

        if req.selector_labels is not None:
            ret['spec']['selector'] = {
                'matchLabels': req.selector_labels,
            }
        elif req.pvreq is not None and req.pvreq.selector_labels is not None:
            ret['spec']['selector'] = {
                'matchLabels': req.pvreq.selector_labels,
            }

        if req.storage is not None:
            ret['spec']['resources'] = {
                'requests': {
                    'storage': req.storage,
                },
            }
        elif req.pvreq is not None and req.pvreq.storage is not None:
            ret['spec']['resources'] = {
                'requests': {
                    'storage': req.pvreq.storage,
                },
            }

        if req.access_modes is not None:
            ret['spec']['accessModes'] = req.access_modes
        elif req.pvreq is not None and req.pvreq.access_modes is not None:
            ret['spec']['accessModes'] = req.pvreq.access_modes

        if req.volume_name is not None:
            ret['spec']['volumeName'] = req.volume_name

        return ret

    def build(self, req: KData_PersistentVolumeClaim_Request) -> Mapping[Any, Any]:
        return merger.merge(copy.deepcopy(self.internal_build(req)), req.merge_config if req.merge_config is not None else {})


class KData_PersistentVolumeClaim_NoSelector(KData_PersistentVolumeClaim):
    """
    A PersistentVolumeClaim that doesn't support selectors.
    """
    def internal_build(self, req: KData_PersistentVolumeClaim_Request) -> Mapping[Any, Any]:
        ret: Dict[Any, Any] = dict(copy.deepcopy(super().internal_build(req)))
        if 'selector' in ret['spec']:
            del ret['spec']['selector']
            if req.volume_name is not None:
                ret['spec']['storageClassName'] = ''
                ret['spec']['volumeName'] = req.volume_name
            elif req.pvreq is not None:
                ret['spec']['storageClassName'] = ''
                ret['spec']['volumeName'] = req.pvreq.name
            else:
                raise InvalidParamError('Cloud not determine volume name')
        return ret
