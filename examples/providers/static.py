"""`Static` providers example."""

from objects.providers import Class
from objects.providers import Object
from objects.providers import Function
from objects.providers import Value


# Provides class - `object`:
cls_provider = Class(object)
assert cls_provider() is object

# Provides object - `object()`:
object_provider = Object(object())
assert isinstance(object_provider(), object)

# Provides function - `len`:
function_provider = Function(len)
assert function_provider() is len

# Provides value - `123`:
value_provider = Value(123)
assert value_provider() == 123
