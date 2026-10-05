# Salute della VM 204: atop, controllo ogni 5 minuti, watchdog

Nasce dal blocco del 12/09/2026, quando il sistema ospite si è fermato e il servizio è rimasto irraggiungibile per 23 giorni senza che nessuno lo sapesse, mentre Proxmox mostrava la VM `running`. Il dettaglio è nel work-log del 05/10/2026. Questa cartella copre ciò che si può fare dentro la VM; la parte comune a tutte le VM di Proxmox (canale di notifica, controllo di silenzio, sorgenti del collettore) è registrata come cosa da fare in `D:\network-design` e appartiene al progetto `D:\log-collector`.

## Che cosa installa

`atop` registra ogni 10 minuti quali processi usano CPU, memoria e disco, e conserva 28 giorni. Serve a rispondere a posteriori alla domanda che il 05/10 è rimasta aperta: quale processo teneva occupato un core dal 06/09. Si legge con `atop -r /var/log/atop/atop_AAAAMMGG`, e con `t` e `T` si scorre nel tempo.

`vm-health-check` gira ogni 5 minuti da un timer systemd e scrive nel journal con tag `vm-health` quando trova un processo sopra l'80% di un core per 30 minuti, swap oltre 1 GiB, memoria disponibile sotto 200 MiB, un intervento dell'OOM killer, nginx o `intrapanel` non attivi, oppure nginx che non risponde in locale. L'allarme include i processi principali del momento, non si ripete prima di 60 minuti e al rientro scrive una riga di chiusura. Le soglie sono in `/etc/vm-health/vm-health.conf`. Gli allarmi si leggono con `journalctl -t vm-health`.

`60-watchdog.conf` fa sì che systemd tenga vivo il watchdog hardware della VM: se il sistema resta bloccato per 30 secondi, il dispositivo fa resettare la VM a Proxmox. Diventa operativo solo quando il dispositivo esiste, cioè dopo `qm set 204 --watchdog model=i6300esb,action=reset` sul nodo e uno spegnimento con riaccensione della VM; fino ad allora systemd segnala l'assenza e prosegue. Su Ubuntu c'è un secondo ostacolo, scoperto il 05/10/2026: i file `/lib/modprobe.d/blacklist_linux-*.conf` del kernel mettono in blacklist i driver watchdog, compreso `i6300esb`, quindi la scheda compare in `lspci` ma `/dev/watchdog` non esiste. `systemd-modules-load` rispetta la blacklist, per cui l'installatore aggiunge `i6300esb-watchdog.service`, che all'avvio carica il modulo per nome con `modprobe`. La verifica è `wdctl`, che deve mostrare il dispositivo `i6300ESB timer`.

## Installazione

Dalla cartella del repository sulla VM, con la password di `sudo`:

```bash
sudo bash ops/vm-health/install.sh
```

Lo script è idempotente e non sovrascrive una configurazione già presente in `/etc/vm-health/`. Una prova senza effetti si fa con `python3 ops/vm-health/vm-health-check.py --dry-run --state /tmp/vmh.json --conf ops/vm-health/vm-health.conf`.

## Limiti dichiarati

Un controllo che gira dentro la VM non può segnalare il blocco della VM stessa, perché si ferma con lei: contro quel caso servono il watchdog e un controllo esterno, che è il controllo di silenzio del collettore. Finché non c'è un relay SMTP, `NOTIFY_CMD` resta vuoto e gli allarmi non escono dalla VM: vanno letti nel journal o, quando la VM sarà sorgente del collettore, arriveranno lì.
