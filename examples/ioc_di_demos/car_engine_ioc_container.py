"""Example of inversion of control container for Car & Engine example."""

from dependency_injector import catalogs
from dependency_injector import providers

from car_engine_ioc import Car
from car_engine_ioc import Engine


class Components(catalogs.DeclarativeCatalog):
    """Catalog of component providers."""

    engine = providers.Factory(Engine)

    car = providers.Factory(Car, engine=engine)


if __name__ == '__main__':
    car = Components.car()  # Application creates Car's instance
