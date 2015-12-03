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

.. code::

    # settings.py
    AMQP_QUEUE_INBOUND='incoming'
    AMQP_EXCHANGE_INBOUND='incoming'
    AMQP_EXCHANGE_OUTBOUND='outgoing'
    AMQP_ROUTING_KEY_INBOUND='outgoing'
    AMQP_ROUTING_KEY_OUTBOUND='outgoing'

.. code::

    # app.py
    from henson import Application
    from henson_amqp import AMQP

    from . import settings
    from .callback import run

    app = Application('app', callback=run)
    app.config.from_object(settings)

    amqp = AMQP(app)
    app.consumer = amqp.consumer()

.. code::

    $ henson run app

Contents:

.. toctree::
   :maxdepth: 2

   api


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

