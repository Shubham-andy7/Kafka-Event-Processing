from pyspark.sql import SparkSession
from pyspark.sql.functions import from_json, col
from pyspark.sql.types import StructType, StringType, LongType, FloatType, MapType
from pymongo import MongoClient
from pyspark.sql.streaming import StreamingQueryException

# MongoDB Setup
mongo_client = MongoClient("mongodb+srv://cantonicatech:cantodb2023@cluster0.hpbqw.mongodb.net/")  # Using MongoDB hostname as defined in docker-compose.yml
# mongodb+srv://cantonicatech:cantodb2023@cluster0.hpbqw.mongodb.net/cantonicastag
db = mongo_client['event_logs_db']
collection = db['logs']

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
    .option("kafka.bootstrap.servers", "kafka:9092") \
    .option("subscribe", "website-events") \
    .load()

# Convert the binary Kafka message to string and parse JSON
events = df.selectExpr("CAST(value AS STRING) as json") \
    .select(from_json(col("json"), schema).alias("data")) \
    .select("data.*")

# Example Transformation: Count events by type
event_counts = events.groupBy("event_type").count()

# Write the counts to the console
query_console = event_counts.writeStream \
    .outputMode("complete") \
    .format("console") \
    .start()

# Function to insert logs into MongoDB
def write_to_mongo(row):
    try:
        event_log = {
            "event_type": row['event_type'],
            "details": row['details'],
            "timestamp": row['timestamp']
        }
        collection.insert_one(event_log)
    except Exception as e:
        print(f"Error inserting row into MongoDB: {e}")

# Write the processed stream to MongoDB
query_mongo = events.writeStream \
    .foreach(write_to_mongo) \
    .start()

# Await termination of both streams
try:
    query_console.awaitTermination()
    query_mongo.awaitTermination()
except StreamingQueryException as e:
    print(f"Streaming query failed: {e}")
