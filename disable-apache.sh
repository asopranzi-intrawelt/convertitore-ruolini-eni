#!/bin/bash
systemctl stop apache2
systemctl disable apache2
systemctl restart nginx
echo "Apache2 disabilitato, nginx riavviato."
