"""henson_amqp integration tests."""

import json

import pytest

from henson_amqp import DeliveryMode


@pytest.mark.parametrize(
    'delivery_mode', (DeliveryMode.NONPERSISTENT, DeliveryMode.PERSISTENT, 1, 2))
@pytest.mark.asyncio
def test_read_write(test_consumer, test_producer, delivery_mode):
    """Test that reading from the consumer returns a message from amqp."""
    yield from test_consumer._begin_consuming()
    test_producer.app.settings['AMQP_DELIVERY_MODE'] = delivery_mode
    message = json.dumps({'spam': 'eggs'}).encode()
    yield from test_producer.send(message)
    read_message = (yield from test_consumer.read())
    yield from test_consumer._acknowledge_message(
        test_consumer.app,
        read_message,
    )
    assert read_message.body == message
    assert read_message.properties.delivery_mode == delivery_mode
    yield from test_consumer._teardown(test_consumer.app)
    yield from test_producer._teardown(test_producer.app)
