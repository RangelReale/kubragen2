class KG2Exception(Exception):
    pass


class InvalidOperationError(KG2Exception):
    pass


class InvalidParamError(KG2Exception):
    pass


class NotSupportedError(KG2Exception):
    pass


class MergeError(KG2Exception):
    pass


class ConfigFileError(KG2Exception):
    pass
