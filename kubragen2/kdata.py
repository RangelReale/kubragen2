from typing import Optional, Mapping, Any

from .data import Data
from .exception import InvalidOperationError


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
