from typing import Any

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
    def __init__(self, value: Any = None, enabled: bool = True, disabled_if_none: bool = False):
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
