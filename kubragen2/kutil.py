import base64
import re
from typing import Union

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


def secret_data_encode(data: Union[bytes, str]) -> str:
    """
    Encode bytes or str secret using the current provider.
    By default encoding is done using base64, using the utf-8 charset.

    :param data: Data to encode
    :return: encoded secret
    :raises: KGException
    """
    if isinstance(data, str):
        data = data.encode('utf-8')
    return secret_data_encode_bytes(data).decode("utf-8")


def secret_data_encode_bytes(data: bytes) -> bytes:
    """
    Encode bytes secret using the current provider.
    By default encoding is done using base64, and raw bytes are returned

    :param data: Data to encode
    :return: encoded secret
    :raises: KGException
    """
    return base64.b64encode(data)
