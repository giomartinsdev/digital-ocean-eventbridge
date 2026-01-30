import os
import json
from dotenv import load_dotenv
load_dotenv()

class Constants():
    def __init__(self):
        self.RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'rabbitmq')
        self.RABBITMQ_PORT = os.getenv('RABBITMQ_PORT', '5672')
        self.RABBITMQ_USER = os.getenv('RABBITMQ_USER', 'guest')
        self.RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
        self.RABBITMQ_URL = f"amqp://{self.RABBITMQ_USER}:{self.RABBITMQ_PASSWORD}@{self.RABBITMQ_HOST}:{self.RABBITMQ_PORT}"
        self.MAIN_EXCHANGE = 'app_events_exchange'
        self.DLX_EXCHANGE = 'app_events_dlx'
        self.QUEUE_MAP = self._load_mapping()
    
    def _load_mapping(self):
        with open('mapping.json', 'r') as f:
            return json.load(f)