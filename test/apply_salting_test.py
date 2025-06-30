from Dags.tasks.spark.calculate_drone_flight_metrics import CalculateDroneFlightMetrics
from pyspark.sql import SparkSession
from pyspark.sql.functions import col
import unittest

class TestSaltingMethods(unittest.TestCase):
    def setUp(self):
        self.spark = SparkSession.builder \
            .appName("TestCalculateDroneFlightMetrics") \
            .master("local[*]") \
            .getOrCreate()
        self.processor = CalculateDroneFlightMetrics()

    def tearDown(self):
        self.spark.stop()

    def test_apply_salting_function(self):
        data = [("DRN001",) for _ in range(700)] + [("DRN002",) for _ in range(500)]
        df = self.spark.createDataFrame(data, ["drone_id"])

        salted_df = self.processor.apply_salting(df, seuil=634, n_salt=5)

        salts = salted_df.filter(col("drone_id") == "DRN001").select("salt").distinct().collect()
        self.assertGreater(len(salts), 1, "DRN001 should have multiple salt values")

        salts_drn002 = salted_df.filter(col("drone_id") == "DRN002").select("salt").distinct().collect()
        self.assertEqual(len(salts_drn002), 1, "DRN002 should have only one salt value")
        self.assertEqual(salts_drn002[0]["salt"], 0, "DRN002's salt should be 0")

if __name__ == "__main__":
    unittest.main()
