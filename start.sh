#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$SCRIPT_DIR/odoo_service/.venv311/bin/python"
FLASK_APP="$SCRIPT_DIR/odoo_service/flask_service.py"

echo "Avvio IntraPanel su http://192.168.20.22:5000"
echo "Accesso consentito solo a: 192.168.10.73, 192.168.10.74, 192.168.10.75"

cd "$SCRIPT_DIR/odoo_service"
exec "$VENV" flask_service.py
