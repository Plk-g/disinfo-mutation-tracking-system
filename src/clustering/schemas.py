from pyspark.sql.types import (
    StructType,
    StructField,
    StringType,
    IntegerType,
    DoubleType,
    ArrayType,
)

# Input embedding schema (what clustering expects)
EMBEDDING_SCHEMA = StructType([
    StructField("id", StringType(), False),
    StructField("epoch", IntegerType(), False),
    StructField("vector", ArrayType(DoubleType()), False),
])

# Output cluster assignment
CLUSTER_SCHEMA = StructType([
    StructField("id", StringType(), False),
    StructField("epoch", IntegerType(), False),
    StructField("cluster_id", IntegerType(), False),
])

# Drift event output (what backend + viz will consume)
DRIFT_EVENT_SCHEMA = StructType([
    StructField("epoch", IntegerType(), False),
    StructField("cluster_id", IntegerType(), False),
    StructField("drift_score", DoubleType(), False),
    StructField("event_type", StringType(), False),
])
