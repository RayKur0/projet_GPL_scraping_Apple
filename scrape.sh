#!/bin/bash
# Script pour scraper le cours de XRP depuis eToro

# URL de la page eToro pour XRP
URL="https://www.etoro.com/fr/markets/xrp"

# Récupérer le contenu HTML de la page sans spécifier de User-Agent
HTML=$(curl -s "$URL")

# Extraction du prix en ciblant le span avec la classe "instrument-price et-font-3xl"
# On capture le nombre situé entre le début du span et le tag de fermeture </span>
PRICE=$(echo "$HTML" | grep -oP 'class="instrument-price et-font-3xl">\s*\K[0-9.]+(?=\s*</span>)' | head -1)

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
