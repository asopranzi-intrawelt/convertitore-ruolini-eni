---
generated-from-commit: 0516741
generated-from-branch: main
generated-date: 2026-06-16
covers-paths:
  - nginx.conf
  - setup-nginx.sh
  - odoo_service/flask_service.py
  - odoo_service/odoo_handler/rpc/xml_rpc.py
  - odoo_service/.venv311/**
  - IntraPanel/frontend/build/**
  - PROXMOX_OTTIMIZZAZIONE.md
last-verified-commit: 0516741
---

# Deployment

## Architettura di produzione

L'applicazione è in produzione su una singola VM Proxmox raggiungibile a `192.168.20.22`,
accessibile via browser su `http://convertitore-ruolini` (porta 80). I client devono avere la
voce `192.168.20.22 convertitore-ruolini` nel proprio file hosts.

A partire dal commit `0516741` la responsabilità è separata fra nginx e Flask, e non più
concentrata su Flask come in origine. nginx, sulla porta 80, fa due cose. Serve direttamente
dal disco la build statica della SPA[^1] React, che vive in `/var/www/convertitore-ruolini` ed
è di proprietà di `www-data`, l'utente con cui gira il worker nginx. E applica la *IP
restriction*: ammette i soli `192.168.10.73`, `192.168.10.74`, `192.168.10.75`, e risponde 403
a qualunque altro indirizzo, valutando l'IP TCP reale della connessione e non header inoltrati.
Solo le rotte applicative `/get-login`, `/trex/*`, `/upload`, `/save`, `/download/*` vengono
inoltrate in *proxy* al backend Flask su `127.0.0.1:5000`, che non è più esposto direttamente
in LAN e non serve più alcuna interfaccia: alla radice `/` risponde 404 perché è puro backend
API. Tutto il resto cade sul ramo statico con fallback su `index.html`, secondo lo schema delle
*single page application*.

Due dettagli della configurazione nginx meritano attenzione. Sulla location delle API è
impostato `proxy_read_timeout 600s`, perché la rotta `/save` arricchisce il foglio interrogando
Odoo riga per riga e una conversione può durare alcuni minuti: il default di 60 secondi
produrrebbe un 504 a metà elaborazione. La build servita usa URL relativi, cioè le chiamate API
partono verso la stessa origine da cui è servita la pagina, così una sola build vale tanto in
locale quanto in LAN senza dover ricompilare per ambiente.

Il backend Flask legge le credenziali Odoo dal file `.env` e mantiene una sessione XML-RPC[^2]
condivisa fra le istanze, autenticandosi una sola volta per coppia di credenziali invece che a
ogni riga del ruolino. Questo riduce di oltre la metà i tempi di conversione senza cambiare
alcun risultato.

Il repository remoto è `git@github.com:asopranzi-intrawelt/convertitore-ruolini-eni.git`,
autenticato via SSH con la chiave ed25519 sull'account asopranzi-intrawelt.

## Separazione fra ambiente di sviluppo e produzione

La strategia adottata tiene fisicamente separati tre ambienti sulla stessa macchina, così da
poter sviluppare e validare senza mai rischiare la continuità del servizio in LAN.

La produzione è il branch `main`, nella cartella di progetto principale
`/home/intrawelt/Scrivania/convertitore-ruolini-eni`. È da questa cartella che gira il systemd
user service, quindi è questa la sola vista del repository che il servizio carica al riavvio o
al reboot. Si tocca solo per il deploy, non per lo sviluppo.

Lo sviluppo avviene in un *worktree* git separato, la cartella
`/home/intrawelt/Scrivania/convertitore-ruolini-eni-dev`, permanentemente sul branch `develop`
ramificato da `main`. Un worktree è una seconda vista dello stesso repository agganciata a un
altro branch: si lavora e si committa lì senza spostare il branch della produzione, e un branch
può essere attivo in un solo worktree alla volta, perciò non si fa mai `git checkout` del branch
sbagliato nella cartella di produzione. Le modifiche si testano in locale su porte dedicate, si
fanno confluire in `main` con un merge, e solo allora si esegue la procedura di deploy. Il
dettaglio operativo del test locale è in `dev-testing.md`.

Esiste infine una copia *vergine* di sicurezza, l'unione `eni-report+intrapanelUI` sotto
`/home/intrawelt/Scrivania`, che riproduce uno stato noto-funzionante completamente isolato dal
repository di produzione. Serve da baseline d'emergenza e da riferimento per validare gli output:
gira in locale con backend sulla porta 5050 e frontend sulla 3000, e non va modificata se non
per gli allineamenti indispensabili.

## Procedura di deploy

Il deploy parte dalla cartella di produzione sul branch `main`, dopo aver fatto confluire da
`develop` le modifiche già validate in locale. Se è cambiato il frontend, si ricompila prima la
build, perché è ciò che verrà pubblicato:

```bash
cd IntraPanel/frontend
npm run build
```

Poi si esegue lo script di deploy come root. Lo script pubblica la build in
`/var/www/convertitore-ruolini` assegnandone la proprietà a `www-data`, installa il server block
nginx dalla fonte unica `nginx.conf` e ricarica nginx in modo grazioso, senza tagliare le
connessioni:

```bash
sudo bash setup-nginx.sh
```

Infine si riavvia il backend, che da quel momento carica il codice aggiornato:

```bash
systemctl --user restart intrapanel
```

L'ordine rende il disservizio minimo: dopo `setup-nginx.sh` l'app è già funzionante perché nginx
serve la nuova build e inoltra le API al Flask ancora attivo, e il riavvio successivo è questione
di pochi secondi. Prima di un cutover rischioso conviene taggare lo stato funzionante, ad esempio
`git tag pre-deploy-<data>`, così il rollback è `git reset --hard <tag>` seguito da una nuova
esecuzione di `setup-nginx.sh` e dal riavvio del backend.

## Comandi

Flask è un systemd user service con linger attivo, quindi riparte da solo al boot:

```bash
systemctl --user status intrapanel    # stato
systemctl --user restart intrapanel   # riavvio dopo modifiche al backend
journalctl --user -u intrapanel -f    # log in tempo reale
```

nginx è un systemd system service:

```bash
sudo nginx -t                         # verifica sintassi prima di ricaricare
sudo systemctl reload nginx           # ricarica graziosa dopo modifiche al config
```

Verifica rapida che i due servizi siano in ascolto, la porta 80 di nginx e la 5000 di Flask:

```bash
ss -tlnp | grep -E ':80|:5000'
```

Da localhost nginx risponde 403 per via della IP restriction: è il comportamento atteso, non un
errore. La verifica funzionale reale va fatta dal browser di un client autorizzato.

## Virtual environment

Il runtime Python è `.venv311/` sotto `odoo_service/`, creato con `python3.11` perché su questa
VM `python3.12-venv` non è installato mentre `python3.11-venv` sì. Gli script `pip` e `flask`
usano shebang assoluti: se la cartella del progetto viene rinominata o spostata vanno aggiornati.

```bash
OLD=/percorso/vecchio/odoo_service/.venv311
NEW=/percorso/nuovo/odoo_service/.venv311
grep -rl "$OLD" "$NEW/bin/" | while read f; do sed -i "s|$OLD|$NEW|g" "$f"; done
```

## Variabili d'ambiente e segreti

`odoo_service/.env`, non tracciato, da creare manualmente su ogni nuovo ambiente. L'utente Odoo
da usare è `asopranzi@intrawelt.com`.

```
ODOO_URL=https://trex.intrawelt.com
ODOO_DB=intrawelt
ODOO_USERNAME=asopranzi@intrawelt.com
ODOO_PASSWORD=<password Odoo>
```

`IntraPanel/frontend/.env`, non tracciato. Dopo il refactoring l'URL dell'API è relativo, quindi
le variabili vanno lasciate vuote: una build vuota produce chiamate same-origin valide sia in
locale sia in LAN. Un valore esplicito serve solo se si vuole forzare un backend diverso.

```
REACT_APP_REPORT_API=
REACT_APP_CERT_API=
```

[^1]: *SPA*, Single Page Application - applicazione web in cui la navigazione avviene lato
client senza ricaricare la pagina; il server restituisce sempre `index.html` per i percorsi non
corrispondenti a file statici, e il routing è gestito da JavaScript nel browser.

[^2]: *XML-RPC*, XML Remote Procedure Call - protocollo con cui Flask interroga Odoo invocando
metodi remoti su un endpoint HTTP, scambiando parametri e risultati serializzati in XML.
