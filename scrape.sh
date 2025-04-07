#!/bin/bash
# Script pour scraper le cours de XRP depuis crypto.com (version française)

# URL de la page crypto.com pour XRP (version FR)
URL="https://crypto.com/price/fr/xrp"

# Récupérer le contenu HTML de la page
HTML=$(curl -s "$URL")

# Extraction du prix en ciblant le span avec la classe "chakra-text css-13hqrwd"
RAW_PRICE=$(echo "$HTML" | grep -oP 'class="chakra-text css-13hqrwd">\s*\$\K[0-9]+(?:[,.][0-9]+)?' | head -1)

# Vérifier que le prix a été extrait
if [ -z "$RAW_PRICE" ]; then
    echo "Erreur : Impossible d'extraire le prix. Vérifiez la regex et la structure HTML."
    exit 1
fi

# Convertir une éventuelle virgule en point (exemple : 1,96 -> 1.96)
PRICE=$(echo "$RAW_PRICE" | sed 's/,/./')

# Obtenir le timestamp courant
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Enregistrer la donnée dans data.txt au format CSV (timestamp,price)
echo "$TIMESTAMP,\$$PRICE" >> data.txt

# Afficher le résultat pour vérification
echo "[$TIMESTAMP] Prix XRP: \$$PRICE"
