#!/bin/bash
# Script pour scraper le cours de XRP depuis crypto.com

# URL de la page de cours de XRP sur crypto.com
URL="https://crypto.com/price/xrp"

# Récupérer le contenu HTML de la page (sans spécifier de User-Agent)
HTML=$(curl -s "$URL")

# Extraction du prix en ciblant le span avec la classe "chakra-text css-13hqrwd"
# Exemple d'extrait HTML : <span class="chakra-text css-13hqrwd">$1,97 USD</span>
RAW_PRICE=$(echo "$HTML" | grep -oP 'class="chakra-text css-13hqrwd">\K\$[0-9,]+\s?USD' | head -1)

# Vérifier que le prix a été extrait
if [ -z "$RAW_PRICE" ]; then
    echo "Erreur : Impossible d'extraire le prix. Vérifiez la regex et la structure HTML."
    exit 1
fi

# Nettoyer le prix : retirer le '$' et ' USD', et convertir la virgule en point
PRICE=$(echo "$RAW_PRICE" | sed -E 's/\$//; s/ ?USD//; s/,/./')

# Obtenir le timestamp courant
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Enregistrer la donnée dans data.txt au format CSV (timestamp,price)
echo "$TIMESTAMP,\$$PRICE" >> data.txt

# Afficher le résultat pour vérification
echo "[$TIMESTAMP] Prix XRP: \$$PRICE"
