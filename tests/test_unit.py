"""henson_amqp unit tests."""

import asyncio
from copy import copy
import json
from unittest import mock

import pytest

from henson_amqp import AMQP, Consumer, Message


def test_register_consumer(test_app):
    """Test that consumer registration behaves correctly."""
    test_app.settings['REGISTER_CONSUMER'] = True
    test_app.settings['AMQP_PREFETCH_COUNT'] = 1
    test_app.settings['AMQP_PREFETCH_SIZE'] = 1
    AMQP(test_app)
    assert isinstance(test_app.consumer, Consumer)


def test_no_register_consumer(test_app):
    """Test that consumers are not registered if not explicitly set."""
    AMQP(test_app)
    assert not test_app.consumer


@pytest.mark.asyncio
async def test_enqueue_message(test_consumer, test_envelope, test_properties):
    """Test adding messages to the consumer's message queue."""
    # Mock away the channel for unit tests
    test_consumer.channel = mock.MagicMock()
    test_consumer._message_queue = asyncio.Queue()
    await test_consumer._enqueue_message(
        test_consumer.channel, b'test', test_envelope, test_properties)
    expected_message = Message(b'test', test_envelope, test_properties)
    actual_message = test_consumer._message_queue.get_nowait()
    assert expected_message == actual_message


@pytest.mark.asyncio
async def test_read(test_consumer, test_envelope, test_properties):
    """Test that reading returns a message from the queue."""
    # Mock away the channel for unit tests
    test_consumer._channel = mock.MagicMock()
    test_consumer._message_queue = asyncio.Queue()
    # Get a consumer and add an mock message to its queue
    message = Message(b'foo', test_envelope, test_properties)
    test_consumer._message_queue.put_nowait(message)
    read_message = (await test_consumer.read())
    assert read_message == message


@pytest.mark.asyncio
async def test_retry(test_consumer):
    """Test that the included retry function works."""
    test_consumer._channel = mock.AsyncMock()
    message = {"spam": "eggs"}
    await test_consumer.retry(test_consumer.app, message)
    test_consumer._channel.publish.assert_called_with(
        payload=json.dumps(message).encode('utf-8'),
        exchange_name=test_consumer.app.settings['AMQP_INBOUND_EXCHANGE'],
        routing_key=test_consumer.app.settings['AMQP_INBOUND_ROUTING_KEY'],
    )


@pytest.mark.asyncio
async def test_produce_exhange_name(test_producer):
    """Test that providing an exchange name works when sending."""
    test_producer._channel = mock.AsyncMock()
    message = 'message acknowledged'
    exchange_name = 'diverted'

    await test_producer.send(message, exchange_name=exchange_name)
    test_producer._channel.publish.assert_called_with(
        payload=message,
        routing_key=mock.ANY,
        exchange_name=exchange_name,
        properties=mock.ANY,
    )


@pytest.mark.asyncio
async def test_produce_no_exchange_name(test_producer):
    """Test that the default exchange is used when none is provided."""
    test_producer._channel = mock.AsyncMock()
    message = 'message acknowledged'
    await test_producer.send(message)

    test_producer._channel.publish.assert_called_with(
        payload=message,
        routing_key=mock.ANY,
        exchange_name=test_producer.app.settings['AMQP_OUTBOUND_EXCHANGE'],
        properties=mock.ANY,
    )


@pytest.mark.asyncio
async def test_produce_routing_key(test_producer):
    """Test that providing a routing key when sending works."""
    test_producer._channel = mock.AsyncMock()
    message = 'spam and eggs'
    routing_key = 'parrot'

    await test_producer.send(message, routing_key=routing_key)
    test_producer._channel.publish.assert_called_with(
        payload=message,
        routing_key=routing_key,
        exchange_name=mock.ANY,
        properties=mock.ANY,
    )


@pytest.mark.asyncio
async def test_produce_no_routing_key(test_producer):
    """Test that a default routing key is used when none is provided."""
    test_producer._channel = mock.AsyncMock()
    message = 'spam and eggs'
    await test_producer.send(message)

    test_producer._channel.publish.assert_called_with(
        payload=message,
        routing_key=test_producer.app.settings['AMQP_OUTBOUND_ROUTING_KEY'],
        exchange_name=mock.ANY,
        properties=mock.ANY,
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
