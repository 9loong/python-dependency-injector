"""`di.Factory` providers example."""

import dependency_injector as di


class User(object):
    """Example class User."""

# Factory provider creates new instance of specified class on every call.
users_factory = di.Factory(User)

# Creating several User objects:
user1 = users_factory()
user2 = users_factory()

# Making some asserts:
assert user1 is not user2
assert isinstance(user1, User) and isinstance(user2, User)
