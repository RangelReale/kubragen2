from typing import Optional, Any


class Option:
    pass


class OptionValue(Option):
    name: str
    wrap_type: Optional[Any]

    def __init__(self, name: str, wrap_type: Optional[Any] = None):
        self.name = name
        self.wrap_type = wrap_type

    def process_value(self, value: Any) -> Any:
        if self.wrap_type is not None:
            return self.wrap_type(value)
        return value
