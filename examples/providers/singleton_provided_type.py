"""`Singleton` specialization for limitation to provided type example."""

import dependency_injector.providers as providers
import dependency_injector.errors as errors


class BaseService:
    """Base service class."""


class UsersService(BaseService):
    """Users service."""


class PhotosService(BaseService):
    """Photos service."""


class ServiceProvider(providers.Singleton):
    """Service provider."""

    provided_type = BaseService


# Creating several service providers with BaseService instances:
users_service_provider = ServiceProvider(UsersService)
photos_service_provider = ServiceProvider(PhotosService)

# Trying to create service provider with not a BaseService instance:
try:
    some_service_provider = ServiceProvider(object)
except errors.Error as exception:
    print(exception)
    # <class '__main__.ServiceProvider'> can provide only
    # <class '__main__.BaseService'> instances
