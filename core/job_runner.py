from core.logger import setup_logger
from actions.login import login
from actions.add_hours import add_hours
from actions.set_task_executing import set_task_executing
from actions.set_task_completed import set_task_completed

logger = setup_logger()

ACTION_MAP = {
    "login": login,
    "add_hours": add_hours,
    "set_task_executing": set_task_executing,
    "set_task_completed": set_task_completed,
}


def run_job(job: dict):
    """
    Executa um job completo: abre o browser, roda as actions na ordem definida
    e fecha o browser ao final.

    Args:
        job: Dicionário com as configurações do job (name, task_id, hours, actions).
    """
    from core.browser import BrowserSession

    name = job.get("name", "job")
    task_id = job.get("task_id", "")
    hours = job.get("hours", 8)
    actions = job.get("actions", [])

    logger.info(f"Iniciando job: '{name}' | task: {task_id} | ações: {actions}")

    with BrowserSession() as page:
        for action_name in actions:
            if action_name not in ACTION_MAP:
                logger.warning(f"Ação desconhecida ignorada: '{action_name}'")
                continue

            logger.info(f"Executando ação: {action_name}")
            action_fn = ACTION_MAP[action_name]

            if action_name == "login":
                action_fn(page)

            elif action_name == "add_hours":
                action_fn(page, task_id, hours)

            elif action_name in ("set_task_executing", "set_task_completed"):
                action_fn(page, task_id)

    logger.info(f"Job '{name}' finalizado.")
