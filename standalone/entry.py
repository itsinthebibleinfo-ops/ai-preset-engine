"""Standalone entry point for the AI Sound Design Engine.

Used by PyInstaller to create a self-contained executable.
Starts uvicorn programmatically serving the FastAPI application.
"""

import uvicorn

from engine.server import app  # noqa: F401  (import triggers path setup)


def main():
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        log_level="info",
    )


if __name__ == "__main__":
    main()
