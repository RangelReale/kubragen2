import deepmerge  # type: ignore

from ..option import Option
from .merger import option_merge_fallback, option_type_conflict


class OptionsMerger(deepmerge.Merger):
    def value_strategy(self, path, base, nxt):
        if isinstance(base, Option):
            return nxt
        return super().value_strategy(path, base, nxt)


optionsmerger = OptionsMerger(
    [
        (list, "append"),
        (dict, "merge"),
    ],
    ['override', option_merge_fallback], [option_type_conflict]
)
"""A dict/list merger that supports options."""
