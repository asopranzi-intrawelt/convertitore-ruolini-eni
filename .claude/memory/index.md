# Snapshot di sincronizzazione

> Da leggere per primo a inizio sessione. Fotografa lo stato del progetto al commit di
> riferimento e mappa ogni scheda al suo stato di verifica. È la fonte di verità su cosa è fatto,
> non le spunte del diario.

## Stato

```
Branch attivo:         main
Commit di riferimento: 0a25c2e
Data snapshot:         2026-06-15
```

## Stato di verifica delle schede

| Scheda | last-verified | Stato |
|---|---|---|
| STACK.md | 2da37cf | stale (nginx aggiunto) |
| design-and-security.md | 2da37cf | stale (IP restriction spostata su nginx) |
| deployment.md | 2da37cf | stale (URL cambiato, nginx in stack) |
| dev-testing.md | 2da37cf | aggiornata |
| current-work.md | 2da37cf | stale (Proxmox completato, refactoring attivo) |
| roadmap.md | 2da37cf | aggiornata |

## Punto di ripresa

Hostname `convertitore-ruolini` attivo e funzionante su 2/3 client (192.168.10.75 manca
voce in /etc/hosts). nginx su porta 80 fa da proxy a Flask su 127.0.0.1:5000 con IP
restriction. Flask non più esposto direttamente in LAN. Systemd user service attivo con linger.
Proxmox optimization completata e verificata post-reboot: RAM 2 GB, CPU 2 vCPU, servizi inutili
disabilitati, app up dopo il riavvio; boot target lasciato `graphical.target` per scelta.
Prossimo: refactoring su branch separato (nginx serve la build React, Flask solo API,
rimozione `IntraPanel/backend/`, pulizia Certificazioni). Aperto: voce /etc/hosts su .75.
