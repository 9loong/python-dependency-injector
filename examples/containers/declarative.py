"""Declarative IoC container simple example."""

from dependency_injector import containers
from dependency_injector import providers


# Defining declarative IoC container:
class Container(containers.DeclarativeContainer):
    """Example IoC container."""

    factory1 = providers.Factory(object)

    factory2 = providers.Factory(object)

# Creating some objects:
object1 = Container.factory1()
object2 = Container.factory2()

# Making some asserts:
assert object1 is not object2
assert isinstance(object1, object)
assert isinstance(object2, object)
