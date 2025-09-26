# src/camtrace/scheduler.py APScheduler to trigger the job nightly at 23:59 America/Chicago.

import os
from zoneinfo import ZoneInfo

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from camtrace.report_job import run_daily_report_and_alert


def start_scheduler() -> BackgroundScheduler:
    """
    Starts a background scheduler that runs the daily report at 23:59 America/Chicago.
    Returns the scheduler instance so the caller can keep a reference (and shut it down on exit).
    """
    tz = ZoneInfo(os.getenv("CAMTRACE_TZ", "America/Chicago"))
    sched = BackgroundScheduler(timezone=tz)
    trigger = CronTrigger(hour=23, minute=59)  # 23:59 local time
    sched.add_job(
        run_daily_report_and_alert,
        trigger,
        id="camtrace_daily_report",
        replace_existing=True,
    )
    sched.start()
    print("[scheduler] CamTrace daily report scheduled for 23:59", flush=True)
    return sched
