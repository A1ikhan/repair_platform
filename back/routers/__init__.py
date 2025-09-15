# api/routers/__init__.py
from .auth import auth_router
from .repairs import repair_router

__all__ = ['auth_router', 'repair_router']