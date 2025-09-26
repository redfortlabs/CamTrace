# src/camtrace/report_job.py
"""
Production daily report + email alert wiring.

Assumes there is a report generator function named
`generate_markdown_report()` that returns:
    (report_path: pathlib.Path, total_violations: int, by_device: dict[str, int])

If your function lives under a different module or name, update the import
in the TRY block below.
"""

from pathlib import Path

# ✅ Import your existing report generator (adjust the import if your path differs)
try:
    # Most likely location
    from camtrace.reporting import generate_markdown_report
except ImportError:
    # Common alternates — uncomment / adjust if needed
    # from camtrace.reports import generate_markdown_report
    # from camtrace.report import generate_markdown_report
    raise  # Could not find your generator; fix the import above.

from camtrace.alert_email import send_email


def run_daily_report_and_alert() -> Path:
    """
    Runs the real daily report generator. If violations > 0, emails the FULL Markdown report.
    Returns the path to the generated Markdown file.
    """
    report_path, total_violations, by_device = _run_generator()

    if total_violations > 0:
        subject = f"CamTrace Daily Report — {total_violations} violation(s)"
        body_text = _read_md(report_path)
        try:
            send_email(subject, body_text)
        except Exception as e:
            # Do not crash the scheduler if email fails
            print(f"[email] failed to send: {e}")

    return report_path


# ------------------------- helpers -------------------------


def _run_generator() -> tuple[Path, int, dict[str, int]]:
    """Thin wrapper to call your generator and validate its return signature."""
    result = generate_markdown_report()
    if not isinstance(result, tuple) or len(result) != 3:
        raise RuntimeError(
            "generate_markdown_report() must return (Path, int, dict[str,int]). "
            "Update your report generator to return: (report_path, total_violations, by_device)"
        )

    report_path, total_violations, by_device = result

    if not isinstance(report_path, Path):
        raise TypeError("report_path must be a pathlib.Path")
    if not isinstance(total_violations, int):
        raise TypeError("total_violations must be an int")
    if not isinstance(by_device, dict):
        raise TypeError("by_device must be a dict[str, int]")

    return report_path, total_violations, by_device


def _read_md(path: Path) -> str:
    return path.read_text(encoding="utf-8")
