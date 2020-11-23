import re

from kubragen2.exception import InvalidParamError


def unit_to_bytes(value: str) -> int:
    m = re.match('^([0-9]+)(.*)$', value)
    if m is None:
        raise InvalidParamError('Value is not a bytes unit')
    xvalue = int(m.group(1))
    xunit = m.group(2)
    if xunit == "Ki":
        xvalue *= 1024
    elif xunit == "Mi":
        xvalue *= 1024 * 1024
    elif xunit == "Gi":
        xvalue *= 1024 * 1024 * 1024
    elif xunit == "Ti":
        xvalue *= 1024 * 1024 * 1024 * 1024
    elif xunit == "Pi":
        xvalue *= 1024 * 1024 * 1024 * 1024 * 1024
    elif xunit == "Ei":
        xvalue *= 1024 * 1024 * 1024 * 1024 * 1024 * 1024
    elif xunit == "K":
        xvalue *= 1000
    elif xunit == "M":
        xvalue *= 1000 * 1000
    elif xunit == "G":
        xvalue *= 1000 * 1000 * 1000
    elif xunit == "T":
        xvalue *= 1000 * 1000 * 1000 * 1000
    elif xunit == "P":
        xvalue *= 1000 * 1000 * 1000 * 1000 * 1000
    elif xunit == "E":
        xvalue *= 1000 * 1000 * 1000 * 1000 * 1000 * 1000
    else:
        raise InvalidParamError('Unknown byte unit "{}"'.format(xunit))
    return xvalue
