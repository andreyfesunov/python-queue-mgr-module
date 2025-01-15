import os
from typing import Callable

from pika import BasicProperties
from pika.adapters.blocking_connection import BlockingChannel, BlockingConnection
from pika.connection import ConnectionParameters
from pika.credentials import PlainCredentials
from pika.spec import Basic


class RabbitMQ:
    def __init__(self) -> None:
        self.user: str = os.getenv("RABBITMQ_USER", "user")
        self.password: str = os.getenv("RABBITMQ_PASSWORD", "password")
        self.host: str = os.getenv("RABBITMQ_HOST", "localhost")
        self.port: int = int(os.getenv("RABBITMQ_PORT", 5672))
        self.connection: BlockingConnection | None = None
        self.channel: BlockingChannel | None = None
        self.connect()

    def connect(self) -> None:
        credentials: PlainCredentials = PlainCredentials(
            username=self.user, password=self.password
        )
        parameters: ConnectionParameters = ConnectionParameters(
            host=self.host, port=self.port, credentials=credentials
        )
        self.connection = BlockingConnection(parameters=parameters)
        self.channel = self.connection.channel()

    def close(self) -> None:
        if self.connection and not self.connection.is_closed:
            self.connection.close()

    def consume(
        self,
        queue_name: str,
        callback: Callable[
            [BlockingChannel, Basic.Deliver, BasicProperties, bytes], None
        ],
    ) -> None:
        if not self.channel:
            raise Exception("Connection is not established.")

        self.channel.basic_consume(
            queue=queue_name, on_message_callback=callback, auto_ack=True
        )
        self.channel.start_consuming()

    def publish(self, queue_name: str, message: str) -> None:
        if not self.channel:
            raise Exception("Connection is not established.")

        self.channel.queue_declare(queue=queue_name, durable=True)
        self.channel.basic_publish(
            exchange="",
            routing_key=queue_name,
            body=message,
            properties=BasicProperties(delivery_mode=2),
        )

        print(f"Sent message to queue {queue_name}: {message}")
