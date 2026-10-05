# Work-log

> Append-only. Ogni voce registra data, file toccati, motivo e commit di riferimento, in ordine cronologico inverso (più recente in cima).

---

## 2026-10-05 — Presidi contro un nuovo blocco: atop, controllo ogni 5 minuti, watchdog, 4 GB fissi

Commit di riferimento: questo commit. File creati: `ops/vm-health/` (`vm-health-check.py`, timer e servizio systemd, `vm-health.conf`, `60-watchdog.conf`, `i6300esb-watchdog.service`, `install.sh`, `README.md`). File modificati: `.claude/context/deployment.md` (sezione Salute della VM; corretta la frase sul 403 da localhost, che dal commit `253b2f3` risponde 200), `PROXMOX_OTTIMIZZAZIONE.md` (punto 4 dichiarato superato), `.claude/memory/index.md`. Motivo: il blocco del 12/09 è durato 23 giorni perché nessun controllo se n'è accorto e niente ha riavviato la VM.

Eseguito dall'utente con `sudo bash ops/vm-health/install.sh` e sulla shell del nodo. Dentro la VM: `atop` attivo con registro giornaliero in `/var/log/atop/`; `vm-health-check.timer` ogni 5 minuti, primo giro con esito 0 e nessun allarme; `RuntimeWatchdogSec=30s` caricato da systemd. Sul nodo: `qm set 204 --watchdog model=i6300esb,action=reset --memory 4096`, poi `qm shutdown 204 && qm start 204`. Dopo il riavvio la scheda `6300ESB Watchdog Timer` compariva in `lspci` ma `/dev/watchdog` mancava: i file `blacklist_linux-*.conf` del kernel Ubuntu escludono `i6300esb` e `systemd-modules-load` rispetta la blacklist, quindi è stato aggiunto `i6300esb-watchdog.service`, che carica il modulo per nome all'avvio; `wdctl` mostra ora `i6300ESB timer`, timeout 30 s, con keepalive attivo. Seconda sorpresa: la VM avviata con 4 GB ne vedeva 1,4, perché la configurazione aveva `balloon: 1024` e il nodo è vicino all'80% di RAM usata, soglia oltre la quale Proxmox riprende memoria agli ospiti; con `qm set 204 --balloon 4096` il balloon si è sgonfiato a caldo. Servizio verificato dalla LAN con `200` su porta 80 e 8090.

Non fatto qui e registrato in `D:\network-design` (#205-#207 e `docs/log-collector-integrazione.md`), dove l'IT Manager ha deciso che il presidio vale per tutte le VM ed è affidato a `D:\log-collector`: relay SMTP, senza il quale `NOTIFY_CMD` resta vuoto e gli allarmi restano nel journal; la VM come sorgente del collettore con heartbeat; *fleecing* sui lavori di backup. Il watchdog non è stato provato con un blocco simulato, quindi resta da collaudare in una finestra concordata.

---

## 2026-10-05 — Servizio irraggiungibile in LAN: VM 204 bloccata dal 12/09, ripristinata con reset

Commit di riferimento: nessuna modifica di codice né di configurazione; aggiornati solo questo work-log, `LAN_SETUP.md` (riga di troubleshooting) e `index.md` (aperti). Sintomo: `http://convertitore-ruolini/` e `:8090` non rispondevano dalla LAN. Diagnosi dalla postazione .73: la rete è piatta (/19, on-link), le VM vicine .21, .24, .25 e il gateway rispondevano, la .22 non rispondeva nemmeno all'ARP, quindi né firewall né `allow` di nginx erano in causa. Sul nodo Proxmox `qm status 204` dava `running` con uptime di circa 112 giorni, ma il guest agent non rispondeva, la console mostrava "Display output is not active" e l'API riportava `cpu: 0` con 1,7 GB di RAM su 2: sistema ospite in stallo con il processo QEMU vivo. Ripristino con `qm reset 204` alle 11:57; dopo il boot nginx è attivo, la LAN riceve `200` su porta 80 e 8090, Flask su 127.0.0.1:5010 e qemu-guest-agent attivi, CPU a riposo al 99,7% idle.

Quando e perché, per quanto i dati consentono. Il journal del boot precedente si interrompe il 12/09/2026 dopo le 01:30, senza panic, OOM o errori di disco registrati; l'ultimo evento di rilievo è il `guest-fsfreeze` delle 01:01, cioè il backup notturno vzdump della VM (job delle 01:00, durata tipica circa un'ora), e le righe scritte fino alle 01:30 mostrano che il filesystem era di nuovo scrivibile dopo il freeze. Il servizio è quindi rimasto giù per circa 23 giorni senza che nessun controllo lo segnalasse, e i backup notturni successivi risultano `OK` perché fotografano una VM bloccata. Nella settimana precedente sysstat mostra un'anomalia netta: dal 06/09 un core è occupato al 100% in modo costante (31% user, 18% system, load piatto a 1,00), mentre il 04/09 la macchina era al 99,75% idle; RAM al 19% e iowait nullo fino all'ultimo campione, ma 1,7 GB di swap occupati e commit al 115%. Fra le due date l'unico evento rilevante nel journal è l'aggiornamento automatico del 05/09 alle 06:27 (kernel HWE 7.0.0-31, openssh, sssd, gnupg, spice-vdagent). Il collegamento fra quel consumo, l'aggiornamento e il blocco è un'ipotesi, non un fatto accertato: sysstat non registra i dati per processo e il processo responsabile non è più identificabile. Il boot di oggi è il primo sul kernel 7.0.0-31; fino al 12/09 girava 6.17.0-35.

Pendenti: controllare fra qualche giorno con `sar -u` se il consumo costante si ripresenta e, nel caso, identificare il processo con `top` o `pidstat`; valutare un controllo di disponibilità esterno (ping o HTTP dalla LAN) perché lo stato `running` di Proxmox non dice se l'ospite è vivo; valutare un watchdog per la VM (`watchdog: model=i6300esb,action=reset` sul nodo e servizio watchdog nell'ospite). Diagnosi condotta dalla postazione dell'IT Manager via SSH e dalla shell del nodo Proxmox.

---

## 2026-06-16 — Riscrittura della logica di conversione ruolino (su develop)

Commit di riferimento: branch `develop`, in attesa di deploy. Vedi ADR-005 per il dettaglio operativo. File toccato: `odoo_service/flask_service.py`. Motivo: allineare la conversione all'output reale richiesto, dedotto da un benchmark di cinque coppie sorgente/`_IW` (gennaio-maggio 2026) in `/home/intrawelt/Scaricati`. La vecchia logica produceva un foglio `Control` rimappato da cui l'operatore costruiva il `_IW` a mano; la nuova scrive in posizione nel foglio `Fattura` del sorgente i valori Odoo nelle colonne 16, 19, 20, 22 e 30 (pagine, asseverazione, legalizzazione piu apostille, bollo, "quantita marche"), aggiunge un foglio `Controllo IW` con il registro prima/dopo per la revisione, e salva e serve il file come `<sorgente>_IW.xlsx`. Indici di colonna resi costanti leggibili; rimossi `get_eni_data_report`, `controls`, `add_style` e l'intera macchina del foglio `Control`; la robustezza Odoo del task #5 e' confluita nell'helper `valori_odoo` (errore di connessione chiaro, ordine non trovato gestito). Validazione: end-to-end via applicazione su tutti e cinque i mesi, le cinque colonne coincidono col benchmark salvo dieci note di urgenza, lasciate al controllo manuale per decisione esplicita, e due asseverazioni in drift del dato Odoo. La nota di urgenza e quella cliente non hanno un segnale nei dati e restano annotazioni manuali del revisore. Pendente: commit su `develop`, poi deploy in produzione (merge `develop`->`main` ed esecuzione di `setup-nginx.sh`). Nota a margine: ADR-001 e ADR-002 risultano superati dal refactoring nginx gia in produzione, da formalizzare come ADR a parte.

---

## 2026-06-16 — Refactoring in produzione (cutover) e separazione ambienti

Commit di riferimento: 0516741 (merge di `refactoring` in `main`). Cutover dell'architettura: nginx serve la build statica da `/var/www/convertitore-ruolini`, Flask diventa solo-API su 127.0.0.1:5000, `proxy_read_timeout 600s` su `/save`. Eseguito `setup-nginx.sh` (riscritto per pubblicare la build in /var/www e installare il config dalla fonte unica `nginx.conf`) e riavviato il service. Verificato da client LAN reale (.73): output identico al noto-buono, zero celle diverse. Branch `refactoring` (commit 03b927d) portava: fix Odoo, URL API relativo same-origin (`ReportProvider.js` + `.env` vuoto), timeout nginx, cache della sessione XML-RPC in `xml_rpc.py` (conversione ~121s invece di ~295s, output invariato). Stabilita la separazione ambienti: worktree `develop` in `convertitore-ruolini-eni-dev` per lo sviluppo, `main` per la produzione, copia vergine `eni-report+intrapanelUI` come baseline. Documentazione: riscritte `deployment.md` e `dev-testing.md`; aggiornato `index.md`. Pulizia: rimosso il worktree `refactoring`, fermate le istanze di validazione (5060/5061/8080/8081). Pendente: STACK.md e design-and-security.md da sincronizzare alla nuova architettura.

---

## 2026-06-15/16 — Diagnosi e fix del bug Odoo (Track 3) e copia vergine locale (Track 2)

Commit di riferimento: ae41e6b (fix), 466e90b (URL relativo) su `main`. Una conversione di prova falliva silenziosamente: `/save` 500 e `/download` restituiva un file vecchio omonimo. Causa, bug pre-esistente dal 12/06: in `odoo_handler/rpc/xml_rpc.py` due righe residue `self.url = url` / `self.db = db` sovrascrivevano con `None` l'URL letto dal `.env`, quindi ogni chiamata XML-RPC moriva con `unsupported XML-RPC protocol` e l'except lasciava `orders` non assegnato (UnboundLocalError). Rimosse le due righe; verificato uid Odoo 2622 e conversione end-to-end corretta su `main`. Reso poi relativo l'URL API del frontend per togliere il network error in locale. Diagnosi condotta in isolamento su istanze temporanee (Flask 5001, nginx 8080) senza toccare la produzione. Track 2: allestita la copia vergine `eni-report+intrapanelUI` (venv minimale flask/flask-cors/openpyxl, backend 5050, frontend CRA 3000), che NON ha il bug e punta a localhost; validata con conversione completa. Resta `gmandolesi@intrawelt.com` cablato nel suo sorgente, da sostituire (task #4).

---

## 2026-06-15 — Proxmox optimization: verifica post-reboot

Commit di riferimento: 0a25c2e (verifica di runtime, nessuna modifica di codice) Riduzione risorse applicata dalla console Proxmox: RAM a 2 GB, CPU a 2 vCPU. Reboot di verifica eseguito. Dopo il riavvio risultano up sia nginx (active, listen 0.0.0.0:80, syntax OK) sia il systemd user service `intrapanel` (active, 127.0.0.1:5000, HTTP 200, linger attivo). nginx applica la IP restriction: da 127.0.0.1 risponde 403, corretto perché `allow/deny` valuta l'IP TCP reale, non l'header `X-Real-IP`. `free -h`: 1,9 Gi totali, ~1,3 Gi usati, ~635 Mi disponibili, ~693 Mi di swap. Boot target ancora `graphical.target` per scelta esplicita (la VM è anche workstation): `gnome-shell` resta il principale consumatore (~202 MB) e spiega l'uso di swap; chiude così la pendenza "riduzione RAM/CPU" della voce precedente.

---

## 2026-06-15 — Proxmox optimization

Commit di riferimento: 0a25c2e (modifiche solo su file di configurazione sistema, non in repo) Servizi disabilitati: cups, cups-browsed, avahi-daemon, ModemManager, bluetooth, gnome-remote-desktop, kerneloops, power-profiles-daemon, switcheroo-control, mariadb. Desktop GNOME mantenuto su richiesta esplicita (gdm + graphical.target invariati). Aggiornato: PROXMOX_OTTIMIZZAZIONE.md con stato eseguito al 2026-06-15. Pendente: riduzione RAM/CPU dalla console Proxmox (operazione manuale dell'utente).

---

## 2026-06-15 — Hostname LAN e nginx

Commit di riferimento: 0a25c2e File modificati: `odoo_service/flask_service.py` (rimossa IP restriction, binding su 127.0.0.1), `IntraPanel/frontend/.env` (URL aggiornato a http://convertitore-ruolini), `.claude/settings.json` (PROJECT_NAME corretto), `CLAUDE.md` (nome progetto corretto). File creati: `nginx.conf`, `setup-nginx.sh`, `disable-apache.sh`, `~/.config/systemd/user/intrapanel.service`, `/tmp/s.sh`. Motivo: accesso via hostname `convertitore-ruolini` su porta 80; nginx fa da reverse proxy con IP restriction; Flask vincolato a 127.0.0.1:5000; Apache2 disabilitato; systemd user service con loginctl enable-linger per autostart al boot. Pendente: voce /etc/hosts su 192.168.10.75.

---

## 2026-06-12 — Inizializzazione sistema di progetto portabile

Commit di riferimento: 2da37cf (unico commit esistente) File creati: `CLAUDE.md`, `CLAUDE.local.md`, `.claude/settings.json`, `.claude/PROJECT-SYSTEM.md`, `.claude/rules/*`, `.claude/skills/*`, `.claude/templates/*`, `.claude/memory/*`, `.claude/context/*`, `_notes/*`. Motivo: allineamento retroattivo allo standard portabile su progetto esistente; nessuna storia git modificata.

---

## 2026-06-12 — Prima sessione operativa: LAN deployment

Commit di riferimento: 2da37cf File modificati: `odoo_service/flask_service.py`, `IntraPanel/frontend/src/Context/ReportProvider.js`, `IntraPanel/frontend/src/Context/CertificazioniProvider.js`, `IntraPanel/frontend/.env`, `IntraPanel/frontend/package.json`, `odoo_service/odoo_handler/rpc/xml_rpc.py`, `odoo_service/Dockerfile`, `odoo_service/requirements_docker.txt`. File creati: `IntraPanel/frontend/nginx.conf`, `docker-compose.yml`, `start.sh`, `LAN_SETUP.md`, `PROXMOX_OTTIMIZZAZIONE.md`, `odoo_service/.env`. Motivo: rendere l'app accessibile in LAN ai tre IP 192.168.10.73/.74/.75; correggere i `localhost` hardcodati nel frontend; aggiungere IP restriction in Flask; Flask serve anche la React build statica; credenziali Odoo spostate da codice a file `.env` non tracciato.
