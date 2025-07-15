import os
from confluent_kafka import SerializingProducer
import simplejson as json
from datetime import datetime
from datetime import datetime, timedelta
import random
import uuid
import time

LONDON_COORDINATES = {
    "latitude": 51.5074,
    "longitude": -0.1278
}

BIRMINGHAM_COORDINATES = {
    "latitude": 52.4862,
    "longitude": -1.8904
}


LATITUDE_INCREMENT = (BIRMINGHAM_COORDINATES["latitude"] - LONDON_COORDINATES["latitude"]) / 100
LONGITUDE_INCREMENT = (BIRMINGHAM_COORDINATES["longitude"] - LONDON_COORDINATES["longitude"]) / 100

KAFKA_BOOTSTRAP_SERVERS = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
VEHICLE_TOPIC = os.getenv("VEHICLE_TOPIC", "vehicle_data")
GPS_TOPIC = os.getenv("GPS_TOPIC", "gps_data")
TRAFFIC_TOPIC = os.getenv("TRAFFIC_TOPIC", "traffic_data")
WEATHER_TOPIC = os.getenv("WEATHER_TOPIC", "weather_data")
EMERGENCY_TOPIC = os.getenv("EMERGENCY_TOPIC", "emergency_data")

random.seed(42)  # For reproducibility
start_time = datetime.now()
start_location = LONDON_COORDINATES.copy()

def get_next_time():
    global start_time
    start_time += timedelta(seconds=random.randint(30, 60))
    return start_time

def simulate_vehicle_movement():
    global start_location
    
    start_location["latitude"] += LATITUDE_INCREMENT
    start_location["longitude"] += LONGITUDE_INCREMENT

    # add the some randomness to the movement
    start_location["latitude"] += random.uniform(-0.0005, 0.0005)
    start_location["longitude"] += random.uniform(-0.0005, 0.0005)

    return start_location

def generate_vehicle_data(vehicle_id):
    location = simulate_vehicle_movement()
    return {
        'id': uuid.uuid4(),
        'device_id': vehicle_id,
        'timestamp': get_next_time().isoformat(),
        'location': (location["latitude"], location["longitude"]),
        'speed': random.randint(10, 40),
        'direction': 'North-East',
        'make': 'BMW',
        'model': 'X5',
        'year': 2024,
        'fuelType': 'Hybrid'
    }

def generate_gps_data(device_id, timestamp, vehicle_type='private'):
    return {
        'id': uuid.uuid4(),
        'device_id': device_id,
        'timestamp': timestamp,
        'speed': random.uniform(0, 40),
        'direction': 'North-East',
        'vechicleType': vehicle_type,
    }

def generate_traffic_camera_data(device_id, timestamp, location, camera_id):
    return {
        'id': uuid.uuid4(),
        'deviceIdd': device_id,
        'cameraId': camera_id,
        'location': location,
        'timestamp': timestamp,
        'snapshot': 'Base64EncodedString',
    }

def generate_weather_data(device_id, timestamp, location):
    return {
        'id': uuid.uuid4(),
        'device_id': device_id,
        'timestamp': timestamp,
        'location': location,
        'temperature': random.uniform(-5, 26),
        'weatherCondition': random.choice(['Sunny', 'Cloudy', 'Rainy', 'Snowy']),
        'precipitation': random.uniform(0, 25),
        'windSpeed': random.uniform(0, 100),
        'humidity': random.randint(0, 100),
        'aqi': random.randint(0, 500)
    }

def generate_emergency_incident_data(device_id, timestamp, location):
    return {
        'id': uuid.uuid4(),
        'device_id': device_id,
        'incident_id': uuid.uuid4(),
        'incidentType': random.choice(['Accident', 'Fire', 'Medical', 'Police', 'None']),
        'timestamp': timestamp,
        'location': location,
        'severity': random.choice(['Low', 'Medium', 'High']),
        'status': random.choice(['Active', 'Resolved']),
        'description': 'Emergency incident reported',
    }

def json_serializer(obj):
    if isinstance(obj, uuid.UUID):
        return str(obj)
    raise TypeError(f"Type {type(obj)} not JSON serializable")

def delivery_report(err, msg):
    if err is not None:
        print(f"Message delivery failed: {err}")
    else:
        print(f"Message delivered to {msg.topic()} [{msg.partition()}] at offset {msg.offset()}")

def produce_data_to_kafka(producer, topic, data):
    json_str = json.dumps(data, default=json_serializer)
    producer.produce(
        topic=topic,
        key=str(data['id']),
        value=json_str.encode('utf-8'),  # encode AFTER json.dumps
        on_delivery=delivery_report      # typo fix: on_delevery → on_delivery
    )
    producer.flush()

def simulate_journey(producer, device_id):
    while True:
        vehicle_data = generate_vehicle_data(device_id)
        gps_data = generate_gps_data(device_id, vehicle_data['timestamp'])
        traffic_camera_data = generate_traffic_camera_data(device_id, vehicle_data['timestamp'], vehicle_data['location'], f'Camera-{random.randint(1, 10)}')
        weather_data = generate_weather_data(device_id, vehicle_data['timestamp'], vehicle_data['location'])
        emergency_incident_data = generate_emergency_incident_data(device_id, vehicle_data['timestamp'], vehicle_data['location'])
        
        if (vehicle_data['location'][0] >= BIRMINGHAM_COORDINATES['latitude'] and
            vehicle_data['location'][1] <= BIRMINGHAM_COORDINATES['longitude']):
            print("Vehicle has reached Birmingham. Ending simulation...")
            break
        

        produce_data_to_kafka(producer, VEHICLE_TOPIC, vehicle_data)
        produce_data_to_kafka(producer, GPS_TOPIC, gps_data)
        produce_data_to_kafka(producer, TRAFFIC_TOPIC, traffic_camera_data)
        produce_data_to_kafka(producer, WEATHER_TOPIC, weather_data)
        produce_data_to_kafka(producer, EMERGENCY_TOPIC, emergency_incident_data)
        time.sleep(random.uniform(3, 5))  # Simulate time delay between data generation

if __name__ == "__main__":
    producer_config = {
        'bootstrap.servers': KAFKA_BOOTSTRAP_SERVERS,
        'error_cb': lambda err: print(f"Kafka Error: {err}"),
    }

    producer = SerializingProducer(producer_config)

    try:
        simulate_journey(producer, 'Vehicle-RitayanPatra-123')
    
    except KeyboardInterrupt as e:
        print("Simulation interrupted by user.")
    except Exception as e:
        print(f"Unexpected error occured: {e}")

