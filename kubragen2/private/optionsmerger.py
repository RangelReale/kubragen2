import deepmerge  # type: ignore

from ..option import Option


class OptionsMerger(deepmerge.Merger):
    def value_strategy(self, path, base, nxt):
        if isinstance(base, Option):
            return nxt
        return super().value_strategy(path, base, nxt)
