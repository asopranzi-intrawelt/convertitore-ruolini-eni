---
generated-from-commit: 0516741
generated-from-branch: main
generated-date: 2026-06-16
covers-paths:
  - IntraPanel/frontend/package.json
  - IntraPanel/frontend/src/**
  - odoo_service/flask_service.py
  - nginx.conf
last-verified-commit: 0516741
---

# Sviluppo e test

## Dove si sviluppa

Lo sviluppo non avviene mai nella cartella di produzione, ma nel worktree dedicato
`/home/intrawelt/Scrivania/convertitore-ruolini-eni-dev`, sul branch `develop`. Si modifica e si
committa lì; la produzione su `main` resta intoccata finché non si decide un deploy. Il ciclo è
lineare: si lavora su `develop`, si testa in locale, si fa confluire in `main` con un merge, si
esegue la procedura di deploy descritta in `deployment.md`. La cartella di produzione e quella di
sviluppo sono due viste dello stesso repository agganciate a branch diversi, perciò un eventuale
riavvio della VM ricarica sempre il codice di `main` dalla cartella di produzione, mai quello in
lavorazione.

Per creare il worktree di sviluppo, se non c'è:

```bash
git worktree add /home/intrawelt/Scrivania/convertitore-ruolini-eni-dev -b develop main
```

## Test locale dello stack refactorizzato

L'obiettivo è riprodurre in locale, dentro la VM, esattamente ciò che vedrà la LAN, cioè nginx
che serve la build statica e inoltra le API a un Flask solo-API, ma senza la IP restriction e su
porte dedicate, così da poterlo aprire dal browser della macchina senza essere respinti con 403
e senza collidere con la produzione che occupa la porta 80 e la 5000.

Il backend di test si avvia dalla cartella `odoo_service/` del worktree di sviluppo su una porta
libera, riusando il virtual environment di produzione, e necessita di una copia del file `.env`
con le credenziali Odoo perché `.env` non è tracciato da git e quindi assente nel worktree:

```bash
cp /home/intrawelt/Scrivania/convertitore-ruolini-eni/odoo_service/.env odoo_service/.env
PY=/home/intrawelt/Scrivania/convertitore-ruolini-eni/odoo_service/.venv311/bin/python
cd odoo_service
"$PY" -c "from flask_service import app; app.run(host='127.0.0.1', port=5060)"
```

Davanti gli si mette un nginx locale su una porta alta, con la radice puntata alla build e il
proxy verso il backend di test, identico alla produzione tranne l'assenza di `allow`/`deny`. Lo
si lancia come utente normale, con prefisso e file temporanei sotto `/tmp`, così non interferisce
con il nginx di sistema. Il blocco essenziale del server è:

```nginx
server {
    listen 127.0.0.1:8080;
    root /percorso/build;
    index index.html;
    location ~ ^/(get-login|trex|upload|save|download) {
        proxy_pass http://127.0.0.1:5060;
        proxy_read_timeout 600s;
    }
    location / { try_files $uri /index.html; }
}
```

Si apre poi `http://localhost:8080/` dal browser della VM e si fa una conversione vera. Una nota
importante: dopo il cutover `http://localhost:5000/` non mostra più l'interfaccia, perché Flask è
solo-API e l'interfaccia la serve nginx; il test locale dell'interfaccia passa quindi da questo
stack su porta 8080, non dalla 5000.

Queste istanze locali sono avviate a mano e non sopravvivono a un riavvio della macchina. Se
servisse renderle permanenti, andrebbero incapsulate in systemd user service come quello di
produzione.

## Copia vergine come riferimento

La copia `eni-report+intrapanelUI` gira in locale con backend sulla porta 5050 e frontend, dev
server React, sulla 3000. È uno stato noto-funzionante isolato, utile sia come baseline
d'emergenza sia per validare la correttezza di una conversione: si confronta l'output prodotto
dallo stack in prova con quello della vergine sullo stesso file sorgente, e i fogli dati
`INTRAWELT sas` e `Control` devono coincidere cella per cella. Le differenze legittime sono solo
quelle dovute a dati Odoo cambiati nel frattempo.

## Build React

```bash
cd IntraPanel/frontend
npm run build
```

La build legge `IntraPanel/frontend/.env`. Con le variabili vuote l'URL dell'API è relativo e la
build è agnostica rispetto all'ambiente. Il processo Flask non va riavviato dopo una build, ma in
produzione la build non è servita da Flask bensì pubblicata in `/var/www` da `setup-nginx.sh`,
quindi è quel passo a rendere effettiva una nuova build per i client LAN.

## Test automatici

Il progetto usa Create React App con Jest come test runner, ma non esistono test scritti: la
cartella `src/` contiene solo gli stub generati da CRA. Non c'è una suite di integrazione
automatizzata; la verifica è manuale, tramite una conversione reale e il confronto degli output
descritto sopra.
