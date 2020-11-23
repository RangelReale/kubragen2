from typing import Optional, Mapping, Any

from .data import Data
from .exception import InvalidOperationError
from .merger import merger


class KData(Data):
    def is_enabled(self) -> bool:
        return True

    def get_value(self) -> Any:
        raise InvalidOperationError('Cannot get value of KData')


class KData_Manual(KData):
    """
    A :class:`KData` that merges value manually.

    :param merge_value: A Mapping to merge on the result.
    """
    merge_value: Optional[Mapping[Any, Any]]

    def __init__(self, merge_value: Optional[Mapping[Any, Any]] = None):
        self.merge_value = merge_value


class KData_Value(KData):
    """
    A :class:`KData` with a constant value.

    :param value: the data value
    """
    value: str

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
    name: str
    value: Any

    def __init__(self, name: str, value: Any):
        self.name = name
        self.value = value


class KData_StorageClass(KData):
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


class KData_PersistentVolume(KData):
    name: str
    merge_config: Optional[Any]

    def __init__(self, name: str, merge_config: Optional[Any] = None):
        self.name = name
        self.merge_config = merge_config

    def get_value(self) -> Any:
        return merger.merge(self.build(), self.merge_config if self.merge_config is not None else {})

    def build(self) -> Any:
        return {
            'apiVersion': 'v1',
            'kind': 'PersistentVolume',
            'metadata': {
                'name': self.name,
            },
            'spec': {
            },
        }


class KData_PersistentVolume_EmptyDir(KData_PersistentVolume):
    def build(self) -> Any:
        return merger.merge(super().build(), {
            'spec': {
                'emptyDir': {}
            },
        })


class KData_PersistentVolume_HostPath(KData_PersistentVolume):
    hostpath: str

    def __init__(self, name: str, hostpath: str, merge_config: Optional[Any] = None):
        super().__init__(name=name, merge_config=merge_config)
        self.hostpath = hostpath

    def build(self) -> Any:
        return merger.merge(super().build(), {
            'spec': {
                'hostPath': self.hostpath
            },
        })


class KData_PersistentVolume_NFS(KData_PersistentVolume):
    nfs: Any

    def __init__(self, name: str, nfs: Any, merge_config: Optional[Any] = None):
        super().__init__(name=name, merge_config=merge_config)
        self.nfs = nfs

    def build(self) -> Any:
        return merger.merge(super().build(), {
            'spec': {
                'nfs': self.nfs
            },
        })


class KData_PersistentVolume_CSI(KData_PersistentVolume):
    csi: Any

    def __init__(self, name: str, csi: Any, merge_config: Optional[Any] = None):
        super().__init__(name=name, merge_config=merge_config)
        self.csi = csi

    def build(self) -> Any:
        return merger.merge(super().build(), {
            'spec': {
                'csi': self.csi
            },
        })


class KData_PersistentVolumeClaim(KData):
    name: str
    merge_config: Optional[Any]

    def __init__(self, name: str, merge_config: Optional[Any] = None):
        self.name = name
        self.merge_config = merge_config

    def get_value(self) -> Any:
        return merger.merge(self.build(), self.merge_config if self.merge_config is not None else {})

    def build(self) -> Any:
        return {
            'apiVersion': 'v1',
            'kind': 'PersistentVolumeClaim',
            'metadata': {
                'name': self.name,
            },
            'spec': {
            },
        }
