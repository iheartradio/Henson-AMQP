"""henson_amqp unit tests."""

import asyncio
from copy import copy
import json
from unittest import mock

import pytest

from henson_amqp import Message


@pytest.mark.asyncio
def test_enqueue_message(test_consumer, test_envelope, test_properties):
    """Test adding messages to the consumer's message queue."""
    # Mock away the channel for unit tests
    test_consumer.channel = mock.MagicMock()
    test_consumer._message_queue = asyncio.Queue()
    yield from test_consumer._enqueue_message(
        test_consumer.channel, b'test', test_envelope, test_properties)
    expected_message = Message(b'test', test_envelope, test_properties)
    actual_message = test_consumer._message_queue.get_nowait()
    assert expected_message == actual_message


@pytest.mark.asyncio
def test_read(test_consumer, test_envelope, test_properties):
    """Test that reading returns a message from the queue."""
    # Mock away the channel for unit tests
    test_consumer._channel = mock.MagicMock()
    test_consumer._message_queue = asyncio.Queue()
    # Get a consumer and add an mock message to its queue
    message = Message(b'foo', test_envelope, test_properties)
    test_consumer._message_queue.put_nowait(message)
    read_message = (yield from test_consumer.read())
    assert read_message == message


@pytest.mark.asyncio
def test_retry(test_consumer):
    """Test that the included retry function works."""
    test_consumer._channel = mock.MagicMock()
    message = {"spam": "eggs"}
    yield from test_consumer.retry(test_consumer.app, message)
    test_consumer._channel.publish.assert_called_with(
        payload=json.dumps(message).encode('utf-8'),
        exchange_name=test_consumer.app.settings['AMQP_INBOUND_EXCHANGE'],
        routing_key=test_consumer.app.settings['AMQP_INBOUND_ROUTING_KEY'],
    )


def test_producer_factory(test_amqp):
    """Test that ``AMQP.producer`` caches its result."""
    producer1 = test_amqp.producer()
    producer2 = test_amqp.producer()
    assert producer1 is producer2


def test_different_producer_factories(test_amqp):
    """Test that different AMQP instances return different producers."""
    test_amqp_copy = copy(test_amqp)
    producer1 = test_amqp.producer()
    producer2 = test_amqp_copy.producer()
    assert producer1 is not producer2
