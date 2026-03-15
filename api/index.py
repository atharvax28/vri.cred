"""Vercel serverless function entry point for FastAPI application."""

import sys
from pathlib import Path

# Add the demo/backend to the Python path
backend_path = Path(__file__).parent.parent / "demo" / "backend"
if str(backend_path) not in sys.path:
    sys.path.insert(0, str(backend_path))

try:
    from src.main import app as fastapi_app
    # Export the ASGI app for Vercel
    app = fastapi_app
except Exception as e:
    # Fallback error handler if FastAPI fails to import
    from fastapi import FastAPI
    app = FastAPI()
    
    @app.get("/health")
    async def health():
        return {"status": "error", "detail": str(e)}

__all__ = ["app"]
