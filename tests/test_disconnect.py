import asyncio

import pytest


@pytest.mark.asyncio
def test_disconnect_consumer(test_consumer):
    """Test disconnect logic for consumers."""
    test_consumer._message_queue = asyncio.Queue()
    test_consumer._message_queue.put_nowait('message')
    test_consumer._message_queue.put_nowait('message')
    test_consumer._message_queue.put_nowait('message')
    yield from test_consumer._connection_error_callback(Exception())
    for i in range(3):
        message = yield from test_consumer.read()
        assert message == 'message'
    with pytest.raises(Exception):
        yield from test_consumer.read()
