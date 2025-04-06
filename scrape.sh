#!/bin/bash
# Script pour scraper le cours de XRP depuis Kriptomat

# URL de la page de cours de XRP sur Kriptomat
URL="https://kriptomat.io/fr/cours-crypto-monnaies/xrp-valeur/"

# Récupérer le contenu HTML de la page en simulant un navigateur
HTML=$(curl -s -A "Mozilla/5.0" "$URL")

# Extraction du prix en ciblant la div contenant la classe "asset-price"
PRICE=$(echo "$HTML" | grep -oP 'class="ts-3xl tw-bolder asset-price">\K[0-9.]+(?=<)' | head -1)

# Vérifier que le prix a été extrait
if [ -z "$PRICE" ]; then
    echo "Erreur : Impossible d'extraire le prix. Vérifiez la regex et la structure HTML."
    exit 1
fi

# Obtenir le timestamp courant
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

# Enregistrer la donnée dans data.txt au format CSV (timestamp,price)
echo "$TIMESTAMP,\$$PRICE" >> data.txt

# Afficher le résultat
echo "[$TIMESTAMP] Prix XRP: \$$PRICE"
