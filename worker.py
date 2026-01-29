import pika
import requests
import logging
from dotenv import load_dotenv
from constants import Constants


class Worker:
    def __init__(self):
        self.constants = Constants()
        load_dotenv()
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )

    def callback(self, ch, method, _properties, body):
        queue_name = method.routing_key
        target_url = self.constants.QUEUE_MAP.get(queue_name)

        if target_url:
            try:
                headers = {'Content-Type': 'application/json'}
                resp = requests.post(target_url, data=body, headers=headers, timeout=10)
                
                if 200 <= resp.status_code < 300:
                    ch.basic_ack(delivery_tag=method.delivery_tag)
                else:
                    self.logger.error(f"Erro {resp.status_code} na Function. Rejeitando para DLQ.")
                    ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)
            except Exception as e:
                self.logger.error(f"Erro crítico: {e}. Enviando para DLQ.")
                ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

    def setup_rabbit(self, channel):
        channel.exchange_declare(exchange=self.constants.DLX_EXCHANGE, exchange_type='topic', durable=True)
        channel.exchange_declare(exchange=self.constants.MAIN_EXCHANGE, exchange_type='direct', durable=True)

        for queue_name in self.constants.QUEUE_MAP.keys():
            dlq_name = f"{queue_name}.dlq"

            channel.queue_declare(queue=dlq_name, durable=True, arguments={
                'x-message-ttl': 604800000 
            })
            channel.queue_bind(exchange=self.constants.DLX_EXCHANGE, queue=dlq_name, routing_key=queue_name)

            channel.queue_declare(queue=queue_name, durable=True, arguments={
                'x-dead-letter-exchange': self.constants.DLX_EXCHANGE,
                'x-dead-letter-routing-key': queue_name
            })
            
            channel.queue_bind(exchange=self.constants.MAIN_EXCHANGE, queue=queue_name, routing_key=queue_name)
            
            self.logger.info(f"Configurada: {queue_name} -> DLQ: {dlq_name}")

    def run(self):
        params = pika.URLParameters(self.constants.RABBITMQ_URL)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()

        self.setup_rabbit(channel)

        channel.basic_qos(prefetch_count=10)

        for queue_name in self.constants.QUEUE_MAP.keys():
            channel.basic_consume(queue=queue_name, on_message_callback=self.callback)

        self.logger.info('Worker com DLQ pronto. Aguardando eventos...')
        channel.start_consuming()


def main():
    worker = Worker()
    worker.run()

if __name__ == '__main__':
    main()