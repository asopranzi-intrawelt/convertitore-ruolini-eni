---
generated-from-commit: 2da37cf
generated-from-branch: main
generated-date: 2026-06-12
covers-paths:
  - odoo_service/**
  - IntraPanel/frontend/src/**
  - IntraPanel/backend/**
last-verified-commit: 2da37cf
---

# Stack applicativo

## Stack e runtime

Il backend è un'applicazione Flask 3.1.1 eseguita su Python 3.11 tramite il virtual
environment `.venv311` collocato sotto `odoo_service/`. La comunicazione con Odoo avviene
via XML-RPC standard di libreria (`xmlrpc.client`). Le dipendenze di runtime sono Flask,
Flask-Cors, openpyxl e python-dotenv; l'elenco canonico per il deployment Docker è in
`odoo_service/requirements_docker.txt`.

Il frontend è un'applicazione React 18 costruita con Create React App (`react-scripts` 5).
Il gestore di pacchetti è npm 9; i `node_modules` non sono tracciati. La build di produzione
è in `IntraPanel/frontend/build/` e non è tracciata. Le librerie UI sono Material UI 5 per i
componenti e React Router DOM 6 per il routing lato client. Le chiamate HTTP al backend
usano Axios.

Il backend Node.js sotto `IntraPanel/backend/` (Express 4) è codice incompleto e non viene
avviato in produzione: tutto il traffico transita da Flask.

Runtime fissati: Python 3.11 (venv), Node 18 (per la sola build), npm 9.

## Alternative deliberatamente escluse

Nginx come server statico: scartato perché Docker non è disponibile sulla VM e aggiunge una
dipendenza di sistema; Flask serve la build statica direttamente.

Docker Compose: presente come file di riferimento (`docker-compose.yml`) ma non usato in
produzione; i Dockerfile esistono ma non vengono eseguiti nel deployment attuale.

Backend Node.js (Express): presente in `IntraPanel/backend/` come scheletro ma non operativo;
la logica di business è interamente in Flask.

## Flussi di codice e ruolo architetturale dei file

Il flusso principale è il seguente. Il browser carica `index.html` dalla React build servita
da Flask. Il componente `Report.js` mostra la UI. L'utente carica un file Excel tramite
`ReportMenu.js`; l'evento chiama `upload()` in `ReportProvider.js`, che invia il file a
`POST /upload`. Flask lo legge con openpyxl, ne restituisce i dati come JSON e lo tiene in
un dizionario in memoria (`files`). L'utente clicca "Salva": `save()` in `ReportProvider.js`
invia i dati a `POST /save`. Flask arricchisce ogni riga interrogando Odoo via
`SaleOrder.get_list()` in `odoo_handler/models/sale_order.py`, che chiama `XmlRpc.get_call()`
in `odoo_handler/rpc/xml_rpc.py`. Il risultato viene scritto in un foglio di controllo Excel
e salvato sul filesystem. L'utente scarica il file tramite `GET /download/<filename>`.

`flask_service.py` è il punto di ingresso unico: definisce tutte le route API, la IP
restriction via `@app.before_request`, la catch-all che serve la React SPA, e avvia il
server su `0.0.0.0:5000`.

`ReportProvider.js` e `CertificazioniProvider.js` sono i due context React che centralizzano
le chiamate HTTP; la variabile `domain` in ciascuno legge `REACT_APP_REPORT_API` e
`REACT_APP_CERT_API` dal file `.env` al momento della build.

## Riferimenti a snippet

`odoo_service/flask_service.py:22-33` — IP restriction e catch-all SPA.
`odoo_service/odoo_handler/rpc/xml_rpc.py` — autenticazione e chiamata XML-RPC a Odoo.
`odoo_service/odoo_handler/models/sale_order.py` — query ordini di vendita con join su righe.
`IntraPanel/frontend/src/Context/ReportProvider.js:6` — `domain` da variabile d'ambiente.
`IntraPanel/frontend/src/components/Reports/Report.js` — componente principale della UI.
