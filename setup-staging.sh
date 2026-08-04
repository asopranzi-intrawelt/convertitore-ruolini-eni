#!/bin/bash
# Deploy dell'ambiente di STAGING (branch develop) in LAN, parallelo alla produzione.
# Staging = nginx porta 8090 -> build di develop in /var/www/convertitore-ruolini-test,
#           con dietro il Flask di staging su 127.0.0.1:5010 (service intrapanel-staging).
# Non tocca la produzione (porta 80, /var/www/convertitore-ruolini, Flask 5000).
# Va eseguito come root (sudo bash setup-staging.sh) dalla cartella del worktree develop.
set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
BUILD_SRC="$REPO_DIR/IntraPanel/frontend/build"
WWW_DST="/var/www/convertitore-ruolini-test"

# 1. pubblica la build di staging in una cartella separata, leggibile da www-data
rm -rf "$WWW_DST"
mkdir -p "$WWW_DST"
cp -r "$BUILD_SRC"/. "$WWW_DST"/
chown -R www-data:www-data "$WWW_DST"

# 2. installa il server block di staging (porta 8090) dalla fonte nginx-staging.conf
cp "$REPO_DIR/nginx-staging.conf" /etc/nginx/sites-available/convertitore-ruolini-staging
ln -sf /etc/nginx/sites-available/convertitore-ruolini-staging /etc/nginx/sites-enabled/convertitore-ruolini-staging

# 3. valida e ricarica senza interrompere la produzione
nginx -t && systemctl reload nginx
echo "staging OK. Build pubblicata in $WWW_DST, servita su porta 8090."
