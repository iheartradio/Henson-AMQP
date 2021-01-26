=========
Changelog
=========

Version 0.9.0
=============

Released 2021-01-26

- Drop support for Python < 3.8, add support for Python >= 3.8
- Add SSL support

Version 0.8.1
=============

Released 2020-04-13

- Update Henson version requirement to allow versions less than 3.0


Version 0.8.0
=============

Released 2020-02-05

- Add support for ``AMQP_PREFETCH_COUNT`` and ``AMQP_PREFETCH_SIZE``


Version 0.7.0
=============

Released 2019-02-20

- Allow callers of ``Producer.send`` to specify an exchange name


Version 0.6.0
=============

Released 2018-06-25

- Support both ``int`` values and existing ``henson_amqp.DeliveryMode`` ``enums``
  for the ``AMQP_DELIVERY_MODE`` setting
- Stop declaring the exchange with every message sent


Version 0.5.0
=============

Released 2016-06-24

- Support passing ``arguments`` to inbound and outbound exchange declaration


Version 0.4.0
=============

Released 2016-04-27

- Allow callers of ``Producer.send`` to specify a routing key


Version 0.3.0
=============

Released 2016-04-08

- Add support for ``Retry``
- Add ``REGISTER_CONSUMER`` setting


Version 0.2.0
=============

Released 2016-03-11

- If a connection is closed by ``aioamqp`` while reading, raise that exception
  during calls to ``Consumer.read`` after all previously read messages have
  been returned.


Version 0.1.0
=============

Released 2016-03-01

- Initial release
