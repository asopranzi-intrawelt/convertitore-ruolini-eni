# Ottimizzazione VM su Proxmox — IntraPanel

Questa VM ospita esclusivamente il servizio IntraPanel (Flask + React). Al momento
consuma ~5 GB di RAM su 8 disponibili a causa di servizi inutili. Obiettivo: ridurre
il consumo di RAM e CPU liberando risorse sulla VM Proxmox.

---

## 1. Disabilitare i servizi inutili (dalla VM)

### Stato al 2026-06-15 — ESEGUITO

I seguenti servizi sono stati disabilitati con lo script `proxmox-opt.sh`:

| Servizio | Motivo |
|---|---|
| `cups` + `cups-browsed` | Stampa — non usata su server |
| `avahi-daemon` | mDNS/Zeroconf — non necessario |
| `ModemManager` | Modem — assente su VM |
| `bluetooth` | Bluetooth — assente su VM |
| `gnome-remote-desktop` | Desktop remoto GNOME — non usato |
| `kerneloops` | Reporter crash kernel — non utile |
| `power-profiles-daemon` | Gestione energetica — non utile su VM |
| `switcheroo-control` | Switch GPU — non utile su VM |
| `mariadb` | DB locale — app usa solo Odoo XML-RPC esterno |
| `apache2` | Web server — rimpiazzato da nginx |

**Nota:** il desktop GNOME è stato mantenuto (`gdm` + `graphical.target`) per permettere
l'accesso diretto al SO dalla console Proxmox o dalla macchina fisica.
`avahi-daemon` risulta ancora attivo nella sessione corrente (riattivato da D-Bus) ma non
si avvierà al prossimo reboot.

### Comandi manuali se necessario

```bash
sudo systemctl disable --now <nome-servizio>
sudo systemctl enable --now <nome-servizio>   # per riabilitare
```

---

## 2. Avvio automatico di IntraPanel al boot

### Opzione A — Servizio utente systemd (consigliata, nessun root permanente)

```bash
mkdir -p ~/.config/systemd/user/

cat > ~/.config/systemd/user/intrapanel.service << 'EOF'
[Unit]
Description=IntraPanel Flask Service
After=network.target

[Service]
Type=simple
WorkingDirectory=/home/intrawelt/Scrivania/convertitore-ruolini-eni/odoo_service
ExecStart=/home/intrawelt/Scrivania/convertitore-ruolini-eni/odoo_service/.venv311/bin/python flask_service.py
Restart=on-failure
RestartSec=5
StandardOutput=append:/tmp/intrapanel.log
StandardError=append:/tmp/intrapanel.log

[Install]
WantedBy=default.target
EOF

systemctl --user enable intrapanel
sudo loginctl enable-linger intrawelt   # necessario una sola volta
```

### Opzione B — Servizio di sistema (root)

```bash
sudo cp /etc/systemd/system/intrapanel.service << 'EOF'
[Unit]
Description=IntraPanel Flask Service
After=network.target

[Service]
Type=simple
User=intrawelt
WorkingDirectory=/home/intrawelt/Scrivania/convertitore-ruolini-eni/odoo_service
ExecStart=/home/intrawelt/Scrivania/convertitore-ruolini-eni/odoo_service/.venv311/bin/python flask_service.py
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable --now intrapanel
```

---

## 3. Regole firewall ufw (dalla VM)

La porta 5000 deve essere accessibile solo dai tre IP della LAN:

```bash
sudo ufw allow from 192.168.10.73 to any port 5000
sudo ufw allow from 192.168.10.74 to any port 5000
sudo ufw allow from 192.168.10.75 to any port 5000
sudo ufw reload
sudo ufw status numbered
```

---

## 4. Ridurre RAM e CPU dal nodo Proxmox

Trovare l'ID della VM nel pannello Proxmox (es. `101`), poi dal terminale
del **nodo Proxmox** (non dalla VM):

```bash
# Sostituire 101 con il VMID corretto
qm set 101 --memory 1024 --cores 1 --balloon 512
```

| Parametro | Valore consigliato | Note |
|---|---|---|
| `--memory` | 1024 (MB) | 1 GB è abbondante per Flask + 3 utenti |
| `--cores` | 1 | Flask è single-threaded per default |
| `--balloon` | 512 | Memoria minima garantita (balloon driver) |

Se si vuole essere più generosi: `--memory 2048 --cores 2`.

> **Attenzione:** modificare la RAM a caldo potrebbe richiedere un riavvio della VM
> perché venga applicata correttamente.

---

## 5. Verifica dopo il riavvio

```bash
# RAM in uso dopo il riavvio
free -h

# Servizi attivi
systemctl list-units --type=service --state=running --no-pager

# Flask e nginx in ascolto
ss -tlnp | grep -E '80|5000'

# Test nginx (403 da localhost — non è in allow list)
curl -s -o /dev/null -w "HTTP %{http_code}\n" -H "Host: convertitore-ruolini" http://127.0.0.1:80/
```
