import os
import requests
import logging
import json
from dotenv import load_dotenv
from datetime import datetime, timezone
##je charge les fichiers d'environement

from Dags.tasks.spark.spark_create_dataframe_task import SparkCreateDataFrameTask
from Dags.tasks.bigQuery.create_bigquery_connection_task import BigQueyConnectionTask
from Dags.tasks.bigQuery.load_to_bigQuery_table import LoadBigQueryTable
from Dags.tasks.spark.calculate_drone_flight_metrics import CalculateDroneFlightMetrics


load_dotenv()

# Chargement des configs
TOMTOM_API_KEY = os.getenv("TOMTOM_API_KEY")


# Fonction pour récupérer les incidents
def fetch_traffic_incidents():
    print("on commence")
    logging.basicConfig(level=logging.INFO)
    logging.info("Début du pipeline de récupération des incidents")
    spark_connect=BigQueyConnectionTask().create_spark_connection()
    logging.info("Connexion Spark créée")
    spark_sesion=CalculateDroneFlightMetrics("/workspace/Dags/data/drone_flight_logs_large.parquet")
    df=spark_sesion.calculate_drone_flight_metrics(spark_connect)
    logging.info("Calcul des métriques de vol de drone terminé")
    df.show(5)
    logging.info("Chargement des données dans BigQuery")
    load_bigquery=LoadBigQueryTable()
    load_bigquery.load_to_bigquery_table("drone_flight_metrics", df)
    logging.info("Données chargées dans BigQuery avec succès")


if __name__=="__main__":
    fetch_traffic_incidents()