"""henson_amqp integration tests."""

import json

import pytest


@pytest.mark.asyncio
def test_read_write(test_consumer, test_producer):
    """Test that reading from the consumer returns a message from amqp."""
    message = json.dumps({'spam': 'eggs'}).encode()
    yield from test_producer.send(message)
    read_message = (yield from test_consumer.read())
    assert read_message.body == message
