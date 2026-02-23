#!/bin/sh
set -e

# Corrige permissões dos arquivos montados como bind mount (host → container).
# Necessário pois o UID do host pode ser diferente do UID do container.
chmod 666 /app/config.yaml 2>/dev/null || true
chmod 777 /app/logs      2>/dev/null || true

# Troca para o usuário não-root e executa o comando passado via CMD
exec gosu tasker "$@"
