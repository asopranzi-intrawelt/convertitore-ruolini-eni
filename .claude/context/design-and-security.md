---
generated-from-commit: 2da37cf
generated-from-branch: main
generated-date: 2026-06-12
covers-paths:
  - odoo_service/flask_service.py
  - odoo_service/odoo_handler/**
last-verified-commit: 2da37cf
---

# Design e sicurezza

## Paradigmi di design

L'architettura è volutamente piatta: un solo processo Flask gestisce sia le API che la
distribuzione del frontend statico. Non esistono livelli di autenticazione utente: la
sicurezza perimetrale è affidata esclusivamente al controllo dell'IP sorgente. Questo modello
è adeguato a un contesto LAN chiuso dove i tre client sono macchine aziendali note; non è
adeguato a un'esposizione su rete pubblica.

Lo stato del file Excel caricato viene tenuto in un dizionario Python in memoria (`files` in
`flask_service.py`). Questo implica che il dizionario va perso a ogni riavvio del processo e
che non è condiviso tra più worker. Il server Flask è avviato in modalità single-process
(`app.run`), quindi non ci sono race condition sul dizionario.

## Controllo degli accessi

La IP restriction è implementata come hook `@app.before_request` in `flask_service.py`. Il
confronto avviene su `request.remote_addr`, che è l'IP diretto della connessione TCP.
Questo funziona correttamente solo in assenza di proxy intermedi: se in futuro venisse
aggiunto un reverse proxy, `request.remote_addr` restituirebbe l'IP del proxy e la
restriction dovrebbe essere spostata al proxy oppure gestita leggendo `X-Forwarded-For` con
una lista di proxy fidati esplicita (vedere ADR-002 in `memory/decisions.md`).

## Gestione dei segreti

Le credenziali Odoo (URL, database, username, password) sono lette a runtime dal file
`odoo_service/.env` tramite `python-dotenv`. Il file non è tracciato in git. La variabile
`ODOO_PASSWORD` non è mai esposta nelle risposte HTTP né nei log applicativi.

Il file `IntraPanel/frontend/.env` contiene solo l'URL del server (`REACT_APP_*`) e viene
incorporato nella build JavaScript al momento della compilazione: non contiene segreti.

## CORS

Flask-Cors è configurato con `CORS(app)` senza restrizioni di origine (`*`). Poiché la React
SPA è servita dalla stessa origine di Flask (stesso host e porta), le richieste del browser
sono same-origin e il CORS non interviene. La configurazione permissiva è quindi ininfluente
nel deployment attuale ma andrebbe ristretta se il frontend venisse servito separatamente.
