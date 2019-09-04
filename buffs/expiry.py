import buffspecs

from debug import strack_tracer

import time
import sys


@strack_tracer.Track
def register_expiry_time(buffable, buff_spec):
    """ If this buff has an expiry time, register the expiry time on this buffable

    :param Buffable buffable:
    :param BuffSpec buff_spec:
    """
    if buff_spec.duration_seconds != -1:
        now = get_timestamp()
        expires_at = now + buff_spec.duration_seconds
        _add_expiry_time_to_fifo_list(buffable, expires_at, buff_spec.buff_id)


@strack_tracer.Track
def get_expired_buffs(buffable):
    """ Get a generator of all buffs that already have expired and removes them from the expiry list.

    :param Buffable buffable:
    :rtype: generator[BuffSpec]
    """
    while buffable.expiry_times and get_timestamp() >= _get_next_expiry_time(buffable):
        next_expiry_time, buff_id = buffable.expiry_times.pop(0)
        yield buffspecs.get_buff_spec(buff_id)


def _get_next_expiry_time(buffable):
    """ Gets the next expiry time to happen (the lowest value one)

    :param Buffable buffable:
    :return:  A timestamp when the buff will expire
    :rtype: int
    """
    if buffable.expiry_times:
        return buffable.expiry_times[0][0]


@strack_tracer.Track
def _add_expiry_time_to_fifo_list(buffable, expiry_time_to_add, buff_id_to_add):
    """ Adds an expiry time to the expiry time list. It will add lower expiry times earlier in order, so the
        first element is always the next to expire.

    :param Buffable buffable:
    :param int expiry_time_to_add:
    :param int buff_id_to_add:
    """
    index = len(buffable.expiry_times)
    for i in range(len(buffable.expiry_times)):
        expiry_time, buff_id = buffable.expiry_times[i]
        if expiry_time_to_add < expiry_time:
            index = i
            break
    expiry_time = (expiry_time_to_add, buff_id_to_add)
    buffable.expiry_times.insert(index, expiry_time)


def get_timestamp():
    """ Gets current timestamp

    :return:  Current time in seconds
    :rtype: int
    """
    if _mock_time:
        return _mock_time[-1]
    return time.time()


_mock_time = []


class MockTime(object):
    def __init__(self, time):
        self.time = time

    def __enter__(self):
       _mock_time.append(self.time)

    def __exit__(self, exc_type, exc_val, exc_tb):
       _mock_time.remove(self.time)

