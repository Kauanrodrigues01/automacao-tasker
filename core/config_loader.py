import yaml
from pathlib import Path


def load_config(path: str = "config.yaml") -> dict:
    """Carrega e retorna o arquivo de configuração YAML."""
    config_path = Path(path)

    if not config_path.exists():
        raise FileNotFoundError(f"Arquivo de configuração não encontrado: {path}")

    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)
