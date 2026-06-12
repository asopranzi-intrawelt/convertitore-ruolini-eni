# Work-log

> Append-only. Ogni voce registra data, file toccati, motivo e commit di riferimento, in ordine
> cronologico inverso (più recente in cima).

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
