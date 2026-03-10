#!/usr/bin/env bash
# deploy.sh — Déploiement de api-auto-quote sur VPS Ubuntu 24.04 LTS
# Usage : sudo bash /opt/api-auto-quote/deploy.sh

set -e

SERVICE="api-auto-quote"
WORKDIR="/opt/api-auto-quote"
PORT=5001
UNIT="/etc/systemd/system/${SERVICE}.service"

echo "=== [1/5] Création du venv et installation des dépendances Python ==="
python3 -m venv "${WORKDIR}/venv"
"${WORKDIR}/venv/bin/pip" install -r "${WORKDIR}/requirements.txt"

echo "=== [2/5] Ouverture du port ${PORT} via ufw ==="
ufw allow ${PORT}/tcp
ufw --force enable

echo "=== [3/5] Création du service systemd ==="
cat > "${UNIT}" <<EOF
[Unit]
Description=api-auto-quote — Moteur de cotation automatique assurance auto
After=network.target

[Service]
User=root
WorkingDirectory=${WORKDIR}
ExecStart=${WORKDIR}/venv/bin/python3 ${WORKDIR}/api.py
Restart=always
RestartSec=5
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

echo "=== [4/5] Activation et démarrage du service ==="
systemctl daemon-reload
systemctl enable "${SERVICE}"
systemctl restart "${SERVICE}"

# Laisser le service démarrer
sleep 2

echo "=== [5/5] Résumé ==="
IP=$(hostname -I | awk '{print $1}')
echo ""
echo "Service  : ${SERVICE}"
echo "Statut   :"
systemctl status "${SERVICE}" --no-pager -l
echo ""
echo "URLs disponibles :"
echo "  Health : http://${IP}:${PORT}/health"
echo "  Show   : http://${IP}:${PORT}/show"
echo "  Receive: http://${IP}:${PORT}/receive  (POST)"
echo ""
echo "Déploiement terminé."
