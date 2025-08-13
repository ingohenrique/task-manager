import json
import logging
from typing import Any, Dict

import pika

from app.core.config import settings

logger = logging.getLogger(__name__)


class RabbitMQService:
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
            logger.info("Connected to RabbitMQ")
        except Exception as e:
            logger.error(f"Failed to connect to RabbitMQ: {e}")

    def publish_task_event(self, event_type: str, task_data: Dict[str, Any]):
        if not self.channel:
            self.connect()

        try:
            message = {
                "event_type": event_type,
                "task_data": task_data,
                "timestamp": task_data.get("data_atualizacao")
                or task_data.get("data_criacao"),
            }

            self.channel.basic_publish(
                exchange="",
                routing_key="task_events",
                body=json.dumps(message, default=str),
                properties=pika.BasicProperties(delivery_mode=2),
            )
            logger.info(f"Published event: {event_type} for task {task_data.get('id')}")
        except Exception as e:
            logger.error(f"Failed to publish event: {e}")

    def close(self):
        if self.connection and not self.connection.is_closed:
            self.connection.close()


# Singleton instance
rabbitmq_service = RabbitMQService()
