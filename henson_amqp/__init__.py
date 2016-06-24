"""AMQP plugin for Henson."""

import asyncio
from collections import namedtuple
from enum import IntEnum
import json
import pkg_resources
import os

import aioamqp
from henson import Extension

__all__ = ('AMQP', 'Message')

try:
    _dist = pkg_resources.get_distribution(__package__)
    if not __file__.startswith(os.path.join(_dist.location, __package__)):
        # Manually raise the exception if there is a distribution but
        # it's installed from elsewhere.
        raise pkg_resources.DistributionNotFound
except pkg_resources.DistributionNotFound:
    __version__ = 'development'
else:
    __version__ = _dist.version


# TODO: replace this namedtuple with a message class that supports
# acknowledgement, (de)serialization, and other convenience functions
Message = namedtuple('Message', ('body', 'envelope', 'properties'))


class Consumer:
    """A consumer of an AMQP queue.

    Args:
        app (henson.base.Application): The application for which this
            consumer consumes.
    """

    def __init__(self, app):
        """Initialize the consumer."""
        # Store a reference to the app and declare some attributes that
        # will be set later by async calls.
        self.app = app
        self._message_queue = None
        self._transport = None
        self._protocol = None
        self._channel = None

        # Register the message acknowledgement and application teardown
        # callbacks with the application.
        self.app.message_acknowledgement(self._acknowledge_message)
        self.app.teardown(self._teardown)

    @asyncio.coroutine
    def _acknowledge_message(self, app, message):
        """Acknowledge a message on the AMQP server.

        Args:
            app (henson.base.Application): The application that
                processed the message.
            message (Message): The message returned from the consumer to
                the application.
        """
        yield from self._channel.basic_client_ack(message.envelope.delivery_tag)  # NOQA: line length

    @asyncio.coroutine
    def _teardown(self, app):
        """Cleanup the protocol and transport before shutting down.

        Args:
            app (henson.base.Application): The application to which this
                Consumer belongs.
        """
        if self._protocol is not None:
            yield from self._protocol.close()
        if self._transport is not None:
            self._transport.close()

    @asyncio.coroutine
    def _enqueue_message(self, channel, body, envelope, properties):
        """Add fetched messages to the internal message queue.

        Args:
            body (bytes): The message fetched from rabbit.
            envelope (aioamqp.envelope.Envelope): An envelope of
                message metadata.
            properties (aioamqp.properties.Properties): Additional
                properties about the message content (e.g. headers,
                content_type, etc.).
        """
        message = Message(body, envelope, properties)
        yield from self._message_queue.put(message)

    @asyncio.coroutine
    def _connection_error_callback(self, exception):
        """Handle aioamqp connection errors.

        Args:
            exception (Exception): The exception resulting from the
                connection being closed.
        """
        yield from self._message_queue.put(exception)

    @asyncio.coroutine
    def _begin_consuming(self):
        """Begin reading messages from the specified AMQP broker."""
        # Create a connection to the broker
        self._message_queue = asyncio.Queue(
            maxsize=self.app.settings['AMQP_PREFETCH_LIMIT'])
        self._transport, self._protocol = yield from aioamqp.connect(
            host=self.app.settings['AMQP_HOST'],
            port=self.app.settings['AMQP_PORT'],
            login=self.app.settings['AMQP_USERNAME'],
            password=self.app.settings['AMQP_PASSWORD'],
            virtualhost=self.app.settings['AMQP_VIRTUAL_HOST'],
            heartbeat=self.app.settings['AMQP_HEARTBEAT_INTERVAL'],
            on_error=self._connection_error_callback,
            **self.app.settings['AMQP_CONNECTION_KWARGS']
        )

        # Declare the queue and exchange that we expect to read from
        self._channel = yield from self._protocol.channel()

        yield from self._channel.queue_declare(
            queue_name=self.app.settings['AMQP_INBOUND_QUEUE'],
            durable=self.app.settings['AMQP_INBOUND_QUEUE_DURABLE'],
        )
        if self.app.settings['AMQP_INBOUND_EXCHANGE']:
            yield from self._channel.exchange_declare(
                arguments=self.app.settings['AMQP_INBOUND_EXCHANGE_KWARGS'],
                durable=self.app.settings['AMQP_INBOUND_EXCHANGE_DURABLE'],
                exchange_name=self.app.settings['AMQP_INBOUND_EXCHANGE'],
                type_name=self.app.settings['AMQP_INBOUND_EXCHANGE_TYPE'],
            )
            yield from self._channel.queue_bind(
                queue_name=self.app.settings['AMQP_INBOUND_QUEUE'],
                exchange_name=self.app.settings['AMQP_INBOUND_EXCHANGE'],
                routing_key=self.app.settings['AMQP_INBOUND_ROUTING_KEY'],
            )

        # Begin reading and assign the callback function to be called
        # with each message retrieved from the broker
        yield from self._channel.basic_consume(
            queue_name=self.app.settings['AMQP_INBOUND_QUEUE'],
            callback=self._enqueue_message,
        )

    @asyncio.coroutine
    def read(self):
        """Read a single message from the message queue.

        If the consumer has not yet begun reading from the AMQP broker,
        that process is initiated before yielding from the queue.

        Returns:
            Message: The next available message.

        Raises:
            aioamqp.exceptions.AioamqpException: The exception raised on
                connection close.
        """
        # On the first call to read, connect to the AMQP server and
        # begin consuming messages.
        if self._message_queue is None:
            yield from self._begin_consuming()

        # Read the next result from the internal message queue.
        result = yield from self._message_queue.get()

        # If the result is an exception, the connection was closed, and
        # the consumer was unable to recover. Raise the original
        # exception.
        if isinstance(result, Exception):
            raise result

        # Finally, return the result if it is a valid message.
        return result

    @asyncio.coroutine
    def retry(self, app, message):
        """Requeue a message to be processed again.

        This coroutine is meant for use with the
        :class:`henson.contrib.retry.Retry` extension.

        Args:
            app (henson.base.Application): The application processing
                the message.
            message (dict): A copy of the message read from the AMQP
                server.

        .. note:: This function assumes that messages are JSON
            serializeable. If they are not, a custom function may be
            used in its place.
        """
        yield from self._channel.publish(
            payload=json.dumps(message).encode('utf-8'),
            exchange_name=self.app.settings['AMQP_INBOUND_EXCHANGE'],
            routing_key=self.app.settings['AMQP_INBOUND_ROUTING_KEY'],
        )


class Producer:
    """A producer of an AMQP queue.

    Args:
        app (henson.base.Application): The application for which this
            producer produces.
    """

    def __init__(self, app):
        """Initialize the producer."""
        # Store a reference to the application for later use.
        self.app = app
        self._transport = None
        self._protocol = None
        self._channel = None

        # Register a teardown callback.
        self.app.teardown(self._teardown)

    @asyncio.coroutine
    def _connect(self):
        self._transport, self._protocol = yield from aioamqp.connect(
            host=self.app.settings['AMQP_HOST'],
            port=self.app.settings['AMQP_PORT'],
            login=self.app.settings['AMQP_USERNAME'],
            password=self.app.settings['AMQP_PASSWORD'],
            virtualhost=self.app.settings['AMQP_VIRTUAL_HOST'],
            heartbeat=self.app.settings['AMQP_HEARTBEAT_INTERVAL'],
            **self.app.settings['AMQP_CONNECTION_KWARGS']
        )
        self._channel = yield from self._protocol.channel()

    @asyncio.coroutine
    def _teardown(self, app):
        """Cleanup the protocol and transport before shutting down.

        Args:
            app (henson.base.Application): The application to which this
                Consumer belongs.
        """
        if self._protocol is not None:
            yield from self._protocol.close()
        if self._transport is not None:
            self._transport.close()

    @asyncio.coroutine
    def send(self, message, *, routing_key=None):
        """Send a message to the configured AMQP broker and exchange.

        Args:
            message (str): The body of the message to send.
            routing_key (str): The routing key that should be used to
                send the message. If set to ``None``, the
                ``AMQP_OUTBOUND_ROUTING_KEY`` application setting will
                be used. Defaults to ``None``.
        """
        properties = {
            'delivery_mode': self.app.settings['AMQP_DELIVERY_MODE'].value,
        }
        if not self._channel:
            yield from self._connect()
        if routing_key is None:
            routing_key = self.app.settings['AMQP_OUTBOUND_ROUTING_KEY']

        yield from self._channel.exchange_declare(
            arguments=self.app.settings['AMQP_OUTBOUND_EXCHANGE_KWARGS'],
            durable=self.app.settings['AMQP_OUTBOUND_EXCHANGE_DURABLE'],
            exchange_name=self.app.settings['AMQP_OUTBOUND_EXCHANGE'],
            type_name=self.app.settings['AMQP_OUTBOUND_EXCHANGE_TYPE'],
        )
        yield from self._channel.publish(
            payload=message,
            exchange_name=self.app.settings['AMQP_OUTBOUND_EXCHANGE'],
            routing_key=routing_key,
            properties=properties,
        )


class DeliveryMode(IntEnum):
    """AMQP message delivery modes."""

    NONPERSISTENT = 1
    """Mark messages as non-persistent before sending to the AMQP instance."""
    PERSISTENT = 2
    """Mark messages as persistent before sending to the AMQP instance."""


class AMQP(Extension):
    """An interface to interact with an AMQP broker."""

    DEFAULT_SETTINGS = {
        # Connection settings
        'AMQP_HOST': 'localhost',
        'AMQP_PORT': 5672,
        'AMQP_USERNAME': 'guest',
        'AMQP_PASSWORD': 'guest',
        'AMQP_VIRTUAL_HOST': '/',
        'AMQP_HEARTBEAT_INTERVAL': 60,
        'AMQP_CONNECTION_KWARGS': {},

        # Consumer settings
        'REGISTER_CONSUMER': False,
        'AMQP_DISPATCH_METHOD': 'ROUND_ROBIN',
        'AMQP_INBOUND_EXCHANGE': '',
        'AMQP_INBOUND_EXCHANGE_DURABLE': False,
        'AMQP_INBOUND_EXCHANGE_TYPE': 'direct',
        'AMQP_INBOUND_EXCHANGE_KWARGS': {},
        'AMQP_INBOUND_QUEUE': '',
        'AMQP_INBOUND_QUEUE_DURABLE': False,
        'AMQP_INBOUND_ROUTING_KEY': '',
        'AMQP_PREFETCH_LIMIT': 0,

        # Producer settings
        'AMQP_OUTBOUND_EXCHANGE': '',
        'AMQP_OUTBOUND_EXCHANGE_DURABLE': False,
        'AMQP_OUTBOUND_EXCHANGE_TYPE': 'direct',
        'AMQP_OUTBOUND_EXCHANGE_KWARGS': {},
        'AMQP_OUTBOUND_ROUTING_KEY': '',
        'AMQP_DELIVERY_MODE': DeliveryMode.NONPERSISTENT,
    }

    def init_app(self, app):
        """Initialize the application.

        If the application's ``REGISTER_CONSUMER`` setting is truthy,
        create a consumer and attach it to the application.

        Args:
            app (henson.base.Application): The application instance that
                will be initialized.
        """
        super().init_app(app)
        if app.settings['REGISTER_CONSUMER']:
            app.consumer = self.consumer()

    def consumer(self):
        """Return a new AMQP consumer.

        Returns:
            Consumer: A new consumer object that can be used to read
                from the AMQP broker and queue specified the
                Application's settings.
        """
        return Consumer(self.app)

    def producer(self):
        """Return an AMQP producer, creating it if necessary.

        Returns:
            Producer: A new producer object that can be used to write to
                the AMQP broker and exchange specified by the
                Application's settings.
        """
        if not hasattr(self, '_producer'):
            self._producer = Producer(self.app)
        return self._producer
