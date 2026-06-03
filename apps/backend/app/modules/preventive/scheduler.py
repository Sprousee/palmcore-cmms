from datetime import datetime

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.core.database import AsyncSessionLocal
from app.modules.preventive.cron_jobs import run_preventive_maintenance_job

scheduler = AsyncIOScheduler(timezone="UTC")


async def _run_preventive_job() -> None:
    async with AsyncSessionLocal() as session:
        await run_preventive_maintenance_job(session)


def start_preventive_scheduler() -> None:
    scheduler.add_job(
        _run_preventive_job,
        trigger="interval",
        minutes=15,
        next_run_time=datetime.utcnow(),
    )
    scheduler.start()
