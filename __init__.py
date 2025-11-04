# news_backend/__init__.py

"""
This file initializes the news_backend package.

✅ Keep this minimal to prevent circular imports.
Only include modules that do NOT depend on the main app or routers.
"""

from . import database, models, schemas

__all__ = ["database", "models", "schemas"]
