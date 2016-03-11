=========
Changelog
=========

Version 0.2.0
=============

Release TBD

- If a connection is closed by ``aioamqp`` while reading, raise that exception
  during calls to ``Consumer.read`` after all previously read messages have
  been returned.


Version 0.1.0
=============

Released 2016-03-01

- Initial release
