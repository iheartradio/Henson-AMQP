=========
Changelog
=========

Version 0.6.0
=============

Release TBD

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
