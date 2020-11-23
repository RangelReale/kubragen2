import deepmerge  # type: ignore

from ..exception import MergeError, InvalidParamError


def option_check_key_exist(config, path, base, nxt):
    for k, v in nxt.items():
        if k not in base:
            raise InvalidParamError('Unknown option: "{}"'.format('.'.join(path + [k])))
    return deepmerge.STRATEGY_END


def option_type_conflict(config, path, base, nxt):
    if len(path) > 0:
        raise MergeError("Type conflict at '{}': {}, {}".format(
            '.'.join(path), repr(base), repr(nxt)
        ))
    raise MergeError("Type conflict: {}, {}".format(
        repr(base), repr(nxt)
    ))


def option_merge_fallback(config, path, base, nxt):
    if len(path) > 0:
        raise MergeError("Merge fallback at '{}': {}, {}".format(
            '.'.join(path), repr(base), repr(nxt)
        ))
    raise MergeError("Merge fallback: {}, {}".format(
        repr(base), repr(nxt)
    ))
