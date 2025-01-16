from unittest.mock import MagicMock, patch

import pytest
from pika import BasicProperties

from src.rabbitmq import RabbitMQ


@pytest.fixture
def mock_connection():
    with patch("src.rabbitmq.BlockingConnection") as MockBlockingConnection:
        mock_connection = MagicMock()
        mock_channel = MagicMock()

        mock_connection.is_closed = False
        mock_connection.channel.return_value = mock_channel
        mock_channel.queue_declare.return_value = None
        mock_channel.basic_publish.return_value = None

        MockBlockingConnection.return_value = mock_connection

        yield mock_connection


@pytest.fixture
def rabbitmq(mock_connection) -> RabbitMQ:
    return RabbitMQ()


def test_initialization(rabbitmq: RabbitMQ, mock_connection) -> None:
    mock_connection.channel.assert_called_once()
    assert rabbitmq.connection == mock_connection
    assert rabbitmq.channel == mock_connection.channel.return_value


def test_close(rabbitmq: RabbitMQ, mock_connection) -> None:
    rabbitmq.close()
    mock_connection.close.assert_called_once()


def test_publish(rabbitmq: RabbitMQ, mock_connection) -> None:
    rabbitmq.publish("test_queue", "test_message")

    mock_connection.channel().queue_declare.assert_called_once_with(
        queue="test_queue", durable=True
    )

    mock_connection.channel().basic_publish.assert_called_once_with(
        exchange="",
        routing_key="test_queue",
        body="test_message",
        properties=BasicProperties(delivery_mode=2),
    )


def test_consume(rabbitmq: RabbitMQ, mock_connection) -> None:
    mock_callback = MagicMock()

    rabbitmq.consume("test_queue", mock_callback)

    mock_connection.channel().basic_consume.assert_called_once_with(
        queue="test_queue", on_message_callback=mock_callback, auto_ack=True
    )

    mock_connection.channel().start_consuming.assert_called_once()


def test_publish_connection_not_established(rabbitmq: RabbitMQ) -> None:
    rabbitmq.channel = None

    with pytest.raises(Exception):
        rabbitmq.publish("test_queue", "test_message")


def test_consume_connection_not_established(rabbitmq: RabbitMQ) -> None:
    rabbitmq.channel = None

    with pytest.raises(Exception):
        rabbitmq.consume("test_queue", lambda *args: None)
