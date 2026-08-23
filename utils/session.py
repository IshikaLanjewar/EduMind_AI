"""Backward-compatible import wrapper for the root session module."""
from session import init_session

__all__ = ["init_session"]
