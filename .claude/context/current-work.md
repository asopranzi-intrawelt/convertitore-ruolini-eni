---
generated-from-commit: 0516741
generated-from-branch: main
generated-date: 2026-06-16
covers-paths:
  - odoo_service/flask_service.py
  - odoo_service/odoo_handler/rpc/xml_rpc.py
  - IntraPanel/frontend/**
  - nginx.conf
  - setup-nginx.sh
  - .claude/**
last-verified-commit: 0516741
---

# Feature attiva

Stato: refactoring per la LAN completato e in produzione (cutover al commit `0516741`, verificato
da un client LAN reale). L'attività aperta in coda è uniformare l'utente Odoo (task #4).

## Refactoring architettura (Fase 2 roadmap) — completato e deployato

L'architettura è stata separata: nginx serve la build statica da `/var/www/convertitore-ruolini`
ai tre IP autorizzati e inoltra le sole rotte API a Flask `127.0.0.1:5000`, che ora è solo-API.
Aggiunti il timeout `proxy_read_timeout 600s` su `/save`, l'URL API relativo same-origin nel
frontend, e una cache della sessione XML-RPC che dimezza i tempi di conversione senza cambiare i
risultati. Risolto contestualmente il bug Odoo del 12/06 in `xml_rpc.py`. Verifica end-to-end da
client `.73`: output identico al noto-buono. Dettaglio architettura e deploy in `deployment.md`.

Restano fuori dal lavoro fatto, come possibili passi successivi: rimuovere `IntraPanel/backend/`
(Node.js non operativo) e pulire il componente Certificazioni (inutilizzato).

## Separazione test e produzione — adottata

Produzione su `main` nella cartella principale, con deploy in LAN via `setup-nginx.sh`. Sviluppo
nel worktree `develop` sotto `convertitore-ruolini-eni-dev`, con test locale su porte dedicate.
Baseline vergine `eni-report+intrapanelUI` (backend 5050, frontend 3000) come riferimento e
ripiego. Procedura completa in `deployment.md` e `dev-testing.md`.

## Prossima attività

### 1. Uniformare utente Odoo ad asopranzi@intrawelt.com (task #4) — prossima

`gmandolesi@intrawelt.com` non è più dipendente. `main` e `develop` leggono l'utente dal `.env`,
dove c'è già `asopranzi@intrawelt.com`, quindi vanno solo verificati. La copia vergine
`eni-report` ha invece `gmandolesi` e la password cablati nel sorgente
(`odoo_handler/rpc/xml_rpc.py`): vanno sostituiti con `asopranzi`, idealmente spostando le
credenziali in un `.env` come negli altri ambienti.

## Domande aperte

- OS del client 192.168.10.75, per le istruzioni del file hosts (manca ancora la voce
  `192.168.20.22 convertitore-ruolini`).
- Sincronizzare `STACK.md` e `design-and-security.md` alla nuova architettura (Flask solo-API,
  nginx serve la build, build in `/var/www`, cache XML-RPC).
