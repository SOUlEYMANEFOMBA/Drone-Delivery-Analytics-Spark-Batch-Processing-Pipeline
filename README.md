# 📦 Drone Delivery Analytics – Spark Batch Processing Pipeline

## 🧭 Contexte

Dans le cadre de la gestion d'une flotte de drones de livraison, il est crucial d’analyser les journaux de vol pour détecter des anomalies, optimiser les performances, surveiller la consommation énergétique, et garantir la fiabilité des trajets. Les drones envoient périodiquement (toutes les 30 secondes) des logs comprenant leur position, état de batterie, charge transportée et statut opérationnel.

---
## 🎯 Contexte du problème
Le système collecte un volume important de données en continu. Or, les traitements analytiques classiques deviennent coûteux et lents à mesure que la volumétrie augmente.
Ton job Spark lit 1,5 To de données GPS sur 7 jours pour calculer des statistiques de vol par drone (distance, vitesse, consommation, etc.).
Mais :

- 🐌 Il est très lent (> 2h)

- 🔄 Il fait beaucoup de shuffle

- ⚠️ Les CPU sont déséquilibrées entre les workers

Deux principaux défis techniques sont identifiés :

- Le **skew de données** causé par des drones plus actifs que d'autres, générant des déséquilibres de partitionnement.

- Le besoin d'une **architecture scalable et performante** pour calculer les indicateurs clés comme :
  - Durée moyenne de vol
  - Distance moyenne parcourue
  - Vitesse moyenne
  - Consommation moyenne de batterie

---
## 🔧 Tech Stack

| Stage                      | Technology                          |
|---------------------------|--------------------------------------|
| Data Ingestion            | fichier csv|
| Data Processing           | Apache Spark                         |
| Storage                   | Google BigQuery                      |
| Data Transformation       | dbt Cloud                            |
| Data Visualization        | Looker Studio (or Power BI)          |
| Orchestration             | Apache Airflow (Dockerized)          |
| Containerization          | Docker + Docker Compose              |

---


## 🛠️ Méthodologie et Architecture

### 🔁 Pipeline de Traitement

1. **Chargement des logs** (au format Parquet pour optimiser la lecture).
2. **Filtrage des statuts `in_flight`**.
3. **Identification des vols distincts** (séparation par intervalle de 30s ou plus).
4. **Calculs par vol** :
   - Temps de vol
   - Distance (formule de Haversine)
   - Batterie consommée
5. **Agrégation par drone** :
   - Moyennes globales des indicateurs

### ⚖️ Gestion du Skew (Salting)

Pour éviter que Spark n’exécute des tâches déséquilibrées à cause de drones très présents :
- Un seuil est défini (ex : 634 logs)
- Les drones dépassant ce seuil sont "saltés" via une colonne aléatoire
- Le `repartition` se fait ensuite sur `drone_id` + `salt` pour équilibrer le traitement entre workers

### 💡 Optimisations appliquées

- **Format Parquet** pour accélérer les I/O
- **Window Functions** pour détecter les segments de vol
- **Calculs vectoriels** (radians, sin, cos) directement dans Spark SQL
- **Utilisation de UDFs évitée** pour maximiser le parallélisme natif Spark
- **Repartition stratégique** avant les `groupBy`

---

## 📈 Résultats obtenus

- ✅ Calcul correct et rapide des métriques clés sur un dataset volumineux
- ✅ Bonne scalabilité observée grâce au format parquet et au salting
- ✅ Pipeline entièrement écrit en **PySpark** avec une approche modulaire (class-based)
- ✅ Tests unitaires mis en place sur le salting pour valider la logique
- ✅ Une table BigQuery contenant les **statistiques de vol moyennes par drone** :
  - `avg_flight_duration` (secondes),
  - `avg_battery_consumption` (%),
  - `avg_distance` (km),
  - `avg_speed` (km/h).

---

## 📤 Étapes suivantes (non implémentées dans ce repo)

- Intégration avec **Apache Airflow** pour l’orchestration
- Surveillance des métriques via un tableau de bord (Grafana, Looker, PowerBI...)

---

## 📁 Arborescence du projet

```bash
.
├── .devcontainer/
│   └── decontainer.json
    └── docker-compose.yml  
├── dags/
│   └── tasks/
        └── BigQuery/
│           └── create_bigquery_connection_task.py
            └── load_to_bigquery_table_task.py
│       └── spark/
│           └── calculate_drone_flight_metrics.py
    ├── data/
│         └── drone_flight_logs_large.csv
├── keys/
│   └── real-time-traffic-pipeline-xxx.json
├── libs/
│   └── gcs-connector-hadoop3-latest.jar
    └── spark-bigquery-with-dependencies_2.12-0.32.2.jar
├── test/
│   └── apply_salting_test.py
├── README.md
