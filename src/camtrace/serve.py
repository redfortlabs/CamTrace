from __future__ import annotations

import os

import uvicorn

from .app import build_app  # adjust import if needed


def main() -> int:
    # Safer default — override with CAMTRACE_HOST=0.0.0.0 in Docker/LAN
    host = os.getenv("CAMTRACE_HOST", "127.0.0.1")
    port = int(os.getenv("CAMTRACE_PORT", "8000"))

    app = build_app()
    uvicorn.run(app, host=host, port=port)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
