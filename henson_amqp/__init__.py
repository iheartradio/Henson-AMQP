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

# This wrapper object makes it easier to pass around AMQP settings over
# specifying all settings as function arguments in everywhere they're
# required
AMQPSettings = namedtuple(
    'AMQPSettings',
    ('host', 'port', 'username', 'password', 'virtual_host', 'kwargs'),
)


class Consumer:
    """A consumer of an AMQP queue.

    Args:
        settings (AMQPSettings): A settings object specifying options to
            be passed to ``aioamqp.connect``.
        queue_name (str): The name of the queue from which to read.
        exchange_name (Optional[str]): If supplied, the name of the
            exchange that the queue is bound to. Defaults to ``''``.
        exchange_type (Optional[str]): The type of the exchange
            specified by ``exchange_name``. Defaults to ``'direct'``.
        routing_key (Optional[str]): The routing key used to bind the
            queue and exchange. Defaults to ``''``.
    """

    def __init__(self, settings, queue_name, exchange_name='',
                 exchange_type='direct', routing_key=''):
        """Initialize the consumer."""
        self.settings = settings
        self.queue_name = queue_name
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.routing_key = routing_key

        # Declare some attributes that will be set later by async calls
        self._message_queue = None
        self.transport = None
        self.protocol = None
        self.channel = None

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
        # TODO: once Henson supports a message acknowledgement callback,
        # the ack should happen there instead
        yield from channel.basic_client_ack(envelope.delivery_tag)

    @asyncio.coroutine
    def _begin_consuming(self):
        """Begin reading messages from the specified AMQP broker."""
        # Create a connection to the broker
        self._message_queue = asyncio.Queue()
        self.transport, self.protocol = yield from aioamqp.connect(
            host=self.settings.host,
            port=self.settings.port,
            login=self.settings.username,
            password=self.settings.password,
            virtual_host=self.settings.virtual_host,
            **self.settings.kwargs
        )

        # Declare the queue and exchange that we expect to read from
        self.channel = yield from self.protocol.channel()
        yield from self.channel.queue_declare(self.queue_name)
        if self.exchange_name:
            yield from self.channel.exchange_declare(
                exchange_name=self.exchange_name,
                type_name=self.exchange_type,
            )
            yield from self.channel.queue_bind(
                self.queue_name, self.exchange_name, self.routing_key)

        # Begin reading and assign the callback function to be called
        # with each message retrieved from the broker
        yield from self.channel.basic_consume(
            queue_name=self.queue_name,
            callback=self._enqueue_message,
        )

        # TODO: once Henson supports application teardown, this should
        # happen in that callback
        # Close the connection
        # yield from self.protocol.close()
        # self.transport.close()

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
        settings (AMQPSettings): A settings object specifying options to
            be passed to ``aioamqp.connect``.
        exchange_name (str): The name of the exchange to publish to.
        exchange_type (Optional[str]): The type of the exchange
            specified by ``exchange_name``. Defaults to ``'direct'``.
        routing_key (Optional[str]): The routing key that should be used
            when publishing messages. Defaults to ``''``.
    """

    def __init__(self, settings, exchange_name, exchange_type='direct',
                 routing_key=''):
        """Initialize the producer."""
        self.settings = settings
        self.exchange_name = exchange_name
        self.exchange_type = exchange_type
        self.routing_key = routing_key

    @asyncio.coroutine
    def send(self, message):
        """Send a message to the configured AMQP broker and exchange.

        Args:
            message (str): The body of the message to send.
        """
        self.transport, self.protocol = yield from aioamqp.connect(
            host=self.settings.host,
            port=self.settings.port,
            login=self.settings.username,
            password=self.settings.password,
            virtual_host=self.settings.virtual_host,
            **self.settings.kwargs
        )
        channel = yield from self.protocol.channel()
        yield from channel.exchange_declare(
            exchange_name=self.exchange_name,
            type_name=self.exchange_type,
        )
        yield from channel.publish(
            message, self.exchange_name, self.routing_key)
        # yield from self.protocol.close()
        # self.transport.close()


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

    def init_app(self, app):
        """Initialize the application."""
        super().init_app(app)
        self.amqp_settings = AMQPSettings(
            host=app.settings['AMQP_HOST'],
            port=app.settings['AMQP_PORT'],
            username=app.settings['AMQP_USERNAME'],
            password=app.settings['AMQP_PASSWORD'],
            virtual_host=app.settings['AMQP_VIRTUAL_HOST'],
            kwargs=app.settings['AMQP_CONNECTION_KWARGS'],
        )

    def consumer(self):
        """Return a new AMQP consumer.

        Returns:
            Consumer: A new consumer object that can be used to read
                from the AMQP broker and queue specified the
                Application's settings.
        """
        return Consumer(
            settings=self.amqp_settings,
            queue_name=self.app.settings['AMQP_QUEUE_INBOUND'],
            exchange_name=self.app.settings['AMQP_EXCHANGE_INBOUND'],
            exchange_type=self.app.settings['AMQP_EXCHANGE_TYPE_INBOUND'],
            routing_key=self.app.settings['AMQP_ROUTING_KEY_INBOUND'],
        )

    def producer(self):
        """Return a new AMQP producer.

        Returns:
            Producer: A new producer object that can be used to write to
                the AMQP broker and exchange specified by the
                Application's settings.
        """
        return Producer(
            settings=self.amqp_settings,
            exchange_name=self.app.settings['AMQP_EXCHANGE_OUTBOUND'],
            exchange_type=self.app.settings['AMQP_EXCHANGE_TYPE_OUTBOUND'],
            routing_key=self.app.settings['AMQP_ROUTING_KEY_OUTBOUND'],
        )
