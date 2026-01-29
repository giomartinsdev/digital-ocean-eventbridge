import os
import json

class Constants():
    def __init__(self):
        self.RABBITMQ_URL = os.getenv('RABBITMQ_URL', 'amqp://guest:guest@localhost:5672//').strip()
        self.MAIN_EXCHANGE = 'app_events_exchange'
        self.DLX_EXCHANGE = 'app_events_dlx'
        self.QUEUE_MAP = self._load_mapping()
    
    def _load_mapping(self):
        with open('mapping.json', 'r') as f:
            return json.load(f)