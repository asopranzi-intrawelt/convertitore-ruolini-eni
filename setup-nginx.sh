#!/bin/bash
# Deploy del frontend statico e del reverse proxy nginx.
# Va eseguito come root (sudo bash setup-nginx.sh) dalla cartella del repo.
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_SRC="$REPO_DIR/IntraPanel/frontend/build"
WWW_DST="/var/www/convertitore-ruolini"

# 1. pubblica la build dove nginx (www-data) puo leggerla, fuori dalla home
rm -rf "$WWW_DST"
mkdir -p "$WWW_DST"
cp -r "$BUILD_SRC"/. "$WWW_DST"/
chown -R www-data:www-data "$WWW_DST"

# 2. installa il server block dalla fonte unica nginx.conf
cp "$REPO_DIR/nginx.conf" /etc/nginx/sites-available/convertitore-ruolini
rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/convertitore-ruolini /etc/nginx/sites-enabled/convertitore-ruolini

# 3. valida la configurazione e ricarica senza interrompere le connessioni
nginx -t && systemctl reload nginx
echo "nginx OK. Build pubblicata in $WWW_DST"
