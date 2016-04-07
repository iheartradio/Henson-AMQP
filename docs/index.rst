===========
Henson-AMQP
===========

A library for interacting with AMQP with a Henson application.

Installation
============

Install with pip::

    $ python -m pip install henson-amqp

Quickstart
==========

.. code:: python

    # settings.py
    AMQP_INBOUND_QUEUE = 'incoming'
    AMQP_INBOUND_EXCHANGE = 'incoming'
    AMQP_OUTBOUND_EXCHANGE = 'outgoing'
    AMQP_INBOUND_ROUTING_KEY = 'outgoing'
    AMQP_OUTBOUND_ROUTING_KEY = 'outgoing'

.. code:: python

    # app.py
    from henson import Application
    from henson_amqp import AMQP

    from . import settings
    from .callback import run

    app = Application('app', callback=run)
    app.config.from_object(settings)

    amqp = AMQP(app)
    app.consumer = amqp.consumer()

    # Enable optional Retry support
    from henson.contrib.retry import Retry
    app.settings['RETRY_CALLBACK'] = app.consumer.retry
    Retry(app)

.. code::

    $ henson run app

Contents:

.. toctree::
   :maxdepth: 1

   settings
   api
   changes


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

