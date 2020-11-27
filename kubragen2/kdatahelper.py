from typing import Sequence, Any, Optional, Mapping, List, Dict

from .configfile import ConfigFileRender, ConfigFile, ConfigFileRenderMulti
from .data import Data, DisabledData
from .exception import InvalidParamError
from .kdata import KData, KData_Value, KData_ConfigMap, KData_Secret, KData_Manual, KData_Env
from .merger import merger
from .options import Options


class KDataHelper:
    pass


class KDataHelper_ConfigFile(KDataHelper):
    """
    Outputs a configuration file using :class:`ConfigFile` if possible, otherwise just output a string.

    :param value: the value configured by the user, possible a :class:`ConfigFile`
    :param options: options to be used by the config file
    :param renderers: a list of config file renderers to be considered, in order
    :return: a configuration file content as string
    """
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
    KData helpers for Kubernetes `container.env` values.
    """
    @staticmethod
    def info(base_value: Optional[Any] = None, value: Optional[Any] = None, enabled: bool = True,
             disable_if_none: bool = False) -> Any:
        """
        Outputs a configuration compatible with the Kubernetes *container.env*.

        If *value* is not a Mapping, it will be considered a simple 'value' field.

        :param base_value: the base dict that is merged with the result, normally containing the name of the object.
        :type base_value: Mapping
        :param value: a value configured by the user, possibly None
        :param enabled: whether the information is enabled. If not, a :class:`kubragen.data.DisabledData` is returned
        :param disable_if_none: automatically disable if value and value_if_kdata is None
        :return: a configuration compatible with the Kubernetes *container.env* specification
        """
        if not enabled or (disable_if_none and value is None):
            return DisabledData()

        ret = base_value
        if ret is None:
            ret = {}

        if isinstance(value, KData_Env):
            ret = {
                'name': value.name,
            }
            value = value.value

        merge_config: Mapping[Any, Any] = {}
        if isinstance(value, KData):
            if isinstance(value, KData_Manual):
                merge_config = value.merge_config
            elif isinstance(value, KData_Value):
                merge_config = {
                    'value': value.value,
                }
            elif isinstance(value, KData_ConfigMap):
                merge_config = {
                    'valueFrom': {
                        'configMapKeyRef': {
                            'name': value.configmapName,
                            'key': value.configmapData
                        }
                    },
                }
            elif isinstance(value, KData_Secret):
                merge_config = {
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
            if isinstance(value, Mapping) and not isinstance(value, str):
                merge_config = value
            else:
                merge_config = {
                    'value': value,
                }

        return merger.merge(ret, merge_config)

    @staticmethod
    def list(value: Optional[Sequence[Any]] = None) -> Sequence[Any]:
        ret: List[Any] = []
        if value is None:
            return ret
        for v in value:
            ret.append(KDataHelper_Env.info(base_value={}, value=v))
        return ret


class KDataHelper_Volume(KDataHelper):
    """
    KData helpers for Kubernetes `podSpec.volumes` values.
    """
    @staticmethod
    def info(base_value: Optional[Any] = None, value: Optional[Any] = None,
             key_path: Optional[str] = None, enabled: bool = True,
             disable_if_none: bool = False):
        """
        Outputs a configuration compatible with the Kubernetes *podSpec.volume*.

        :param base_value: the base dict that is merged with the result, normally containing the name of the object.
        :type base_value: dict
        :param value: a value configured by the user, possibly None
        :param enabled: whether the information is enabled. If not, a :class:`kubragen.data.DisabledData` is returned
        :param disable_if_none: automatically disable if value and value_if_kdata is None
        :return: a configuration compatible with the Kubernetes *podSpec.volume* specification
        """
        if not enabled or (disable_if_none and value is None):
            return DisabledData()

        ret = base_value
        if ret is None:
            ret = {}

        merge_config: Mapping[Any, Any] = {}
        if isinstance(value, KData):
            if isinstance(value, KData_Manual):
                merge_config = value.merge_config
            elif isinstance(value, KData_Value):
                merge_config = value.value
            elif isinstance(value, KData_ConfigMap):
                merge_config = {
                    'configMap': {
                        'name': value.configmapName,
                        'items': [{
                            'key': value.configmapData,
                            'path': value.configmapData if key_path is None else key_path,
                        }],
                    }
                }
            elif isinstance(value, KData_Secret):
                merge_config = {
                    'secret': {
                        'secretName': value.secretName,
                        'items': [{
                            'key': value.secretData,
                            'path': value.secretData if key_path is None else key_path,
                        }],
                    }
                }
            else:
                raise InvalidParamError('Unsupported KData: "{}"'.format(repr(value)))
        elif value is not None:
            if isinstance(value, Mapping) and not isinstance(value, str):
                merge_config = value
            else:
                raise InvalidParamError('Unsupported Volume spec: "{}"'.format(str(value)))

        return merger.merge(ret, merge_config)
