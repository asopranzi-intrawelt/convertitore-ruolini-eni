---
generated-from-commit: 2da37cf
generated-from-branch: main
generated-date: 2026-06-12
covers-paths:
  - IntraPanel/frontend/package.json
  - IntraPanel/frontend/src/**
  - odoo_service/flask_service.py
last-verified-commit: 2da37cf
---

# Sviluppo e test

## Avvio in sviluppo

Non esiste un ambiente di sviluppo separato dalla produzione. Per modificare il frontend si
lavora sul codice sorgente in `IntraPanel/frontend/src/`, poi si esegue `npm run build` nella
stessa cartella per aggiornare la build che Flask serve. Non è configurato un dev server con
hot reload.

Per avviare Flask in sviluppo (dalla cartella `odoo_service/`):

```bash
.venv311/bin/python3.11 flask_service.py
```

## Test del frontend

Il progetto usa Create React App con il test runner Jest (`react-scripts test`). Non esistono
test scritti: la cartella `src/` contiene solo i file di stub generati da CRA (`App.test.js`,
`setupTests.js`). Il comando `npm test` è presente ma non produce output utile.

## Verifica manuale del deployment

Dopo una modifica al backend o alla build React, la verifica funzionale avviene aprendo
`http://192.168.20.22:5000` dal browser su uno dei tre IP autorizzati e caricando un file
Excel di test. Non esiste una suite di test di integrazione automatizzata.

Dalla macchina server, la risposta del servizio si verifica con:

```bash
# Deve restituire 403 (IP non autorizzato)
curl -s -o /dev/null -w "%{http_code}" http://127.0.0.1:5000/
```

## Build React

```bash
cd IntraPanel/frontend
npm run build
```

La build legge `IntraPanel/frontend/.env` e incorpora `REACT_APP_REPORT_API` e
`REACT_APP_CERT_API` negli asset JavaScript. Dopo la build, il processo Flask non va
riavviato: serve i nuovi file statici dalla stessa cartella `build/`.

Il comando `npm install` richiede `--legacy-peer-deps` perché il `package.json` usa dipendenze
con conflitti di peer tra le versioni.
