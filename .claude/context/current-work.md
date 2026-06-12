---
generated-from-commit: 2da37cf
generated-from-branch: main
generated-date: 2026-06-12
covers-paths:
  - odoo_service/flask_service.py
  - IntraPanel/frontend/**
last-verified-commit: 2da37cf
---

# Feature attiva

Stato: in lavorazione

## Cosa fa

Rendere l'app accessibile in LAN tramite il nome host `convertitore-ruolini` invece
dell'indirizzo `192.168.20.22:5000`, mantenendo l'IP restriction ai soli tre indirizzi
autorizzati.

## File da modificare

- Configurazione DNS/hosts sulla VM o sul router LAN: aggiungere record `A` che mappa
  `convertitore-ruolini` a `192.168.20.22`.
- Sui client (192.168.10.73/.74/.75): aggiungere riga in `/etc/hosts` oppure configurare
  il DNS locale in modo che `convertitore-ruolini` si risolva a `192.168.20.22`.
- `IntraPanel/frontend/.env`: aggiornare `REACT_APP_REPORT_API` e `REACT_APP_CERT_API` da
  `http://192.168.20.22:5000` a `http://convertitore-ruolini` (se si usa la porta 80) o
  `http://convertitore-ruolini:5000` (se si mantiene la porta 5000).
- Eventuale riconfigurazione della porta se si decide di far girare Flask su 80 (richiede
  root o authbind) o di mettere Nginx davanti.
- Rebuild React dopo modifica al `.env`.

## Checklist di completamento

- [ ] Strategia hostname scelta (DNS locale vs `/etc/hosts` su ogni client)
- [ ] Record DNS o voce hosts aggiunta
- [ ] `.env` aggiornato con il nuovo hostname
- [ ] `npm run build` eseguito
- [ ] Accesso verificato da tutti e tre i client con `http://convertitore-ruolini`

## Domande aperte

Porta finale: si mantiene `:5000` nell'URL o si passa alla porta 80? Porta 80 richiede
privilegi root o un reverse proxy; porta 5000 è più semplice ma l'URL rimane con il numero
di porta esplicito.

## Fasi successive (in ordine)

1. Hostname LAN (questa feature)
2. Refactoring architettura Flask+React (separazione API da frontend, variabili d'ambiente,
   struttura directory)
3. Ottimizzazione VM Proxmox (disabilitazione servizi, riduzione RAM/CPU)
