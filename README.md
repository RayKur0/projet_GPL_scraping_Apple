# projet_GPL_scraping_Apple

Ce projet a pour objectif de scraper en continu le prix de la crypto XRP depuis Cryptoast et de générer un rapport quotidien détaillé. Le dashboard permet de suivre en temps réel le cours de XRP, d'afficher la dernière mise à jour, un graphique d'évolution et les rapports journaliers.

## Fonctionnalités

- **Présentation :**  
  Un onglet dédié qui présente le projet, ses objectifs et sa méthodologie (scraping et génération de rapports).

- **Dashboard :**  
  - Affiche le prix actuel de XRP et la date/heure de la dernière mise à jour.
  - Affiche un graphique illustrant l'évolution du cours à partir des données enregistrées dans `data.txt`.
  - Affiche le rapport quotidien généré (extrait de `daily_report.txt`).

- **Actualisation :**  
  Le dashboard se met à jour automatiquement toutes les 5 minutes et le rapport quotidien est généré chaque jour à 20h via une tâche cron.
