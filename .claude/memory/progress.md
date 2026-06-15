# Work-log

> Append-only. Ogni voce registra data, file toccati, motivo e commit di riferimento, in ordine
> cronologico inverso (più recente in cima).

---

## 2026-06-15 — Proxmox optimization: verifica post-reboot

Commit di riferimento: 0a25c2e (verifica di runtime, nessuna modifica di codice)
Riduzione risorse applicata dalla console Proxmox: RAM a 2 GB, CPU a 2 vCPU. Reboot di verifica
eseguito. Dopo il riavvio risultano up sia nginx (active, listen 0.0.0.0:80, syntax OK) sia il
systemd user service `intrapanel` (active, 127.0.0.1:5000, HTTP 200, linger attivo). nginx
applica la IP restriction: da 127.0.0.1 risponde 403, corretto perché `allow/deny` valuta
l'IP TCP reale, non l'header `X-Real-IP`. `free -h`: 1,9 Gi totali, ~1,3 Gi usati, ~635 Mi
disponibili, ~693 Mi di swap. Boot target ancora `graphical.target` per scelta esplicita
(la VM è anche workstation): `gnome-shell` resta il principale consumatore (~202 MB) e spiega
l'uso di swap; chiude così la pendenza "riduzione RAM/CPU" della voce precedente.

---

## 2026-06-15 — Proxmox optimization

Commit di riferimento: 0a25c2e (modifiche solo su file di configurazione sistema, non in repo)
Servizi disabilitati: cups, cups-browsed, avahi-daemon, ModemManager, bluetooth,
gnome-remote-desktop, kerneloops, power-profiles-daemon, switcheroo-control, mariadb.
Desktop GNOME mantenuto su richiesta esplicita (gdm + graphical.target invariati).
Aggiornato: PROXMOX_OTTIMIZZAZIONE.md con stato eseguito al 2026-06-15.
Pendente: riduzione RAM/CPU dalla console Proxmox (operazione manuale dell'utente).

---

## 2026-06-15 — Hostname LAN e nginx

Commit di riferimento: 0a25c2e
File modificati: `odoo_service/flask_service.py` (rimossa IP restriction, binding su 127.0.0.1),
`IntraPanel/frontend/.env` (URL aggiornato a http://convertitore-ruolini),
`.claude/settings.json` (PROJECT_NAME corretto), `CLAUDE.md` (nome progetto corretto).
File creati: `nginx.conf`, `setup-nginx.sh`, `disable-apache.sh`,
`~/.config/systemd/user/intrapanel.service`, `/tmp/s.sh`.
Motivo: accesso via hostname `convertitore-ruolini` su porta 80; nginx fa da reverse proxy con
IP restriction; Flask vincolato a 127.0.0.1:5000; Apache2 disabilitato; systemd user service
con loginctl enable-linger per autostart al boot.
Pendente: voce /etc/hosts su 192.168.10.75.

---

## 2026-06-12 — Inizializzazione sistema di progetto portabile

Commit di riferimento: 2da37cf (unico commit esistente)
File creati: `CLAUDE.md`, `CLAUDE.local.md`, `.claude/settings.json`,
`.claude/PROJECT-SYSTEM.md`, `.claude/rules/*`, `.claude/skills/*`, `.claude/templates/*`,
`.claude/memory/*`, `.claude/context/*`, `_notes/*`.
Motivo: allineamento retroattivo allo standard portabile su progetto esistente; nessuna
storia git modificata.

---

## 2026-06-12 — Prima sessione operativa: LAN deployment

Commit di riferimento: 2da37cf
File modificati: `odoo_service/flask_service.py`, `IntraPanel/frontend/src/Context/ReportProvider.js`,
`IntraPanel/frontend/src/Context/CertificazioniProvider.js`, `IntraPanel/frontend/.env`,
`IntraPanel/frontend/package.json`, `odoo_service/odoo_handler/rpc/xml_rpc.py`,
`odoo_service/Dockerfile`, `odoo_service/requirements_docker.txt`.
File creati: `IntraPanel/frontend/nginx.conf`, `docker-compose.yml`, `start.sh`,
`LAN_SETUP.md`, `PROXMOX_OTTIMIZZAZIONE.md`, `odoo_service/.env`.
Motivo: rendere l'app accessibile in LAN ai tre IP 192.168.10.73/.74/.75; correggere i
`localhost` hardcodati nel frontend; aggiungere IP restriction in Flask; Flask serve anche la
React build statica; credenziali Odoo spostate da codice a file `.env` non tracciato.
