#!/usr/bin/env bash
# Instala e sobe a API na VM (Ubuntu 24.04 LTS).
# Uso, dentro da VM:  sudo bash deploy/setup.sh
set -euo pipefail

APP_DIR=/opt/api-tarefas
DATA_DIR=/var/lib/api-tarefas
REPO_DIR="$(cd "$(dirname "$0")/.." && pwd)"

echo ">> Instalando pacotes do sistema"
apt-get update -y
apt-get install -y python3-venv nginx sqlite3

echo ">> Copiando a aplicação para $APP_DIR"
mkdir -p "$APP_DIR" "$DATA_DIR"
cp -r "$REPO_DIR/app" "$REPO_DIR/requirements.txt" "$APP_DIR/"

echo ">> Criando ambiente virtual Python e instalando dependências"
python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install --upgrade pip
"$APP_DIR/venv/bin/pip" install -r "$APP_DIR/requirements.txt"

chown -R www-data:www-data "$APP_DIR" "$DATA_DIR"

echo ">> Configurando o serviço systemd"
cp "$REPO_DIR/deploy/api-tarefas.service" /etc/systemd/system/
systemctl daemon-reload
systemctl enable --now api-tarefas
systemctl restart api-tarefas

echo ">> Configurando o Nginx (porta 80 -> 8000)"
cp "$REPO_DIR/deploy/nginx-api-tarefas.conf" /etc/nginx/sites-available/api-tarefas
ln -sf /etc/nginx/sites-available/api-tarefas /etc/nginx/sites-enabled/api-tarefas
rm -f /etc/nginx/sites-enabled/default
nginx -t
systemctl restart nginx

sleep 2
echo ">> Teste local:"
curl -s http://127.0.0.1/health && echo
echo ">> Pronto! Acesse http://<IP_PUBLICO_DA_VM>/docs"
