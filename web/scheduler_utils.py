from apscheduler.schedulers.background import BackgroundScheduler
from core.job_runner import run_job
from core.logger import setup_logger
from datetime import datetime

logger = setup_logger()


def reschedule(scheduler: BackgroundScheduler, config: dict):
    """Remove todos os jobs do scheduler e reagenda com o novo config."""
    scheduler.remove_all_jobs()

    jobs = (config or {}).get("jobs") or []
    now = datetime.now()

    if not jobs:
        logger.info("Nenhum job no config — scheduler sem tarefas agendadas.")
        return

    for job in jobs:
        name = job.get("name", "job")
        date_str = job.get("date")
        time_str = job.get("time", "00:00")

        if not date_str:
            logger.warning(f"Job '{name}' sem campo 'date' — ignorado.")
            continue

        run_date_str = f"{date_str} {time_str}:00"

        try:
            run_date = datetime.strptime(run_date_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            logger.warning(f"Job '{name}' com data inválida '{run_date_str}' — ignorado.")
            continue

        if run_date <= now:
            logger.warning(f"Job '{name}' agendado para {run_date_str} já passou — ignorado.")
            continue

        scheduler.add_job(
            func=run_job,
            trigger="date",
            run_date=run_date,
            name=name,
            kwargs={"job": job},
        )

        logger.info(f"Job agendado: '{name}' para {run_date_str}")
