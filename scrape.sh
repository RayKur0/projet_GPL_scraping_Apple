#!/bin/bash
# Script pour scraper le cours de XRP depuis Cryptoast

# URL de la page Cryptoast pour XRP
URL="https://cryptoast.fr/cours-xrp-52.html"

# Récupérer le contenu HTML de la page
HTML=$(curl -s "$URL")

# Extraire le prix en cherchant le texte après la classe "cours-price"
# Ajustez la regex si nécessaire en fonction de la structure réelle
PRICE=$(echo "$HTML" | grep -oP 'class="cours-price">\K[0-9.,]+' | head -1)

# Obtenir le timestamp courant
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Enregistrer la donnée dans data.txt (format CSV : timestamp,price)
echo "$TIMESTAMP,\$$PRICE" >> data.txt

# Afficher le résultat
echo "[$TIMESTAMP] Prix XRP: \$$PRICE"
