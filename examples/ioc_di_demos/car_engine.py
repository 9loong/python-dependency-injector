"""Car & Engine example."""


class Engine(object):
    """Example engine."""


class Car(object):
    """Example car."""

    def __init__(self):
        """Initializer."""
        self.engine = Engine()


if __name__ == '__main__':
    car = Car()  # Application creates Car's instance
