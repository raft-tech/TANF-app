def header_row(description, length, start, end, validators=[], item_number=None):
    return {
        'item_number': item_number,
        'description': description,
        'length': length,
        'start': start,
        'end': end,
        'validator': validators
    }

def construct_header_schema():
    header_schema = [
        header_row('Title', 6, 1, 6),
        header_row('Calaender Quarter', 5, 7, 11),
        header_row('Data Type', 1, 12, 12),
        header_row('State FIPS Code', 2, 13, 14, item_number=1),
        header_row('Tribe Code', 3, 15, 17),
        header_row('Program Type', 3, 18, 20),
        header_row('Edit Indicator', 1, 21, 21),
        header_row('Encryption Indicator', 1, 22, 22),
        header_row('Update Indicator', 1, 23, 23),
    ]

    return header_schema

def construct_trailer_schema():
    trailer_schema = [
        header_row('Title', 7, 1, 7),
        header_row('Number of Records', 7, 8, 14),
        header_row('Blank', 9, 15, 23),
    ]

    return trailer_schema
