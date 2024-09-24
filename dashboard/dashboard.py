from flask import Flask, render_template
from flask_socketio import SocketIO, emit
from kafka import KafkaConsumer
import json
import threading

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

# Initialize Kafka Consumer
consumer = KafkaConsumer(
    'website-events',
    bootstrap_servers=['localhost:9092'],
    auto_offset_reset='latest',
    enable_auto_commit=True,
    group_id='dashboard-group',
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))
)

def consume_events():
    for message in consumer:
        event = message.value
        socketio.emit('new_event', event)

@app.route('/')
def index():
    return render_template('dashboard.html')

if __name__ == '__main__':
    # Start Kafka consumer in a separate thread
    thread = threading.Thread(target=consume_events)
    thread.daemon = True
    thread.start()
    socketio.run(app, host='0.0.0.0', port=5001)
