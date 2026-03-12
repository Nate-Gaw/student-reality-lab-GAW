"""
__init__.py for data.storage package
"""
from .database import DatabaseManager, University, Base

__all__ = [
    'DatabaseManager',
    'University',
    'Base'
]
