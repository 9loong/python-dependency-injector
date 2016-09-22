"""A naive example of dependency injection on Python.

Example implementation of dependency injection in Python from Martin Fowler's
article about dependency injection and inversion of control:

http://www.martinfowler.com/articles/injection.html

This mini application uses ``movies`` library, that is configured to work with
sqlite movies database and csv file movies database.
"""

import sqlite3

import movies
import movies.finders

import example.db
import example.main

import settings

import dependency_injector.containers as containers
import dependency_injector.providers as providers


class ResourcesModule(containers.DeclarativeContainer):
    """IoC container of application resource providers."""

    database = providers.Singleton(sqlite3.connect, settings.MOVIES_DB_PATH)


@containers.copy(movies.MoviesModule)
class DbMoviesModule(movies.MoviesModule):
    """IoC container for overriding movies module component providers."""

    movie_finder = providers.Factory(movies.finders.SqliteMovieFinder,
                                     database=ResourcesModule.database,
                                     **movies.MoviesModule.movie_finder.kwargs)


@containers.copy(movies.MoviesModule)
class CsvMoviesModule(movies.MoviesModule):
    """IoC container for overriding movies module component providers."""

    movie_finder = providers.Factory(movies.finders.CsvMovieFinder,
                                     csv_file_path=settings.MOVIES_CSV_PATH,
                                     delimiter=',',
                                     **movies.MoviesModule.movie_finder.kwargs)


class DbApplication(containers.DeclarativeContainer):
    """IoC container of database application component providers."""

    main = providers.Callable(example.main.main,
                              movie_lister=DbMoviesModule.movie_lister)

    init_db = providers.Callable(example.db.init_sqlite,
                                 movies_data=settings.MOVIES_SAMPLE_DATA,
                                 database=ResourcesModule.database)


class CsvApplication(containers.DeclarativeContainer):
    """IoC container of csv application component providers."""

    main = providers.Callable(example.main.main,
                              movie_lister=CsvMoviesModule.movie_lister)

    init_db = providers.Callable(example.db.init_csv,
                                 movies_data=settings.MOVIES_SAMPLE_DATA,
                                 csv_file_path=settings.MOVIES_CSV_PATH,
                                 delimiter=',')

if __name__ == '__main__':
    DbApplication.init_db()
    DbApplication.main()

    CsvApplication.init_db()
    CsvApplication.main()
