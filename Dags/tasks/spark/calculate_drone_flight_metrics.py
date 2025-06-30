import logging
from pyspark.sql import SparkSession
from pyspark.sql.window import Window

from pyspark.sql.functions import col, avg,lag, unix_timestamp, when,sum as spark_sum, min, max, first, last, radians, sin, cos, atan2, sqrt,lit, rand

class CalculateDroneFlightMetrics:
    """
    Classe pour gérer les tâches de traitement Spark avec des scripts Bash.
    
    pour calculer les métriques de vol des drones à partir des données brutes.
    
    Cette classe lit un fichier CSV contenant les journaux de vol des drones,
    
    calcule les métriques de vol telles que la durée du vol, la consommation de batterie et la distance parcourue,
    
    et retourne un DataFrame avec les résultats agrégés par drone.
    
    Attributs:
        input_csv_path (str): Chemin du fichier CSV d'entrée contenant les journaux de vol des drones.
    Méthodes: 
        calculate_drone_flight_metrics(spark_session):
            Calcule les métriques de vol des drones à partir des données brutes.    
            
    """

    def __init__(self, input_csv_path: str = "/opt/airflow/dags/data/drone_flight_logs_large.csv"):  
        self.input_csv_path = input_csv_path

    
    def calculate_drone_flight_metrics(self, spark_session):
        """
        Calcule les métriques de vol des drones à partir des données brutes.
        """
        try:
            logging.info("Starting calculation of drone flight metrics...")
            ## Pour calculer le temps de vol de chaques drone on a besion du debut de vol et de la fin de son vol entre deux status in_flight succesive 
            ## distance est calculée comme la somme des différences entre les latitudes et longitudes de début et de fin
            ## la consommation est calculée en multipliant le temps de vol par le taux de consommation de la batterie
            ##la vitesse moyenne est calculée comme la distance divisée par le temps de vol
            # Chargement des données
            logging.info(f"Loading data from {self.input_csv_path}...")
            # Chargement

            df=spark_session.read\
                            .option("mergeSchema", "true")\
                            .option("header", "true")\
                            .parquet(self.input_csv_path)
        

            # Filtrage
            df = df.filter(col("status") == "in_flight")
            
            ##application du salting pour les drones sur-représentés
            df= self.apply_salting(df, seuil=634, n_salt=5)
            

            # 5. Repartition explicite AVANT groupBy
            df = df.repartition("drone_id", "salt")
            
           
            windowSpec = Window.partitionBy("drone_id").orderBy("timestamp")
            df = df.withColumn("previous_ts", lag("timestamp").over(windowSpec))
            df = df.withColumn("time_diff", unix_timestamp("timestamp") - unix_timestamp("previous_ts"))

            # Détection des coupures de vol
            df = df.withColumn("segment_break", when(col("time_diff") > 30, 1).otherwise(0))
            df = df.withColumn("flight_id", spark_sum("segment_break").over(windowSpec.rowsBetween(Window.unboundedPreceding, 0)))


            # Agrégation des vols
            df_segments = df.groupBy("drone_id","salt", "flight_id").agg(
                min("timestamp").alias("start_time"),
                max("timestamp").alias("end_time"),
                first("latitude").alias("start_lat"),
                first("longitude").alias("start_lon"),
                last("latitude").alias("end_lat"),
                last("longitude").alias("end_lon"),
                first("battery_level").alias("start_battery"),
                last("battery_level").alias("end_battery")
            )
            
            ## function to calculate distance
            # haversine_udf = udf(lambda lat1, lon1, lat2, lon2: self.__haversine_distance(lat1, lon1, lat2, lon2), returnType="double")
            
            R = 6371.0  # rayon de la Terre en km

            df_segments = df_segments.withColumn("dlat", radians(col("end_lat") - col("start_lat")))\
                                    .withColumn("dlon", radians(col("end_lon") - col("start_lon")))\
                                    .withColumn("a", sin(col("dlat") / 2) ** 2 + 
                                                    cos(radians(col("start_lat"))) * 
                                                    cos(radians(col("end_lat"))) * 
                                                    sin(col("dlon") / 2) ** 2)\
                                    .withColumn("c", 2 * atan2(sqrt(col("a")), sqrt(1 - col("a"))))\
                                    .withColumn("distance", lit(R) * col("c"))
            
            # #calcul du temps moyen de chaque drone en vol et de la consomation de la batterie
            df_final_segments = df_segments.withColumn("flight_duration", unix_timestamp("end_time") - unix_timestamp("start_time"))\
                    .withColumn("battery_consumption", col("start_battery") - col("end_battery"))\
                    .groupBy("drone_id")\
                    .agg(
                        avg("flight_duration").alias("avg_flight_duration"),
                        avg("battery_consumption").alias("avg_battery_consumption"),
                        avg("distance").alias("avg_distance")
                       )\
                    .withColumn("avg_speed", col("avg_distance") / (col("avg_flight_duration") / 3600))  # en km/h
            
            return df_final_segments
        except Exception as e:
            logging.error(f"Error calculating drone flight metrics: {e}")
            logging.exception("Error calculating drone flight metrics")
    
    def apply_salting(self, df, seuil: int = 634, n_salt: int = 5):
        #calcul du volume par drone (les drones sur-représentés )
        df_count = df.groupBy("drone_id").count()
        df_hot = df_count.filter(col("count") > seuil).select("drone_id")

        df = df.join(df_hot.withColumn("needs_salt", lit(1)), on="drone_id", how="left")

        df = df.withColumn(
            "salt",
            when(col("needs_salt") == 1, (rand() * n_salt).cast("int")).otherwise(lit(0))
        )

        return df
