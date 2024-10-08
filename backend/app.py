from flask import Flask, request, jsonify
from kafka import KafkaProducer
import json

app = Flask(__name__)

# Initialize Kafka Producer
producer = KafkaProducer(
    bootstrap_servers=['localhost:9092'],
    value_serializer=lambda v: json.dumps(v).encode('utf-8')
)

@app.route('/event', methods=['POST'])
def capture_event():
    event = request.get_json()
    if not event:
        return jsonify({'error': 'Invalid event data'}), 400
    
    # Send event to Kafka topic 'website-events'
    producer.send('website-events', value=event)
    producer.flush()
    
    return jsonify({'status': 'Event received'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
