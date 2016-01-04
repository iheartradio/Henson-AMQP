"""AMQP plugin for Henson."""

import asyncio
from collections import namedtuple
from pkg_resources import get_distribution

import aioamqp
from henson import Extension

__all__ = ('AMQP', 'Message')
__version__ = get_distribution(__package__).version


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
    def _begin_consuming(self):
        """Begin reading messages from the specified AMQP broker."""
        # Create a connection to the broker
        self._message_queue = asyncio.Queue()
        self._transport, self._protocol = yield from aioamqp.connect(
            host=self.app.settings['AMQP_HOST'],
            port=self.app.settings['AMQP_PORT'],
            login=self.app.settings['AMQP_USERNAME'],
            password=self.app.settings['AMQP_PASSWORD'],
            virtual_host=self.app.settings['AMQP_VIRTUAL_HOST'],
            **self.app.settings['AMQP_CONNECTION_KWARGS']
        )

        # Declare the queue and exchange that we expect to read from
        self._channel = yield from self._protocol.channel()
        yield from self._channel.queue_declare(
            self.app.settings['AMQP_QUEUE_INBOUND'])
        if self.app.settings['AMQP_EXCHANGE_INBOUND']:
            yield from self._channel.exchange_declare(
                exchange_name=self.app.settings['AMQP_EXCHANGE_INBOUND'],
                type_name=self.app.settings['AMQP_EXCHANGE_TYPE_INBOUND'],
            )
            yield from self._channel.queue_bind(
                self.app.settings['AMQP_QUEUE_INBOUND'],
                self.app.settings['AMQP_EXCHANGE_INBOUND'],
                self.app.settings['AMQP_ROUTING_KEY_INBOUND'],
            )

        # Begin reading and assign the callback function to be called
        # with each message retrieved from the broker
        yield from self._channel.basic_consume(
            queue_name=self.app.settings['AMQP_QUEUE_INBOUND'],
            callback=self._enqueue_message,
        )

    @asyncio.coroutine
    def read(self):
        """Read a single message from the message queue.

        If the consumer has not yet begun reading from the AMQP broker,
        that process is initiated before yielding from the queue.

        Returns:
            Message: The next available message.
        """
        if self._message_queue is None:
            yield from self._begin_consuming()
        return (yield from self._message_queue.get())


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

        # Register a teardown callback.
        self.app.teardown(self._teardown)

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
    def send(self, message):
        """Send a message to the configured AMQP broker and exchange.

        Args:
            message (str): The body of the message to send.
        """
        self._transport, self._protocol = yield from aioamqp.connect(
            host=self.app.settings['AMQP_HOST'],
            port=self.app.settings['AMQP_PORT'],
            login=self.app.settings['AMQP_USERNAME'],
            password=self.app.settings['AMQP_PASSWORD'],
            virtual_host=self.app.settings['AMQP_VIRTUAL_HOST'],
            **self.app.settings['AMQP_CONNECTION_KWARGS']
        )
        channel = yield from self._protocol.channel()
        yield from channel.exchange_declare(
            exchange_name=self.app.settings['AMQP_EXCHANGE_OUTBOUND'],
            type_name=self.app.settings['AMQP_EXCHANGE_TYPE_OUTBOUND'],
        )
        yield from channel.publish(
            message,
            self.app.settings['AMQP_EXCHANGE_OUTBOUND'],
            self.app.settings['AMQP_ROUTING_KEY_OUTBOUND'],
        )


class AMQP(Extension):
    """An interface to interact with an AMQP broker."""

    DEFAULT_SETTINGS = {
        # Connection settings
        'AMQP_HOST': 'localhost',
        'AMQP_PORT': 5672,
        'AMQP_USERNAME': 'guest',
        'AMQP_PASSWORD': 'guest',
        'AMQP_VIRTUAL_HOST': '/',
        'AMQP_CONNECTION_KWARGS': {},

        # Send / receive settings
        'AMQP_DISPATCH_METHOD': 'ROUND_ROBIN',
        'AMQP_EXCHANGE_INBOUND': '',
        'AMQP_EXCHANGE_TYPE_INBOUND': 'direct',
        'AMQP_EXCHANGE_OUTBOUND': '',
        'AMQP_EXCHANGE_TYPE_OUTBOUND': 'direct',
        'AMQP_QUEUE_INBOUND': '',
        'AMQP_ROUTING_KEY_INBOUND': '',
        'AMQP_ROUTING_KEY_OUTBOUND': '',
    }

    def consumer(self):
        """Return a new AMQP consumer.

        Returns:
            Consumer: A new consumer object that can be used to read
                from the AMQP broker and queue specified the
                Application's settings.
        """
        return Consumer(self.app)

    def producer(self):
        """Return a new AMQP producer.

        Returns:
            Producer: A new producer object that can be used to write to
                the AMQP broker and exchange specified by the
                Application's settings.
        """
        return Producer(self.app)
