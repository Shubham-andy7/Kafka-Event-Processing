from kafka import KafkaConsumer
import json

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    'website-events',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='earliest',
    enable_auto_commit=True,
    group_id='website-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

if __name__ == "__main__":
    print("Starting Kafka Consumer...")
    for message in consumer:
        event = message.value
        print(f"Received event: {event}")
        # Add processing logic here
        # For example, send to a database or trigger analytics
