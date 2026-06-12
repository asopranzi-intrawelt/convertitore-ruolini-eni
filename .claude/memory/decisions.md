# Registro delle decisioni architetturali

> Convenzione ADR-lite, append-only. Ogni decisione architetturale non ovvia entra come voce
> numerata con data, stato, contesto, decisione, motivazione e conseguenze. Una decisione non si
> cancella e non si riscrive: quando viene superata, si aggiunge una nuova voce che dichiara di
> superare la precedente e ne cita il numero. Le inferenze non confermate si marcano come da
> verificare e si promuovono a decisione solo quando una fonte le conferma.

## ADR-001 — Flask serve sia le API che la React SPA sulla stessa porta

Data: 2026-06-12
Stato: accettata
Contesto: il frontend React aveva bisogno di un server statico separato (Nginx, serve,
Node.js) e le URL delle API erano hardcodate su `localhost`, rendendo l'app inutilizzabile da
altre macchine in LAN. Docker non era disponibile sulla VM.
Decisione: Flask serve la build statica di React tramite una catch-all route, oltre alle API
esistenti, tutto sulla porta 5000. `static_folder=None` disabilita la route `/static/`
built-in di Flask che interferiva con i file della build React.
Motivazione: zero dipendenze aggiuntive (niente Nginx, niente Node in produzione), deployment
a un singolo processo, compatibile con il venv Python già presente.
Conseguenze: ogni modifica al codice React richiede `npm run build` prima che le modifiche
siano visibili; la porta 5000 è l'unico punto di ingresso per frontend e API.

## ADR-002 — IP restriction a livello applicativo in Flask

Data: 2026-06-12
Stato: accettata
Contesto: l'app deve essere accessibile solo ai tre IP statici della LAN Intrawelt
(192.168.10.73, .74, .75). ufw era attivo ma non bloccava (non abilitato in modalità
enforcing); nessun proxy inverso davanti a Flask.
Decisione: `@app.before_request` confronta `request.remote_addr` con un set di IP ammessi e
ritorna 403 per tutti gli altri. Le regole ufw per porta 5000 sono state aggiunte come
secondo livello di difesa, anche se ufw non era in enforcing mode al momento.
Motivazione: soluzione semplice, senza dipendenze infrastrutturali, funziona correttamente
quando Flask riceve le connessioni dirette (senza proxy intermedi che maschererebbero l'IP).
Conseguenze: se in futuro si aggiunge un proxy inverso (Nginx, Traefik), `request.remote_addr`
restituirà l'IP del proxy; in quel caso la restriction andrà spostata al proxy o si dovrà
leggere `X-Forwarded-For` con fiducia esplicita.

## ADR-003 — Credenziali Odoo in file .env non tracciato

Data: 2026-06-12
Stato: accettata
Contesto: le credenziali Odoo (`asopranzi@intrawelt.com` / password) erano hardcodate in
`odoo_handler/rpc/xml_rpc.py` e sarebbero finite nel repository git.
Decisione: le credenziali sono spostate in `odoo_service/.env`, escluso da git, e lette
tramite `python-dotenv` all'avvio. Il file `.env` va ricreato manualmente su ogni nuovo
ambiente di deployment.
Motivazione: nessun segreto nel repository; la rotazione della password non richiede un
commit.
Conseguenze: il deployment su una macchina nuova richiede la creazione manuale di
`odoo_service/.env` con le variabili `ODOO_URL`, `ODOO_DB`, `ODOO_USERNAME`, `ODOO_PASSWORD`.

## ADR-004 — Adozione del sistema di progetto portabile

Data: 2026-06-12
Stato: accettata
Contesto: il progetto necessita di uno stato interamente recuperabile da un clone e di
documentazione che resti allineata al codice senza rilettura integrale a ogni sessione.
Decisione: adottare il sistema descritto in `.claude/PROJECT-SYSTEM.md`, con motore di
riconciliazione ancorato ai commit e doppio livello documentale tracciato/ignorato.
Motivazione: persistenza strutturale su disco indipendente dalla sessione di chat, e controllo
umano sul versionamento.
Conseguenze: ogni passo significativo aggiorna schede, `last-verified-commit`, snapshot e
work-log; commit e push restano manuali.
