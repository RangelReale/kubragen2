class KG2Exception(Exception):
    pass


class InvalidOperationError(KG2Exception):
    pass


class InvalidParamError(KG2Exception):
    pass


class NotFoundError(KG2Exception):
    pass


class NotSupportedError(KG2Exception):
    pass


class InvalidNameError(KG2Exception):
    pass


class TypeError(KG2Exception):
    pass


class MergeError(KG2Exception):
    pass


class InvalidJsonPatchError(KG2Exception):
    pass


class ConfigFileError(KG2Exception):
    pass
