class IllegalCharacterException(Exception):
    def __init__(self, message=""):
        self.message = message


class InvalidPattern(Exception):
    def __init__(self, message=""):
        self.message = message


class MissingExpectedArgument(Exception):
    def __init__(self, message=""):
        self.message = message


class NoCommandsFound(Exception):
    def __init__(self, message=""):
        self.message = message


class UnrecognizedCommandException(Exception):
    def __init__(self, message=""):
        self.message = message
