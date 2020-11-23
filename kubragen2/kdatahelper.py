from typing import Sequence, Any

from .configfile import ConfigFileRender, ConfigFile, ConfigFileRenderMulti
from .data import Data
from .exception import InvalidParamError
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
