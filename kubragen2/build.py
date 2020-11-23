import copy
from typing import Any, MutableMapping, MutableSequence, Union

from .data import DataGetValue, Data


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


def BuildData(data: Any, in_place: bool = True) -> Any:
    """
    Cleanup all instances of Data classes, removing if not enabled or replacing by its value.

    :param data: the data to mutate
    :param in_place: whether to modify the data in-place. If False, data will be duplicated
        using copy.deepcopy
    :return: the same value passed, mutated, except if it is *Data{enabled=False}*, in this case it returns None.
    """
    return DataBuilder().build(data, in_place=in_place)
