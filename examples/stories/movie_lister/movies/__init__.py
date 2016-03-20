"""Movies package.

Top-level package of movies library. This package contains catalog of movies
module components - ``MoviesModule``. It is recommended to use movies library
functionality by fetching required instances from ``MoviesModule`` providers.

Each of ``MoviesModule`` providers could be overridden.
"""

from . import finders
from . import listers
from . import models

from dependency_injector import catalogs
from dependency_injector import providers


class MoviesModule(catalogs.DeclarativeCatalog):
    """Catalog of movies module components."""

    movie_model = providers.DelegatedFactory(models.Movie)
    """:type: providers.Provider -> models.Movie"""

    movie_finder = providers.Factory(finders.MovieFinder,
                                     movie_model=movie_model)
    """:type: providers.Provider -> finders.MovieFinder"""

    movie_lister = providers.Factory(listers.MovieLister,
                                     movie_finder=movie_finder)
    """:type: providers.Provider -> listers.MovieLister"""
