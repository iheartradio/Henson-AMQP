"""Test utilities."""

import os
from unittest import mock

import pika.spec
from henson import Application
import pytest

from henson_amqp import AMQP


class Settings:
    """A container object for test settings."""

    AMQP_HOST = os.environ.get('TEST_AMQP_HOST', 'localhost')
    AMQP_INBOUND_QUEUE = 'test.in'
    AMQP_INBOUND_QUEUE_DURABLE = True
    AMQP_INBOUND_EXCHANGE = 'test.in'
    AMQP_INBOUND_EXCHANGE_DURABLE = True
    AMQP_OUTBOUND_EXCHANGE = 'test.in'
    AMQP_OUTBOUND_EXCHANGE_DURABLE = True
    AMQP_INBOUND_ROUTING_KEY = 'test.in'
    AMQP_OUTBOUND_ROUTING_KEY = 'test.in'


@pytest.fixture
def test_app():
    """Return a test application."""
    return Application('testing', Settings)


@pytest.fixture
def test_amqp(test_app):
    """Return an extension bound to the test app."""
    return AMQP(test_app)


@pytest.fixture
def test_consumer(test_amqp):
    """Return a consumer created by the test AMQP instance."""
    consumer = test_amqp.consumer()
    return consumer


@pytest.fixture
def test_method():
    """Return a mock pika.spec.Basic.Deliver."""
    return mock.Mock(spec=pika.spec.Basic.Deliver)


@pytest.fixture
def test_producer(test_amqp):
    """Return a producer created by the test AMQP instance."""
    producer = test_amqp.producer()
    return producer


@pytest.fixture
def test_properties():
    """Return a mock pika.spec.BasicProperties."""
    return mock.Mock(spec=pika.spec.BasicProperties)
