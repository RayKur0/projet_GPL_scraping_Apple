#!/bin/bash
# Script pour générer le rapport journalier pour XRP en français

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

# Supprimer le symbole $ pour les calculs
OPEN_NUM=$(echo "$OPEN" | sed 's/\$//')
CLOSE_NUM=$(echo "$CLOSE" | sed 's/\$//')

# Calculer le prix maximum et minimum du jour
PRIX_MAX=$(awk -F, '{gsub(/\$/,"",$2); if($2+0>max) max=$2+0} END {print max}' today_data.txt)
PRIX_MIN=$(awk -F, '{gsub(/\$/,"",$2); if(min=="" || $2+0<min) min=$2+0} END {print min}' today_data.txt)

# Calculer la variation journalière en pourcentage : ((max - min)/min)*100
VARIATION=$(echo "scale=2; (($PRIX_MAX - $PRIX_MIN) / $PRIX_MIN) * 100" | bc -l)

# Calculer la moyenne et la volatilité (écart-type) avec awk
read AVG STD < <(awk -F, '{gsub(/\$/,"",$2); sum+=$2; sumsq+=$2*$2; count++} END {if(count>0){avg=sum/count; variance=(sumsq - (sum*sum)/count)/count; if(variance<0) variance=0; std=sqrt(variance); printf "%.3f %.3f", avg, std}}' today_data.txt)

# Calculer le rendement journalier en pourcentage : ((close - open)/open)*100
DAILY_RETURN=$(echo "scale=2; (($CLOSE_NUM - $OPEN_NUM) / $OPEN_NUM) * 100" | bc -l)

REPORT="Daily Report - 20h
📅 Date: $TODAY

🔼 Prix max du jour : \$$PRIX_MAX
🔽 Prix min du jour : \$$PRIX_MIN

📈 Variation journalière : $VARIATION %

📊 Volatility: $STD
📉 Average Price: \$$AVG
💹 Daily Return: $DAILY_RETURN %
"

# Enregistrer le rapport dans daily_report.txt et l'afficher
echo "$REPORT" > daily_report.txt
echo "$REPORT"
