"""Datafile field representations."""
from .util import value_is_empty


class Field:
    """Provides a mapping between a field name and its position."""

    def __init__(self, item, name, type, startIndex, endIndex, required=True, validators=[]):
        self.item = item
        self.name = name
        self.type = type
        self.startIndex = startIndex
        self.endIndex = endIndex
        self.required = required
        self.validators = validators

    def create(self, item, name, length, start, end, type):
        """Create a new field."""
        return Field(item, name, type, length, start, end)

    def __repr__(self):
        """Return a string representation of the field."""
        return f"{self.name}({self.startIndex}-{self.endIndex})"

    def parse_value(self, line):
        """Parse the value for a field given a line, startIndex, endIndex, and field type."""
        value = line[self.startIndex:self.endIndex]

        if value_is_empty(value, self.endIndex-self.startIndex):
            return None

        match self.type:
            case 'number':
                try:
                    value = int(value)
                    return value
                except ValueError:
                    return None
            case 'string':
                return value


def is_encrypted(value, decryption_dict):
    """Determine if value is encrypted."""
    return len([x for x in value if x in decryption_dict]) == 9

def tanf_ssn_decryption_func(value):
    """Decrypt TANF SSN value."""
    decryption_dict = {"@": "1", "9": "2", "Z": "3", "P": "4", "0": "5",
                       "#": "6", "Y": "7", "B": "8", "W": "9", "T": "0"}
    decryption_table = str.maketrans(decryption_dict)

    if is_encrypted(value, decryption_dict):
        return value.translate(decryption_table)
    return value

def ssp_ssn_decryption_func(value):
    """Decrypt SSP SSN value."""
    decryption_dict = {"@": "1", "9": "2", "Z": "3", "P": "4", "0": "5",
                       "#": "6", "Y": "7", "B": "8", "W": "9", "T": "0"}
    decryption_table = str.maketrans(decryption_dict)

    if is_encrypted(value, decryption_dict):
        return value.translate(decryption_table)
    return value


class EncryptedField(Field):
    """Represents an encrypted field and its position."""

    def __init__(self, decryption_func, item, name, type, startIndex, endIndex, required=True, validators=[]):
        super().__init__(item, name, type, startIndex, endIndex, required, validators)
        self.decryption_func = decryption_func

    def parse_value(self, line):
        """Parse and decrypt the value for a field given a line, startIndex, endIndex, and field type."""
        value = line[self.startIndex:self.endIndex]

        if value_is_empty(value, self.endIndex-self.startIndex):
            return None

        match self.type:
            case 'string':
                return self.decryption_func(value)
            case _:
                return None
