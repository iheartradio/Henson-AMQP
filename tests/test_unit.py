"""henson_amqp unit tests."""

import asyncio
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
    test_consumer.channel = mock.MagicMock()
    test_consumer._message_queue = asyncio.Queue()
    # Get a consumer and add an mock message to its queue
    message = Message(b'foo', test_envelope, test_properties)
    test_consumer._message_queue.put_nowait(message)
    read_message = (yield from test_consumer.read())
    assert read_message == message
