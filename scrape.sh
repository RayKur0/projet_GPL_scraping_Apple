#!/bin/bash
# Script pour scraper le cours de XRP depuis eToro

# URL de la page eToro pour XRP
URL="https://www.etoro.com/fr/markets/xrp"

# Récupérer le contenu HTML de la page
HTML=$(curl -s "$URL")

# Tenter d'extraire le prix pour le cas "positive"
PRICE_POS=$(echo "$HTML" | grep -oP 'instrument-price et-font-3xl positive">\s*\K[0-9.]+(?=\s*<)')

# Tenter d'extraire le prix pour le cas "negative"
PRICE_NEG=$(echo "$HTML" | grep -oP 'instrument-price et-font-3xl negative">\s*\K[0-9.]+(?=\s*<)')

# Tenter d'extraire le prix pour le cas sans suffixe
PRICE_NORMAL=$(echo "$HTML" | grep -oP 'instrument-price et-font-3xl">\s*\K[0-9.]+(?=\s*<)')

# Vérifier lequel des trois a retourné une valeur
if [ -n "$PRICE_POS" ]; then
    PRICE="$PRICE_POS"
elif [ -n "$PRICE_NEG" ]; then
    PRICE="$PRICE_NEG"
elif [ -n "$PRICE_NORMAL" ]; then
    PRICE="$PRICE_NORMAL"
else
    echo "Erreur : Impossible d'extraire le prix. Vérifiez la regex et la structure HTML."
    exit 1
fi

# Obtenir le timestamp courant
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Enregistrer la donnée dans data.txt au format CSV (timestamp,price)
echo "$TIMESTAMP,\$$PRICE" >> data.txt

# Afficher le résultat
echo "[$TIMESTAMP] Prix XRP: \$$PRICE"
