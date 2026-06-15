---
generated-from-commit: 0a25c2e
generated-from-branch: main
generated-date: 2026-06-15
covers-paths:
  - odoo_service/flask_service.py
  - IntraPanel/frontend/**
  - .claude/**
last-verified-commit: 0a25c2e
---

# Feature attiva

Stato: refactoring architettura in avvio su branch separato. Proxmox optimization completata e
verificata post-reboot il 2026-06-15.

## Hostname LAN — completato (2/3 client)

`http://convertitore-ruolini` funziona su 192.168.10.73 e 192.168.10.74.
192.168.10.75: manca la voce `192.168.20.22 convertitore-ruolini` nel file hosts di quella
macchina. Il server è configurato correttamente.

## Strategia di sviluppo senza ambiente di test

Non esiste un ambiente di staging. Il deployment di produzione è l'unico:
- nginx su porta 80 → Flask su 127.0.0.1:5000
- systemd user service `intrapanel` con linger attivo

Per sviluppare senza interrompere il servizio:
1. Lavorare su un branch git separato (`git checkout -b refactoring`)
2. Testare modifiche Flask lanciando un'istanza temporanea su porta 5001 dal branch e
   verificando con `curl http://127.0.0.1:5001/`
3. Deploy: `systemctl --user stop intrapanel` → merge branch → `systemctl --user start intrapanel`
   (downtime di pochi secondi, preferibilmente fuori orario lavorativo)
4. Tag dello stato funzionante prima di ogni fase rischiosa: `git tag v1-working`

## Proxmox optimization (Fase 3 roadmap) — completata

Riduzione risorse applicata dalla console Proxmox (RAM 2 GB, CPU 2 vCPU) e verificata con un
reboot il 2026-06-15: nginx e il service `intrapanel` tornano up al boot, l'app risponde,
`free -h` mostra ~635 Mi disponibili con ~693 Mi di swap in uso. Servizi disabilitati e non più
attivi: `apache2`, `cups`, `cups-browsed`, `bluetooth`, `avahi-daemon`, `ModemManager`,
`gnome-remote-desktop`, `kerneloops`, `power-profiles-daemon`, `switcheroo-control`, `mariadb`.
Il boot target è stato lasciato `graphical.target` per scelta esplicita, perché la VM è anche
workstation; `gdm` è `static` e resta caricato di conseguenza, `gnome-shell` è il principale
consumatore residuo di RAM (~202 MB). Dettaglio in `PROXMOX_OTTIMIZZAZIONE.md`.

## Prossime feature (in ordine)

### 1. Refactoring architettura (Fase 2 roadmap) — attiva

Su branch `refactoring`, separare le responsabilità:
- nginx serve direttamente la build React (elimina la catch-all da Flask)
- Flask: solo API su 127.0.0.1:5000
- Rimuovere `IntraPanel/backend/` (Node.js non operativo)
- Uniformare gestione variabili d'ambiente
- Pulizia componente Certificazioni (inutilizzato)

## Definition of done per Proxmox — raggiunta (con una deroga)

- Servizi inutili disabilitati e verificati non più attivi al reboot: fatto
- RAM e CPU ridotte dalla console Proxmox (2 GB / 2 vCPU): fatto
- App ancora raggiungibile dopo il reboot: verificato
- Boot target a `multi-user`: deroga consapevole, lasciato `graphical.target` perché la VM è
  anche workstation. Resta come possibile ottimizzazione futura se la pressione sullo swap
  diventasse un problema (recupererebbe ~250 MB)

## Domande aperte

- OS del client 192.168.10.75 (per istruzioni file hosts)
