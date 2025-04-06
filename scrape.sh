#!/bin/bash
# Script pour scraper le cours de XRP depuis eToro

# URL de la page eToro pour XRP
URL="https://www.etoro.com/fr/markets/xrp"

# Récupérer le contenu HTML de la page
HTML=$(curl -s "$URL")

# Extraction du prix en ciblant la classe variant
# La regex ci-dessous capture le nombre après "instrument-price et-font-3xl"
# avec éventuellement " positive" ou " negative" dans la classe
PRICE=$(echo "$HTML" | grep -oP 'instrument-price et-font-3xl(?: positive| negative)?">\s*\K[0-9.]+(?=\s*<)' | head -1)

# Vérifier que le prix a bien été extrait
if [ -z "$PRICE" ]; then
    echo "Erreur : Impossible d'extraire le prix. Vérifiez la regex et la structure HTML."
    exit 1
fi

# Obtenir le timestamp courant
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Enregistrer la donnée dans data.txt au format CSV (timestamp,price)
echo "$TIMESTAMP,\$$PRICE" >> data.txt

# Afficher le résultat pour vérification
echo "[$TIMESTAMP] Prix XRP: \$$PRICE"
