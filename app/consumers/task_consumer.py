import json
import logging

import pika

from app.core.config import settings

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TaskEventConsumer:
    def __init__(self):
        self.connection = None
        self.channel = None

    def connect(self):
        try:
            self.connection = pika.BlockingConnection(
                pika.URLParameters(settings.rabbitmq_url)
            )
            self.channel = self.connection.channel()
            self.channel.queue_declare(queue="task_events", durable=True)
            logger.info("Consumer connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")
            raise

    def process_message(self, ch, method, properties, body):
        try:
            message = json.loads(body.decode())
            event_type = message.get("event_type")
            task_data = message.get("task_data")
            timestamp = message.get("timestamp")

            logger.info(f"Processing event: {event_type}")
            logger.info(f"Task data: {task_data}")
            logger.info(f"Timestamp: {timestamp}")

            ch.basic_ack(delivery_tag=method.delivery_tag)

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            ch.basic_nack(delivery_tag=method.delivery_tag, requeue=True)

    def start_consuming(self):
        if not self.channel:
            self.connect()

        self.channel.basic_qos(prefetch_count=1)
        self.channel.basic_consume(
            queue="task_events", on_message_callback=self.process_message
        )

        logger.info("Starting to consume messages...")
        try:
            self.channel.start_consuming()
        except KeyboardInterrupt:
            logger.info("Stopping consumer...")
            self.channel.stop_consuming()
            if self.connection:
                self.connection.close()


if __name__ == "__main__":
    consumer = TaskEventConsumer()
    consumer.start_consuming()
