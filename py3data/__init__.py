try:
    from py3data._version import __version__
    from py3data._version import __version_tuple__
except ImportError:
    __version__ = "0.0.0"
    __version_tuple__ = (0, 0, 0)

from py3data.api import Repositories
from py3data.api import Repository
from py3data.api import config

__all__ = ["Repository", "Repositories", "config"]
