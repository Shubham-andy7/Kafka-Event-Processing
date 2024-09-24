from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, LongType, FloatType, MapType

# Define the schema based on expected event data
schema = StructType() \
    .add("event_type", StringType()) \
    .add("details", MapType(StringType(), StringType())) \
    .add("timestamp", LongType())

# Create Spark session
spark = SparkSession.builder \
    .appName("WebsiteEventsStreaming") \
    .getOrCreate()

# Subscribe to Kafka topic
df = spark \
    .readStream \
    .format("kafka") \
    .option("kafka.bootstrap.servers", "localhost:9092") \
    .option("subscribe", "website-events") \
    .load()

# Convert the binary Kafka message to string and parse JSON
events = df.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*")

# Example Transformation: Count events by type
event_counts = events.groupBy("event_type").count()

# Write the counts to the console
query = event_counts.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

query.awaitTermination()
