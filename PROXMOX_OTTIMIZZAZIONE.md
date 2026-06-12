# Ottimizzazione VM su Proxmox — IntraPanel

Questa VM ospita esclusivamente il servizio IntraPanel (Flask + React). Al momento
consuma ~5 GB di RAM su 8 disponibili a causa di servizi inutili (GNOME, Apache2,
MariaDB, CUPS, ecc.). Obiettivo: portarla a ~300-500 MB di RAM al boot.

---

## 1. Disabilitare i servizi inutili (dalla VM)

```bash
sudo systemctl disable --now \
  gdm \
  apache2 \
  mariadb \
  cups \
  cups-browsed \
  avahi-daemon \
  snapd \
  fwupd \
  kerneloops \
  ModemManager \
  colord \
  power-profiles-daemon \
  gnome-remote-desktop \
  unattended-upgrades
```

### Avviare in modalità testo al posto della grafica

```bash
sudo systemctl set-default multi-user.target
```

Dopo il prossimo riavvio la VM parte headless (nessun desktop), il che riduce
drasticamente l'uso di RAM. L'accesso rimane possibile via console Proxmox (VNC/SPICE).

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
# RAM in uso dopo il riavvio (atteso: < 500 MB)
free -h

# Servizi attivi (devono essere molto meno)
systemctl list-units --type=service --state=running --no-pager

# Flask in esecuzione
ss -tlnp | grep 5000

# Test accesso dalla VM stessa (403 atteso — non è in allow list)
curl -s -o /dev/null -w "HTTP %{http_code}\n" http://127.0.0.1:5000/
```
