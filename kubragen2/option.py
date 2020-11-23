class Option:
    pass


class OptionValue(Option):
    name: str

    def __init__(self, name: str):
        self.name = name
