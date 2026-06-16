# Snapshot di sincronizzazione

> Da leggere per primo a inizio sessione. Fotografa lo stato del progetto al commit di
> riferimento e mappa ogni scheda al suo stato di verifica. È la fonte di verità su cosa è fatto,
> non le spunte del diario.

## Stato

```
Branch attivo:         main
Commit di riferimento: 0516741
Data snapshot:         2026-06-16
```

## Stato di verifica delle schede

| Scheda | last-verified | Stato |
|---|---|---|
| STACK.md | 2da37cf | stale (Flask ora solo-API, nginx serve la build, cache Odoo) |
| design-and-security.md | 2da37cf | stale (IP restriction su nginx, build in /var/www) |
| deployment.md | 0516741 | aggiornata (architettura post-cutover + separazione test/prod) |
| dev-testing.md | 0516741 | aggiornata (worktree develop + test locale) |
| current-work.md | 0516741 | aggiornata |
| roadmap.md | 2da37cf | da rivedere (Fase 2 refactoring completata) |

## Punto di ripresa

Refactoring completato e in produzione (cutover al commit `0516741`, verificato da client LAN
.73). Architettura attuale: nginx su porta 80 serve la build statica da `/var/www/convertitore-ruolini`
ai tre IP autorizzati e inoltra le sole rotte API a Flask `127.0.0.1:5000`, che è solo-API
(`/` risponde 404). nginx ha `proxy_read_timeout 600s` su `/save`. Frontend con URL API relativo
(una build per locale e LAN). Backend con sessione XML-RPC in cache (conversione ~121s invece di
~295s). Bug Odoo del 12/06 risolto (XmlRpc non azzera più l'URL letto dal .env).

Separazione ambienti adottata: produzione = `main` nella cartella principale + deploy LAN;
sviluppo = worktree `develop` in `convertitore-ruolini-eni-dev` con test locale su porte dedicate;
baseline vergine = `eni-report+intrapanelUI` (backend 5050, frontend 3000). Dettaglio in
`deployment.md` e `dev-testing.md`.

Prossimo (task #4): uniformare l'utente Odoo ad `asopranzi@intrawelt.com` su tutti i track; in
particolare la copia vergine ha `gmandolesi@intrawelt.com` cablato nel sorgente. Aperti: voce
/etc/hosts su .75; sync di STACK.md e design-and-security.md alla nuova architettura; eventuale
rimozione di `IntraPanel/backend/` e pulizia componente Certificazioni.
