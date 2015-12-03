"""AMQP plugin for Henson."""

from pkg_resources import get_distribution

from henson import Extension

__all__ = ('AMQP',)
__version__ = get_distribution(__package__).version


class AMQP(Extension):
    """An interface to interact with an AMQP broker."""
