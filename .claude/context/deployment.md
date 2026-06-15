---
generated-from-commit: 2da37cf
generated-from-branch: main
generated-date: 2026-06-12
covers-paths:
  - start.sh
  - odoo_service/flask_service.py
  - odoo_service/.venv311/**
  - IntraPanel/frontend/build/**
  - LAN_SETUP.md
  - PROXMOX_OTTIMIZZAZIONE.md
last-verified-commit: 0a25c2e
---

# Deployment

## Livello unico: LAN Intrawelt

L'applicazione è in produzione su una singola VM Proxmox raggiungibile all'indirizzo
`192.168.20.22`. Non esistono ambienti di staging o di test separati. L'accesso è consentito
ai soli IP statici `192.168.10.73`, `192.168.10.74`, `192.168.10.75`; ogni altro indirizzo
riceve HTTP 403 da nginx.

L'URL di accesso dal browser è `http://convertitore-ruolini` (porta 80, nginx).
I client devono avere la voce `192.168.20.22 convertitore-ruolini` nel file hosts locale.

Il repository remoto è `git@github.com:asopranzi-intrawelt/convertitore-ruolini-eni.git`
(SSH, autenticato con chiave ed25519 "VM ruolini" sull'account asopranzi-intrawelt).

## Comandi

Flask è gestito come systemd user service. Comandi principali:

```bash
systemctl --user status intrapanel    # stato
systemctl --user restart intrapanel   # riavvio dopo modifiche al backend
systemctl --user stop intrapanel      # stop
journalctl --user -u intrapanel -f    # log in tempo reale
```

nginx è gestito come systemd system service:

```bash
sudo systemctl status nginx
sudo systemctl restart nginx          # dopo modifiche a /etc/nginx/sites-available/
sudo nginx -t                         # verifica sintassi config prima del restart
```

Build della React SPA (necessaria dopo ogni modifica al frontend o al file `.env`):

```bash
cd IntraPanel/frontend
npm run build
```
Flask non va riavviato dopo la build: serve i nuovi file dalla stessa cartella `build/`.

Verifica che i servizi siano attivi:

```bash
ss -tlnp | grep -E '80|5000'
```

## Virtual environment

Il runtime Python è `.venv311/` sotto `odoo_service/`. Il file `bin/python3.11` è il solo
eseguibile che deve essere usato direttamente; gli altri script (`pip`, `flask`) usano lo
shebang assoluto e richiedono che il percorso della cartella contenitore del progetto
corrisponda a quello con cui gli shebang sono stati scritti. Se la cartella viene rinominata
o spostata, aggiornare gli shebang con:

```bash
OLD=/percorso/vecchio/odoo_service/.venv311
NEW=/percorso/nuovo/odoo_service/.venv311
grep -rl "$OLD" "$NEW/bin/" | while read f; do sed -i "s|$OLD|$NEW|g" "$f"; done
```

## Variabili d'ambiente e segreti

`odoo_service/.env` — non tracciato, da creare manualmente su ogni nuovo ambiente.

```
ODOO_URL=https://trex.intrawelt.com
ODOO_DB=intrawelt
ODOO_USERNAME=<email Odoo>
ODOO_PASSWORD=<password Odoo>
```

`IntraPanel/frontend/.env` — non tracciato, contiene gli URL del backend da incorporare
nella build React.

```
REACT_APP_REPORT_API=http://convertitore-ruolini
REACT_APP_CERT_API=http://convertitore-ruolini
```
