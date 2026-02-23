import uvicorn
from dotenv import load_dotenv
from apscheduler.schedulers.background import BackgroundScheduler

from core.config_loader import load_config
from core.logger import setup_logger
from web.app import app, set_scheduler
from web.scheduler_utils import reschedule

load_dotenv()
logger = setup_logger()


def main():
    config = load_config("config.yaml")

    scheduler = BackgroundScheduler(timezone="America/Sao_Paulo")
    set_scheduler(scheduler)
    reschedule(scheduler, config)
    scheduler.start()

    logger.info("Servidor web iniciado em http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="warning")

    scheduler.shutdown()


if __name__ == "__main__":
    main()
