"""Test utilities."""

import os
from unittest import mock

from aioamqp.envelope import Envelope
from aioamqp.properties import Properties
import pytest

from henson_amqp import AMQP


class Application:
    """A stub application that can be used for testing.

    Args:
        **settings: Keyword arguments that will be used as settings.
    """

    def __init__(self, **settings):
        """Initialize the instance."""
        self.name = 'testing'
        self.settings = settings


@pytest.fixture
def test_amqp():
    """Return an extension bound to the test app."""
    app = Application(
        AMQP_HOST=os.environ.get('TEST_AMQP_HOST', 'localhost'),
        AMQP_QUEUE_INBOUND='test.in',
        AMQP_EXCHANGE_INBOUND='test.in',
        AMQP_EXCHANGE_OUTBOUND='test.in',
        AMQP_ROUTING_KEY_INBOUND='test.in',
        AMQP_ROUTING_KEY_OUTBOUND='test.in',
    )
    return AMQP(app)


@pytest.fixture
def test_consumer(test_amqp):
    """Return a consumer created by the test AMQP instance."""
    consumer = test_amqp.consumer()
    return consumer


@pytest.fixture
def test_producer(test_amqp):
    """Return a producer created by the test AMQP instance."""
    producer = test_amqp.producer()
    return producer


@pytest.fixture
def test_envelope():
    """Return a mock aioamqp.envelope.Envelope."""
    return mock.Mock(spec=Envelope)


@pytest.fixture
def test_properties():
    """Return a mock aioamqp.properties.Properties."""
    return mock.Mock(spec=Properties)
