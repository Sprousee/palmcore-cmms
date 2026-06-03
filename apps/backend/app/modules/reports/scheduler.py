from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.core.database import AsyncSessionLocal
from app.modules.reports.analytics import refresh_report_cache

scheduler = AsyncIOScheduler(timezone="UTC")


async def _refresh_reports() -> None:
    async with AsyncSessionLocal() as session:
        await refresh_report_cache(session)


def start_reports_scheduler() -> None:
    scheduler.add_job(
        _refresh_reports,
        trigger="interval",
        minutes=60,
        next_run_time=datetime.utcnow(),
    )
    scheduler.start()
