#!/bin/bash
# URL de Google Finance pour Apple (AAPL)
URL="https://www.google.com/finance/quote/AAPL:NASDAQ"

# Récupérer le contenu HTML de la page (sans user-agent personnalisé)
HTML=$(curl -s "$URL")

# Extraire le prix en cherchant le texte après la classe "YMlKec fxKbKc"
PRICE=$(echo "$HTML" | grep -o 'class="YMlKec fxKbKc">[^<]*' | head -1 | sed 's/.*">//')

# Obtenir le timestamp courant
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Sauvegarder les données dans data.txt au format CSV
echo "$TIMESTAMP,$PRICE" >> data.txt

# Afficher le résultat
echo "[$TIMESTAMP] Prix AAPL: $PRICE"

