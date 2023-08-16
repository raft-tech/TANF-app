"""Datafile field representations."""

def value_is_empty(value, length):
    """Handle 'empty' values as field inputs."""
    empty_values = [
        ' '*length,  # '     '
        '#'*length,  # '#####'
    ]

    return value is None or value in empty_values


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

class TransformField(Field):
    """Represents a field that requires some transformation before serializing."""

    def __init__(self, transform_func, item, name, type, startIndex, endIndex, required=True, validators=[], **kwargs):
        super().__init__(item, name, type, startIndex, endIndex, required, validators)
        self.transform_func = transform_func
        self.__dict__.update(kwargs)

    def parse_value(self, line):
        """Parse and transform the value for a field given a line, startIndex, endIndex, and field type."""
        value = line[self.startIndex:self.endIndex]

        if value_is_empty(value, self.endIndex-self.startIndex):
            return None

        value = self.transform_func(value, **self.__dict__)
        match self.type:
            case 'string':
                return value
            case 'number':
                try:
                    value = int(value)
                    return value
                except ValueError:
                    return None
            case _:
                return None
