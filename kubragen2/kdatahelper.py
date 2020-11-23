from typing import Sequence, Any, Optional, Mapping, List

from .configfile import ConfigFileRender, ConfigFile, ConfigFileRenderMulti
from .data import Data, DisabledData
from .exception import InvalidParamError
from .kdata import KData, KData_Value, KData_ConfigMap, KData_Secret, KData_Manual, KData_Env
from .merger import merger
from .options import Options


class KDataHelper:
    pass


class KDataHelper_ConfigFile(KDataHelper):
    @staticmethod
    def info(value: Any, options: Options, renderers: Sequence[ConfigFileRender]) -> Any:
        if isinstance(value, str):
            return value
        if isinstance(value, ConfigFile):
            configfilerender = ConfigFileRenderMulti(renderers)
            return configfilerender.render(value.get_value(options))
        if isinstance(value, Data):
            return value
        raise InvalidParamError('Invalid parameter for config file: "{}"'.format(repr(value)))


class KDataHelper_Env(KDataHelper):
    """
    KData helpers for Kubernetes *container.env* values.
    """
    @staticmethod
    def info(base_value: Optional[Any] = None, value: Optional[Any] = None,
             default_value: Optional[Any] = None, enabled: bool = True, disable_if_none: bool = False) -> Any:
        """
        Outputs a configuration compatible with the Kubernetes *container.env*.

        If *value* is not a Mapping, it will be considered a simple 'value' field.

        :param base_value: the base dict that is merged with the result, normally containing the name of the object.
        :type base_value: Mapping
        :param value: a value configured by the user, possibly None
        :param value_if_kdata: a :class:`kubragen.kdata.KData` value configured by the user, possibly None. If
            not a KData instance, **it will be ignored**, and you are supposed to set a value in *default_value.
        :param default_value: a default value to use if value is None
        :param enabled: whether the information is enabled. If not, a :class:`kubragen.data.DisabledData` is returned
        :param disable_if_none: automatically disable if value and value_if_kdata is None
        :return: a configuration compatible with the Kubernetes *container.env* specification
        """
        if not enabled:
            return DisabledData()

        ret = base_value
        if ret is None:
            ret = {}

        if isinstance(value, KData_Env):
            ret = {
                'name': value.name,
            }
            value = value.value

        if isinstance(value, KData):
            if isinstance(value, KData_Manual):
                default_value = merger.merge(ret, value.merge_value)
            elif isinstance(value, KData_Value):
                default_value = {
                    'value': value.value,
                }
            elif isinstance(value, KData_ConfigMap):
                default_value = {
                    'valueFrom': {
                        'configMapKeyRef': {
                            'name': value.configmapName,
                            'key': value.configmapData
                        }
                    },
                }
            elif isinstance(value, KData_Secret):
                default_value = {
                    'valueFrom': {
                        'secretKeyRef': {
                            'name': value.secretName,
                            'key': value.secretData
                        }
                    },
                }
            else:
                raise InvalidParamError('Unsupported KData: "{}"'.format(repr(value)))
        elif value is not None:
            if isinstance(value, Mapping):
                default_value = value
            else:
                default_value = {
                    'value': value,
                }

        # Check again
        # if disable_if_none and default_value is None:
        #     return DisabledData()

        return merger.merge(ret, default_value)

    @staticmethod
    def list(value: Optional[Sequence[Any]] = None) -> Sequence[Any]:
        ret: List[Any] = []
        if value is None:
            return ret
        for v in value:
            ret.append(KDataHelper_Env.info(base_value={}, value=v))
        return ret
