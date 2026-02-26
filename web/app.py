import sys
import os
import threading

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import yaml
from pathlib import Path
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel

from datetime import date
from core.config_loader import load_config
from core.job_runner import run_job
from core.logger import setup_logger

logger = setup_logger()

BASE_DIR = Path(__file__).parent
CONFIG_PATH = BASE_DIR.parent / "config.yaml"
TEMPLATES_DIR = BASE_DIR / "templates"

app = FastAPI(title="Tasker Automação")
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

# Referência ao scheduler criado no main.py (injetado em runtime)
_scheduler = None


def set_scheduler(scheduler):
    global _scheduler
    _scheduler = scheduler


# ── Rotas ──────────────────────────────────────────────────────────────────


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    config = load_config(str(CONFIG_PATH))
    jobs = config.get("jobs") or []
    yaml_content = CONFIG_PATH.read_text(encoding="utf-8")
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "jobs": jobs,
            "yaml_content": yaml_content,
            "today": str(date.today()),
        },
    )


@app.get("/api/config")
async def get_config():
    return {"content": CONFIG_PATH.read_text(encoding="utf-8")}


class ConfigBody(BaseModel):
    content: str


@app.post("/api/config")
async def save_config(body: ConfigBody):
    # Valida o YAML antes de salvar
    try:
        parsed = yaml.safe_load(body.content)
    except yaml.YAMLError as e:
        raise HTTPException(status_code=400, detail=f"YAML inválido: {e}")

    # Aceita YAML vazio/sem jobs (apenas comenta tudo) — sem lançar erro
    if parsed is not None and not isinstance(parsed, dict):
        raise HTTPException(status_code=400, detail="YAML deve ser um mapeamento (chave: valor).")

    CONFIG_PATH.write_text(body.content, encoding="utf-8")
    logger.info("config.yaml atualizado via interface web.")

    # Reagenda os jobs com o novo config
    if _scheduler:
        from web.scheduler_utils import reschedule
        reschedule(_scheduler, parsed or {})

    return {"ok": True, "message": "config.yaml salvo e jobs reagendados."}


class JobBody(BaseModel):
    name: str
    date: str
    time: str
    task_id: str
    hours: float | None = None
    actions: list[str]


def _save_config(config: dict) -> None:
    """Serializa e salva o config.yaml, reagendando os jobs."""
    content = yaml.dump(config, allow_unicode=True, default_flow_style=False, sort_keys=False)
    CONFIG_PATH.write_text(content, encoding="utf-8")
    if _scheduler:
        from web.scheduler_utils import reschedule
        reschedule(_scheduler, config)


@app.post("/api/jobs")
async def create_job(body: JobBody):
    config = load_config(str(CONFIG_PATH))
    jobs = config.get("jobs") or []
    job = {"name": body.name, "date": body.date, "time": body.time, "task_id": body.task_id, "actions": body.actions}
    if body.hours is not None:
        job["hours"] = body.hours
    jobs.append(job)
    config["jobs"] = jobs
    _save_config(config)
    logger.info(f"Job '{body.name}' criado via interface web.")
    return {"ok": True, "message": f"Job '{body.name}' criado."}


@app.put("/api/jobs/{index}")
async def update_job(index: int, body: JobBody):
    config = load_config(str(CONFIG_PATH))
    jobs = config.get("jobs") or []
    if index < 0 or index >= len(jobs):
        raise HTTPException(status_code=404, detail="Job não encontrado.")
    job = {"name": body.name, "date": body.date, "time": body.time, "task_id": body.task_id, "actions": body.actions}
    if body.hours is not None:
        job["hours"] = body.hours
    jobs[index] = job
    config["jobs"] = jobs
    _save_config(config)
    logger.info(f"Job '{body.name}' (índice {index}) atualizado via interface web.")
    return {"ok": True, "message": f"Job '{body.name}' atualizado."}


@app.delete("/api/jobs/{index}")
async def delete_job(index: int):
    config = load_config(str(CONFIG_PATH))
    jobs = config.get("jobs") or []
    if index < 0 or index >= len(jobs):
        raise HTTPException(status_code=404, detail="Job não encontrado.")
    removed = jobs.pop(index)
    config["jobs"] = jobs
    _save_config(config)
    logger.info(f"Job '{removed.get('name')}' removido via interface web.")
    return {"ok": True, "message": f"Job '{removed.get('name')}' removido."}


class RunJobBody(BaseModel):
    job_index: int


@app.post("/api/run-job")
async def run_job_now(body: RunJobBody):
    config = load_config(str(CONFIG_PATH))
    jobs = config.get("jobs") or []

    if body.job_index < 0 or body.job_index >= len(jobs):
        raise HTTPException(status_code=404, detail="Job não encontrado.")

    job = jobs[body.job_index]
    logger.info(f"Execução manual do job '{job.get('name')}' via interface web.")

    # Roda em thread separada para não bloquear a resposta HTTP
    thread = threading.Thread(target=run_job, args=(job,), daemon=True)
    thread.start()

    return {"ok": True, "message": f"Job '{job.get('name')}' iniciado."}


@app.get("/api/jobs")
async def list_jobs():
    config = load_config(str(CONFIG_PATH))
    jobs = config.get("jobs") or []
    result = []
    for i, job in enumerate(jobs):
        result.append({
            "index": i,
            "name": job.get("name"),
            "date": job.get("date"),
            "time": job.get("time"),
            "task_id": job.get("task_id"),
            "hours": job.get("hours"),
            "actions": job.get("actions", []),
        })
    return {"jobs": result}
