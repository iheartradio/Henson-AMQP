import queue

import pytest


def test_disconnect_consumer(test_consumer):
    """Test disconnect logic for consumers."""
    test_consumer._message_queue = queue.Queue()
    test_consumer._message_queue.put_nowait('message')
    test_consumer._message_queue.put_nowait('message')
    test_consumer._message_queue.put_nowait('message')
    test_consumer._connection_error_callback(Exception())
    for i in range(3):
        message = test_consumer.read()
        assert message == 'message'
    with pytest.raises(Exception):
        test_consumer.read()
