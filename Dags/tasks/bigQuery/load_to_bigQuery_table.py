import logging
import os

class LoadBigQueryTable:
    """
    Classe permettant de charger un DataFrame Spark structuré en continu dans une table BigQuery.

    Attributs :
        project_id (str) : ID du projet GCP.
        dataset (str) : Nom du dataset BigQuery.
        checkpoint_base_path (str) : Chemin de base pour stocker les checkpoints Spark.
    """

    def __init__(
        self,
        project_id: str = "real-time-traffic-pipeline",
        dataset: str = "Drone_delivery_data",
        checkpoint_base_path: str = "/tmp/checkpoints_bigquery"
    ):
        self.project_id = project_id
        self.dataset = dataset
        self.checkpoint_base_path = checkpoint_base_path

    def load_to_bigquery_table(self, table_name: str, df_parsed):
        """
        Charge un DataFrame Spark structuré (streaming) dans une table BigQuery.

        Args:
            table_name (str): Nom de la table BigQuery cible.
            df_parsed (DataFrame): DataFrame Spark structuré prêt à être envoyé.
        """
        try:
            print(f"this is projetc id '{self.project_id}'...")
            checkpoint_path = os.path.join(self.checkpoint_base_path, table_name)
            full_table_name = f"{self.project_id}:{self.dataset}.{table_name}"
            ##load dans bigquery ma table
            df_parsed.write\
                .format("bigquery") \
                .option("table", full_table_name) \
                .option("parentProject", self.project_id) \
                .option("temporaryGcsBucket", "real-time-drone-bucket") \
                .option("checkpointLocation", checkpoint_path) \
                .mode("append") \
                .save()

            logging.info(f"Data loaded successfully to BigQuery table '{full_table_name}'.")

        except Exception as e:
            logging.error(f"Failed to load data to BigQuery table '{table_name}' due to: {e}")
