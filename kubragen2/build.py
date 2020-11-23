import copy
from typing import Any, MutableMapping, MutableSequence, Union

from .exception import InvalidParamError


class Data:
    """
    Base class to represent data that can be disabled by a flag.
    The :func:`get_value` function allows for dynamic code generation if needed.
    """
    def is_enabled(self) -> bool:
        """
        Whether the data is enabled. If not, it will be removed by :func:`BuildData`.
        """
        raise NotImplementedError()

    def get_value(self) -> Any:
        """
        Returns the value of the data.

        :return: the data value
        """
        raise NotImplementedError()


class DisabledData(Data):
    """A :class:`Data` class that is always disabled."""
    def is_enabled(self) -> bool:
        return False

    def get_value(self) -> Any:
        return None


class ValueData(Data):
    """
    A :class:`Data` class with constant values.

    :param value: the value to return in :func:`get_value`
    :param enabled: whether the data is enabled
    :param disabled_if_none: set enabled=False if value is None
    """
    def __init__(self, value = None, enabled: bool = True, disabled_if_none: bool = False):
        self.value = value
        self.enabled = enabled
        if disabled_if_none and value is None:
            self.enabled = False

    def is_enabled(self) -> bool:
        return self.enabled

    def get_value(self) -> Any:
        return self.value


class ValueConfiguration:
    """
    Value configuration
    """
    value_path: str

    def __init__(self, value_path: str):
        self.value_path = value_path


def DataIsNone(value: Any) -> bool:
    """
    Checks if the value is None.
    If value is an instance of :class:`Data`, check its *is_enabled()* method.

    :param value: the value to check for None
    :return: whether the value is None or disabled
    """
    if isinstance(value, Data):
        if not value.is_enabled():
            return True
        return DataIsNone(value.get_value())
    return value is None


def DataGetValue(value: Any, raise_if_disabled: bool = False) -> Any:
    """
    Returns the value.
    If value is an instance of :class:`Data`, call its get_value() method, or return None if
    not enabled.

    :param value: the value to check
    :param raise_if_disabled: whether to raise an exception if the value is disabled.
    :return: the value
    :raises InvalidParamError: if value is disabled
    """
    if isinstance(value, Data):
        if not value.is_enabled():
            if raise_if_disabled:
                raise InvalidParamError('Value is disabled')
            return None
        return DataGetValue(value.get_value())
    return value


class DataBuilder:
    def build_prop(self, data: Union[MutableMapping, MutableSequence], key: Any) -> None:
        """
        Cleanup instances of Data class in Mapping or Sequence.
        """
        if isinstance(data[key], Data):
            if not data[key].is_enabled():
                del data[key]
            else:
                data[key] = data[key].get_value()

    def build(self, data: Any, in_place: bool = True) -> Any:
        """
        Cleanup all instances of Data classes, removing if not enabled or replacing by its value.

        :param data: the data to mutate
        :param in_place: whether to modify the data in-place. If False, data will be duplicated
            using copy.deepcopy
        :return: the same value passed, mutated, except if it is *Data{enabled=False}*, in this case it returns None.
        """
        if not in_place:
            data = copy.deepcopy(data)
        if isinstance(data, MutableMapping):
            keylist = list(data.keys())
            for key in keylist:
                self.build_prop(data, key)
            for item in data.values():
                self.build(item)
            return data
        elif isinstance(data, MutableSequence):
            for key in range(len(data) - 1, -1, -1):
                self.build_prop(data, key)
            for item in data:
                self.build(item)
            return data
        return self.get_value(data)

    def get_value(self, data: Any) -> Any:
        return DataGetValue(data)


# def BuildDataProp(data: Union[MutableMapping, MutableSequence], key: Any) -> None:
#     """
#     Cleanup instances of Data class in Mapping or Sequence.
#     """
#     if isinstance(data[key], Data):
#         if not data[key].is_enabled():
#             del data[key]
#         else:
#             data[key] = data[key].get_value()


def BuildData(data: Any, in_place: bool = True) -> Any:
    """
    Cleanup all instances of Data classes, removing if not enabled or replacing by its value.

    :param data: the data to mutate
    :param in_place: whether to modify the data in-place. If False, data will be duplicated
        using copy.deepcopy
    :return: the same value passed, mutated, except if it is *Data{enabled=False}*, in this case it returns None.
    """
    return DataBuilder().build(data, in_place=in_place)

    # if not in_place:
    #     data = copy.deepcopy(data)
    # if isinstance(data, MutableMapping):
    #     keylist = list(data.keys())
    #     for key in keylist:
    #         BuildDataProp(data, key)
    #     for item in data.values():
    #         BuildData(item)
    # elif isinstance(data, MutableSequence):
    #     for key in range(len(data) - 1, -1, -1):
    #         BuildDataProp(data, key)
    #     for item in data:
    #         BuildData(item)
    # return DataGetValue(data)
