"""Vercel serverless function entry point for FastAPI application."""

import sys
from pathlib import Path

# Add the demo/backend to the Python path
backend_path = Path(__file__).parent.parent / "demo" / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

from src.main import app

# Export the ASGI app for Vercel
__all__ = ["app"]
