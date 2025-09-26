# src/camtrace/app.py module that defines FastAPI(app); CLI points to it.

import os

from fastapi import FastAPI

from camtrace.scheduler import (
    start_scheduler,
)  # we'll add serve.py next; this just hooks the scheduler

app = FastAPI(title="CamTrace")

# (Optional) auto-include your API router if it exists; if not, it's safely skipped.
try:
    # If you already have a FastAPI router somewhere (e.g., camtrace.api:router), include it here.
    from camtrace.api import (
        router as api_router,
    )  # adjust if your router lives elsewhere

    app.include_router(api_router)
    print("[app] API router included.")
except Exception as e:
    print(f"[app] No API router included (ok for now): {e}")

_scheduler_ref = None


@app.on_event("startup")
def _startup():
    """Start background scheduler if enabled via env."""
    global _scheduler_ref
    if os.getenv("CAMTRACE_SCHEDULER", "0") == "1":
        _scheduler_ref = start_scheduler()


@app.on_event("shutdown")
def _shutdown():
    """Shut down scheduler cleanly."""
    global _scheduler_ref
    if _scheduler_ref is not None:
        _scheduler_ref.shutdown(wait=False)
        _scheduler_ref = None
