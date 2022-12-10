from importlib.metadata import version

from .client import FoxOpsClient

__version__ = version("foxops_client")

__all__ = ["FoxOpsClient"]
