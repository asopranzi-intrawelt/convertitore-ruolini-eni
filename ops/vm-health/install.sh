#!/usr/bin/env bash
# Installa atop, il controllo di salute e la configurazione del watchdog.
# Uso: sudo bash ops/vm-health/install.sh   (idempotente)
set -euo pipefail

if [ "$(id -u)" -ne 0 ]; then
    echo "Va lanciato con sudo" >&2
    exit 1
fi
SRC="$(cd "$(dirname "$0")" && pwd)"

apt-get install -y atop
systemctl enable --now atop.service

install -m 0755 "$SRC/vm-health-check.py" /usr/local/sbin/vm-health-check
install -d -m 0755 /etc/vm-health /var/lib/vm-health
if [ ! -e /etc/vm-health/vm-health.conf ]; then
    install -m 0644 "$SRC/vm-health.conf" /etc/vm-health/vm-health.conf
fi
install -m 0644 "$SRC/vm-health-check.service" "$SRC/vm-health-check.timer" "$SRC/i6300esb-watchdog.service" /etc/systemd/system/
install -d -m 0755 /etc/systemd/system.conf.d
install -m 0644 "$SRC/60-watchdog.conf" /etc/systemd/system.conf.d/60-watchdog.conf

systemctl daemon-reload
systemctl enable --now i6300esb-watchdog.service
systemctl daemon-reexec
systemctl enable --now vm-health-check.timer
/usr/local/sbin/vm-health-check

echo "== verifica"
systemctl is-active atop.service vm-health-check.timer
systemctl show -p RuntimeWatchdogUSec
ls /dev/watchdog* 2>/dev/null || echo "nessun /dev/watchdog: manca ancora il dispositivo lato Proxmox"
wdctl 2>/dev/null | head -6 || true
journalctl -t vm-health -n 5 --no-pager || true
