#!/bin/bash
# Script pour scraper le cours de XRP depuis eToro

# URL de la page eToro pour XRP
URL="https://www.etoro.com/fr/markets/xrp"

# Récupérer le contenu HTML de la page sans user-agent personnalisé
HTML=$(curl -s "$URL")

# Extraction du prix :
# La regex cherche "instrument-price et-font-3xl" suivi éventuellement de " negative" ou " positive",
# puis le symbole ">" et capture les chiffres (avec éventuellement des points) avant le tag de fermeture </span>
PRICE=$(echo "$HTML" | grep -oP 'instrument-price et-font-3xl(?: negative| positive)?">\s*\K[0-9.]+(?=\s*</span>)' | head -1)

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
