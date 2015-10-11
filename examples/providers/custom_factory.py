"""Custom `di.Factory` example."""

import dependency_injector as di


class User(object):
    """Example class User."""


class UsersFactory(di.Provider):
    """Example users factory."""

    __slots__ = ('_factory',)

    def __init__(self):
        """Initializer."""
        self._factory = di.Factory(User)
        super(UsersFactory, self).__init__()

    def _provide(self, *args, **kwargs):
        """Return provided instance."""
        return self._factory(*args, **kwargs)


# Users factory:
users_factory = UsersFactory()

# Creating several User objects:
user1 = users_factory()
user2 = users_factory()

# Making some asserts:
assert isinstance(user1, User)
assert isinstance(user2, User)
assert user1 is not user2
