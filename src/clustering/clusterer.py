from pyspark.sql import functions as F
from pyspark.sql.types import IntegerType
from pyspark.ml.clustering import KMeans
from pyspark.ml.linalg import Vectors, VectorUDT

class EmbeddingClusterer:
    def __init__(self, k=8, seed=42):
        self.k = k
        self.seed = seed

    def cluster(self, df):
        """
        Expects df with columns: id, epoch, vector (array<double>)
        Returns df with cluster_id
        """

        to_vec = F.udf(lambda x: Vectors.dense(x), VectorUDT())

        df_vec = df.withColumn("features", to_vec("vector"))

        model = KMeans(
            k=self.k,
            seed=self.seed,
            featuresCol="features"
        ).fit(df_vec)

        return model.transform(df_vec).select(
            "id",
            "epoch",
            F.col("prediction").cast(IntegerType()).alias("cluster_id"),
            "vector"
        )
