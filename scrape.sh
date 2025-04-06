#!/bin/bash
# Script pour scraper le cours de XRP depuis eToro

# URL de la page eToro pour XRP
URL="https://www.etoro.com/fr/markets/xrp"

# Récupérer le contenu HTML de la page
HTML=$(curl -s "$URL")

# Tenter d'extraire le prix pour les trois cas possibles
# On recherche l'attribut automation-id et la classe instrument-price et-font-3xl, avec éventuellement " negative" ou " positive"
PRICE=$(echo "$HTML" | grep -oP 'automation-id="market-page-mobile-header-stats-value"\s+class="instrument-price et-font-3xl(?: negative| positive)?">\s*\K[0-9.]+(?=\s*</span>)' | head -1)

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
