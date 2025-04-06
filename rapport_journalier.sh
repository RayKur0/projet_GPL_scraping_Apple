#!/bin/bash
# Script pour générer le rapport quotidien pour AAPL

# Définir la date du jour
TODAY=$(date '+%Y-%m-%d')

# Extraire les données du jour depuis data.txt
grep "^$TODAY" data.txt > today_data.txt

# Vérifier que today_data.txt contient des données
if [ ! -s today_data.txt ]; then
    echo "Aucune donnée pour aujourd'hui."
    exit 1
fi

# Récupérer le prix d'ouverture (première valeur) et de clôture (dernière valeur)
OPEN=$(head -1 today_data.txt | cut -d',' -f2)
CLOSE=$(tail -1 today_data.txt | cut -d',' -f2)

# Calculer le changement en valeur et en pourcentage
CHANGE=$(echo "$CLOSE - $OPEN" | bc -l)
PERCENT_CHANGE=$(echo "scale=2; ($CHANGE / $OPEN) * 100" | bc -l)

# Calculer la moyenne et la volatilité (écart-type) en utilisant awk
read AVG STD < <(awk -F, '{
    sum+=$2; sumsq+=$2*$2; count++
} END {
    if (count > 0) {
        avg = sum/count;
        variance = (sumsq - (sum*sum)/count)/count;
        if (variance < 0) variance=0;
        std = sqrt(variance);
        printf "%.3f %.3f", avg, std;
    }
}' today_data.txt)

# Le rendement journalier est le pourcentage de changement
DAILY_RETURN=$PERCENT_CHANGE

# Formatage du rapport avec les emojis demandés
REPORT="Daily Report - 20h
📅 Date: $TODAY

🟢 Open Price: $OPEN \$

🔴 Close Price: $CLOSE \$

📈 Change: $CHANGE \$ ($PERCENT_CHANGE%)

📊 Volatility: $STD

📉 Average Price: $AVG \$

💹 Daily Return: $DAILY_RETURN%
"

# Enregistrer le rapport dans daily_report.txt et l'afficher
echo "$REPORT" > daily_report.txt
echo "$REPORT"
