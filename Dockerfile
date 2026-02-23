# ============================================================
# Stage 1 – builder
# Instala dependências Python e baixa os browsers do Playwright
# ============================================================
FROM python:3.12-slim AS builder

WORKDIR /build

# Cria um virtualenv isolado para copiar ao stage final
COPY requirements.txt .
RUN python -m venv /venv && \
    /venv/bin/pip install --no-cache-dir --upgrade pip && \
    /venv/bin/pip install --no-cache-dir -r requirements.txt

# Baixa o Chromium em um diretório fixo (será copiado ao runtime)
ENV PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers
RUN /venv/bin/python -m playwright install chromium


# ============================================================
# Stage 2 – runtime
# Imagem final: apenas o necessário para rodar
# ============================================================
FROM python:3.12-slim AS runtime

WORKDIR /app

# Copia o virtualenv completo do builder
COPY --from=builder /venv /venv

# Adiciona o venv ao PATH e define o caminho dos browsers
ENV PATH="/venv/bin:$PATH" \
    PLAYWRIGHT_BROWSERS_PATH=/opt/pw-browsers \
    PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Instala dependências de sistema do Chromium + gosu (drop de privilégio no entrypoint)
# playwright install-deps já roda apt-get update internamente
RUN playwright install-deps chromium && \
    apt-get install -y --no-install-recommends gosu && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copia os browsers do builder
COPY --from=builder /opt/pw-browsers /opt/pw-browsers

# Cria usuário não-root com UID/GID 1000 (igual ao usuário do host)
# para que o bind mount do config.yaml e logs/ tenha permissão de escrita
RUN groupadd -g 1000 tasker && \
    useradd -u 1000 -g tasker -m -s /bin/sh tasker && \
    chown -R tasker:tasker /opt/pw-browsers

# Copia o código da aplicação com ownership do usuário não-root
COPY --chown=tasker:tasker . .

# Cria diretório de logs com permissão correta
RUN mkdir -p logs && chown tasker:tasker logs

# Entrypoint: roda como root, corrige permissões dos bind mounts e troca para tasker
RUN chmod +x /app/entrypoint.sh

EXPOSE 8000

ENTRYPOINT ["/app/entrypoint.sh"]
CMD ["python", "main.py"]
