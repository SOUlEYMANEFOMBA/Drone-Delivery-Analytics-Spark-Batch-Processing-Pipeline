import logging
from pyspark.sql import SparkSession

class BigQueyConnectionTask:
    """_summary_
    
    """
    def create_spark_connection(self):
        """
        Création d'une session Spark avec connexion à BigQuery
        """
        logging.info("Beginning of Spark connection to BigQuery...")

        spark_connect = None
        try:
            # SparkSession avec le connecteur BigQuery
            spark_connect = SparkSession.builder \
                .appName("KafkaToBigQuery") \
                .master('local[*]') \
                .config("spark.jars", "/opt/libs/spark-bigquery-with-dependencies_2.12-0.32.2.jar,/opt/libs/gcs-connector-hadoop3-latest.jar")\
                .config("spark.hadoop.google.cloud.auth.service.account.enable", "true") \
                .config("spark.hadoop.google.cloud.auth.service.account.json.keyfile", "/opt/keys/real-time-traffic-pipeline-30d152e38926.json") \
                .config("spark.hadoop.fs.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFileSystem") \
                .config("spark.hadoop.fs.AbstractFileSystem.gs.impl", "com.google.cloud.hadoop.fs.gcs.GoogleHadoopFS") \
                .getOrCreate()
            
            spark_connect.sparkContext.setLogLevel("ERROR")
            logging.info("Spark session created successfully.")
        
        except Exception as e:
            logging.error(f"Couldn't create the Spark session due to exception: {e}")
        
        return spark_connect
