# IntraPanel — Setup LAN Intrawelt

## Architettura

```
Browser (192.168.10.73 / .74 / .75)
         |
         | HTTP porta 5000
         v
  Server 192.168.20.22:5000
  Flask (Python 3.11, venv311)
  ├── Serve la React SPA (build statica)
  ├── IP restriction: solo .73 / .74 / .75 → 403 per tutti gli altri
  └── API: /upload  /save  /download/<file>  /trex/...
              |
              | XML-RPC
              v
       Odoo (https://trex.intrawelt.com)
```

---

## Percorsi chiave

| Cosa | Dove |
|---|---|
| Script di avvio | `/home/intrawelt/Scrivania/convertitore-ruolini-eni/start.sh` |
| Flask service | `/home/intrawelt/Scrivania/convertitore-ruolini-eni/odoo_service/flask_service.py` |
| React build (statica) | `/home/intrawelt/Scrivania/convertitore-ruolini-eni/IntraPanel/frontend/build/` |
| Virtual environment Python | `/home/intrawelt/Scrivania/convertitore-ruolini-eni/odoo_service/.venv311/` |
| Log Flask | `/tmp/intrapanel.log` |
| Credenziali Odoo (XML-RPC) | `odoo_service/odoo_handler/rpc/xml_rpc.py` |

---

## Avvio manuale

```bash
cd /home/intrawelt/Scrivania/convertitore-ruolini-eni
bash start.sh
```

Oppure in background con log:

```bash
nohup bash start.sh > /tmp/intrapanel.log 2>&1 &
```

---

## URL di accesso

`http://192.168.20.22:5000`

Accessibile **solo** da: `192.168.10.73`, `192.168.10.74`, `192.168.10.75`

---

## Cosa è stato modificato rispetto al codice originale

### Problema
Il frontend React aveva le URL delle API hardcodate su `localhost`:
- `ReportProvider.js` → `http://localhost:5000`
- `CertificazioniProvider.js` → `http://localhost:4000`

Nei browser degli altri PC, `localhost` punta alla loro macchina locale, non al server.
Risultato: tutte le chiamate API fallivano silenziosamente.

### Soluzione

**1. Variabili d'ambiente nel frontend** (`IntraPanel/frontend/.env`)
```
REACT_APP_REPORT_API=http://192.168.20.22:5000
REACT_APP_CERT_API=http://192.168.20.22:5000
```
Le URL vengono incorporate nella build in fase di compilazione (`npm run build`).

**2. Provider aggiornati** (una riga in ciascun file)
- `ReportProvider.js:6` → `const domain = process.env.REACT_APP_REPORT_API || "http://localhost:5000";`
- `CertificazioniProvider.js:6` → `const domain = process.env.REACT_APP_CERT_API || "http://localhost:4000";`

**3. Flask serve anche la React SPA** (`flask_service.py`)
Flask ora risponde a qualunque percorso sconosciuto restituendo `index.html` della build React,
quindi non serve un server separato (Nginx, serve, ecc.).

**4. IP restriction in Flask** (`flask_service.py`)
```python
ALLOWED_IPS = {'192.168.10.73', '192.168.10.74', '192.168.10.75'}

@app.before_request
def restrict_access():
    if request.remote_addr not in ALLOWED_IPS:
        abort(403)
```

**5. React build eseguita**
```bash
cd IntraPanel/frontend
npm run build
```
La build è già presente in `IntraPanel/frontend/build/` e non va rieseguita
salvo modifiche al codice frontend o al file `.env`.

---

## Quando rieseguire la build React

Rieseguire `npm run build` nella cartella `IntraPanel/frontend` solo se:
- Si cambia l'IP del server (modifica `.env`)
- Si modifica il codice JavaScript/React

---

## Firewall (ufw)

La porta 5000 deve essere aperta nel firewall per i tre IP:

```bash
sudo ufw allow from 192.168.10.73 to any port 5000
sudo ufw allow from 192.168.10.74 to any port 5000
sudo ufw allow from 192.168.10.75 to any port 5000
sudo ufw reload
```

Da eseguire **una sola volta**. Le regole persistono ai riavvii.

---

## Verifica che tutto funzioni

```bash
# Flask in esecuzione?
ss -tlnp | grep 5000

# Log in tempo reale
tail -f /tmp/intrapanel.log

# Test IP restriction (deve rispondere 403)
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:5000/
```

---

## Troubleshooting

| Sintomo | Causa probabile | Soluzione |
|---|---|---|
| `ERR_CONNECTION_REFUSED` | Flask non in esecuzione | `bash start.sh` |
| `ERR_CONNECTION_REFUSED` | ufw blocca porta 5000 | Aggiungere regole ufw (vedi sopra) |
| HTTP 403 dal browser | IP non in allow list | Verificare IP del client |
| Pagina bianca nel browser | Build React non aggiornata | `npm run build` in `IntraPanel/frontend` |
| Errore API `/upload` | Odoo non raggiungibile | Verificare VPN/connessione a `trex.intrawelt.com` |
