
class Field:
    name="name"
    friendly_name="friendly_name"

field = Field()
fields  = [field]

x = {getattr(f, 'name', ''): getattr(f, 'friendly_name', '') for f in fields}
print(x)
