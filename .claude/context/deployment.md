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
last-verified-commit: 2da37cf
---

# Deployment

## Livello unico: LAN Intrawelt

L'applicazione è in produzione su una singola VM Proxmox raggiungibile all'indirizzo
`192.168.20.22`. Non esistono ambienti di staging o di test separati. L'accesso è consentito
ai soli IP statici `192.168.10.73`, `192.168.10.74`, `192.168.10.75`; ogni altro indirizzo
riceve HTTP 403.

L'URL di accesso dal browser è `http://192.168.20.22:5000`.

Il repository remoto è `https://github.com/asopranzi-intrawelt/convertitore-ruolini-eni`.

## Comandi

Avvio del servizio dalla radice del progetto:

```bash
bash start.sh
```

Avvio in background con log persistente:

```bash
nohup bash start.sh > /tmp/intrapanel.log 2>&1 &
```

Build della React SPA (necessaria dopo ogni modifica al frontend o al file `.env`):

```bash
cd IntraPanel/frontend
npm run build
```

Verifica che il servizio sia attivo:

```bash
ss -tlnp | grep 5000
tail -f /tmp/intrapanel.log
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
REACT_APP_REPORT_API=http://<IP server>:5000
REACT_APP_CERT_API=http://<IP server>:5000
```

Il valore di `<IP server>` è `192.168.20.22` nel deployment attuale.
