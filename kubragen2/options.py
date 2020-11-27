from typing import Mapping, Any, Optional, Sequence, Union, MutableMapping, MutableSequence

from .build import DataBuilder
from .exception import InvalidParamError
from .option import OptionValue, Option
from .private.merger import option_merge_fallback, option_type_conflict
from .private.optionsmerger import OptionsMerger
from .util import dict_get_value, dict_has_name


class Options:
    """
    Helper used to extract options from a list of merged Mapping.
    Uses dotted property format for easy access.

    :param options: list of Mapping to merge in order.
    """
    options: Mapping[Any, Any]

    def __init__(self, *options: Optional[Mapping[Any, Any]]):
        self.options = {}
        for option in options:
            if option is not None:
                self.options = optionsmerger.merge(self.options, option)

    def has_option(self, name: str) -> Any:
        """
        Checks if the dotted-name option exists.
        """
        return dict_has_name(self.options, name)

    def option_get(self, name: str) -> Any:
        """
        Gets the dotted-name option value.
        """
        return self._option_process(dict_get_value(self.options, name))

    def option_get_opt(self, name: str, default_value: Any) -> Any:
        """
        Gets the dotted-name option value, using a default if not set or `None` or blank string.
        """
        return self.option_get_opt_custom(name, default_value, [None, ''])

    def option_get_opt_custom(self, name: str, default_value: Any, empty_values: Sequence[Any]) -> Any:
        """
        Gets the dotted-name option value, using a default, and allowing customizing the values that
        are considered empty.
        """
        if not self.has_option(name):
            return default_value
        value = self.option_get(name)
        if value in empty_values:
            return default_value
        return value

    def _option_process(self, value: Any) -> Any:
        """
        Process custom :class:`Option` types.
        """
        if isinstance(value, Option):
            if isinstance(value, OptionValue):
                return value.process_value(self.option_get(value.name))
            else:
                raise InvalidParamError('Unknown Optiona type: "{}"'.format(repr(value)))
        return value


class OptionsDataBuilder(DataBuilder):
    """
    A :class:`DataBuilder` that takes in account :class:`Option` instances.
    """
    options: Options

    def __init__(self, options: Options):
        super().__init__()
        self.options = options

    def build_prop(self, data: Union[MutableMapping, MutableSequence], key: Any) -> None:
        super().build_prop(data, key)
        if key in data and isinstance(data[key], Option):
            data[key] = self.options._option_process(data[key])

    def get_value(self, data: Any) -> Any:
        return self.options._option_process(super().get_value(data))


def OptionsBuildData(options: Options, data: Any, in_place: bool = True) -> Any:
    """
    Build data taking in account :class:`Option` instances.
    """
    return OptionsDataBuilder(options).build(data, in_place=in_place)


optionsmerger = OptionsMerger(
    [
        (list, "append"),
        (dict, "merge"),
    ],
    ['override', option_merge_fallback], ['override', option_type_conflict]
)
"""A dict/list merger that supports options."""
