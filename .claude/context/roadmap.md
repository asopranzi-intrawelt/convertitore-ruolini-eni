---
generated-from-commit: 2da37cf
generated-from-branch: main
generated-date: 2026-06-12
covers-paths:
  - ./**
last-verified-commit: 2da37cf
---

# Roadmap

## Fase 1 — Hostname LAN (prossima)

Sostituire `192.168.20.22:5000` con il nome host `convertitore-ruolini` nell'URL di accesso.
Richiede configurazione DNS o `/etc/hosts` e rebuild React.

## Fase 2 — Refactoring

Riorganizzare l'architettura per separare chiaramente le responsabilità:
- backend Flask: solo API, nessuna logica di serving statico
- frontend React: struttura componenti più chiara, rimozione del codice Certificazioni
  inutilizzato
- gestione uniforme delle variabili d'ambiente
- rimozione del backend Node.js incompleto (`IntraPanel/backend/`)

## Fase 3 — Ottimizzazione VM Proxmox

Disabilitare i servizi inutili (GNOME, Apache2, MariaDB, CUPS, ecc.), impostare il boot
target a `multi-user`, ridurre RAM e CPU allocate dalla console Proxmox. Documentazione
completa in `PROXMOX_OTTIMIZZAZIONE.md`.

## Fase 4 — Autostart e robustezza

Configurare il servizio Flask come unit systemd dell'utente con `loginctl enable-linger`,
in modo che parta automaticamente al boot senza richiedere login interattivo.

## Non in roadmap

Autenticazione utente: fuori scope, l'accesso è controllato dall'IP.
Deployment su cloud pubblico: non previsto.
