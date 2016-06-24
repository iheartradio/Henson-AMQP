========
Settings
========

Connection Settings
===================

+------------------------------------+----------------------------------------+
| ``AMQP_HOST``                      | The hostname or IP address of the AMQP |
|                                    | server to connect to. Defaults to      |
|                                    | ``'localhost'``.                       |
+------------------------------------+----------------------------------------+
| ``AMQP_PORT``                      | The port of the AMQP server to connect |
|                                    | to. Defaults to ``5672``.              |
+------------------------------------+----------------------------------------+
| ``AMQP_USERNAME``                  | The username to authenticate with.     |
|                                    | Defaults to   ``'guest'``.             |
+------------------------------------+----------------------------------------+
| ``AMQP_PASSWORD``                  | The password to authenticate with.     |
|                                    | Defaults to ``'guest'``.               |
+------------------------------------+----------------------------------------+
| ``AMQP_VIRTUAL_HOST``              | The virtual host to use. Defaults to   |
|                                    | ``'/'``.                               |
+------------------------------------+----------------------------------------+
| ``AMQP_HEARTBEAT_INTERVAL``        | The heartbeat interval to use for      |
|                                    | connections. Defaults to ``60``.       |
+------------------------------------+----------------------------------------+
| ``AMQP_CONNECTION_KWARGS``         | Additional arguments to pass to        |
|                                    | :func:`aioamqp.connect`. Defaults to   |
|                                    | ``{}``.                                |
+------------------------------------+----------------------------------------+

Consumer Settings
=================

+-----------------------------------+-------------------------------------------+
| ``REGISTER_CONSUMER``             | If ``True``, a consumer will be           |
|                                   | automatically created and assigned to     |
|                                   | the application. Defaults to ``False``.   |
+-----------------------------------+-------------------------------------------+
| ``AMQP_INBOUND_EXCHANGE``         | The name of the exchange that the         |
|                                   | consumer should read from. Defaults to    |
|                                   | ``''`` (the AMQP default exchange).       |
+-----------------------------------+-------------------------------------------+
| ``AMQP_INBOUND_EXCHANGE_DURABLE`` | The durability setting of the exchange    |
|                                   | that the consumer reads from. Defaults    |
|                                   | to ``False``.                             |
+-----------------------------------+-------------------------------------------+
| ``AMQP_INBOUND_EXCHANGE_TYPE``    | The type of the inbound exchange.         |
|                                   | Defaults to ``'direct'``.                 |
+-----------------------------------+-------------------------------------------+
| ``AMQP_INBOUND_EXCHANGE_KWARGS``  | Additonal arguments to pass to            |
|                                   | :func:`aioamqp.channel.exchange_declare`. |
|                                   | Defaults to ``{}``.                       |
+-----------------------------------+-------------------------------------------+
| ``AMQP_INBOUND_QUEUE``            | The name of the queue that the            |
|                                   | consumer should read from. Defaults to    |
|                                   | ``''`` (the AMQP default queue).          |
+-----------------------------------+-------------------------------------------+
| ``AMQP_INBOUND_QUEUE_DURABLE``    | The durability setting of the queue       |
|                                   | the consumer reads from. Defaults to      |
|                                   | ``False``.                                |
+-----------------------------------+-------------------------------------------+
| ``AMQP_INBOUND_ROUTING_KEY``      | The routing key used to bind the          |
|                                   | inbound exchange and queue. Defaults      |
|                                   | to ``''``.                                |
+-----------------------------------+-------------------------------------------+
| ``AMQP_DISPATCH_METHOD``          | Reserved for future use.                  |
+-----------------------------------+-------------------------------------------+

Producer Settings
=================

+------------------------------------+------------------------------------------------+
| ``AMQP_OUTBOUND_EXCHANGE``         | The name of the exchange used by the           |
|                                    | producer to send messages. Defaults to         |
|                                    | ``''``.                                        |
+------------------------------------+------------------------------------------------+
| ``AMQP_OUTBOUND_EXCHANGE_DURABLE`` | The durability setting of the outbound         |
|                                    | exchange. Defaults to ``False``.               |
+------------------------------------+------------------------------------------------+
| ``AMQP_OUTBOUND_EXCHANGE_TYPE``    | The type of the outbound exchange.             |
|                                    | Defaults to ``'direct'``.                      |
+------------------------------------+------------------------------------------------+
| ``AMQP_OUTBOUND_EXCHANGE_KWARGS``  | Additonal arguments to pass to                 |
|                                    | :func:`aioamqp.channel.exchange_declare`.      |
|                                    | Defaults to ``{}``.                            |
+------------------------------------+------------------------------------------------+
| ``AMQP_OUTBOUND_ROUTING_KEY``      | The default routing key used when              |
|                                    | sending messages to the outbound               |
|                                    | exchange if the ``routing_key`` argument       |
|                                    | is not provided. Defaults to ``''``.           |
+------------------------------------+------------------------------------------------+
| ``AMQP_PREFETCH_LIMIT``            | The maximum number of messages to keep         |
|                                    | in the internal queue waiting to be            |
|                                    | processed. If set to ``0``, the                |
|                                    | consumer will fetch all available              |
|                                    | messages from the AMQP queue. Defaults         |
|                                    | to ``0``.                                      |
+------------------------------------+------------------------------------------------+
| ``AMQP_DELIVERY_MODE``             | The mode used when sending messages.           |
|                                    | By default, messages are                       |
|                                    | non-persistent.                                |
|                                    | Defaults to                                    |
|                                    | :attr:`henson_amqp.DeliveryMode.NONPERSISTENT` |
+------------------------------------+------------------------------------------------+
