"""Example of dependency injection in Python.

Alternative injections definition style #2.
"""

import logging
import sqlite3

import boto.s3.connection

import example.main
import example.services

import dependency_injector.containers as containers
import dependency_injector.providers as providers


class Platform(containers.DeclarativeContainer):
    """IoC container of platform service providers."""

    logger = providers.Singleton(logging.Logger)
    logger.add_kwargs(name='example')

    database = providers.Singleton(sqlite3.connect)
    database.add_args(':memory:')

    s3 = providers.Singleton(boto.s3.connection.S3Connection)
    s3.add_kwargs(aws_access_key_id='KEY',
                  aws_secret_access_key='SECRET')


class Services(containers.DeclarativeContainer):
    """IoC container of business service providers."""

    users = providers.Factory(example.services.Users)
    users.add_kwargs(logger=Platform.logger,
                     db=Platform.database)

    auth = providers.Factory(example.services.Auth)
    auth.add_kwargs(logger=Platform.logger,
                    db=Platform.database,
                    token_ttl=3600)

    photos = providers.Factory(example.services.Photos)
    photos.add_kwargs(logger=Platform.logger,
                      db=Platform.database,
                      s3=Platform.s3)


class Application(containers.DeclarativeContainer):
    """IoC container of application component providers."""

    main = providers.Callable(example.main.main)
    main.add_kwargs(users_service=Services.users,
                    auth_service=Services.auth,
                    photos_service=Services.photos)
