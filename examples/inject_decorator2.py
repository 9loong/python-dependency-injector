"""`@inject` decorator example."""

from objects.providers import NewInstance
from objects.injections import KwArg
from objects.decorators import inject


new_object = NewInstance(object)


@inject(KwArg('object_a', new_object))
@inject(KwArg('some_setting', 1334))
def example_callback(object_a, some_setting):
    """This function has dependencies on object a and b.

    Dependencies are injected using `@inject` decorator.
    """
    assert isinstance(object_a, object)
    assert some_setting == 1334


example_callback()
example_callback()
