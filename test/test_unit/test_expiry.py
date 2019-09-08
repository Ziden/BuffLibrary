import unittest
import buffspecs

from mock import Mock
from expiry import register_expiry_time, get_timestamp, get_expired_buffs, FixedTime, _add_expiry_time_to_fifo_list


class Test_Expiry(unittest.TestCase):

    def setUp(self):
        buffspecs.clear()
        self.buffable = Mock()
        self.buffable.expiry_times = []

        self.buff_spec = Mock()
        self.buff_spec.buff_id = 1
        self.buff_spec.duration_seconds = 15
        buffspecs.register_buff(self.buff_spec)

    def test_registering_expiries(self):
        register_expiry_time(self.buffable, self.buff_spec)

        next_expiry_time, buff_id = self.buffable.expiry_times[0]

        assert next_expiry_time == get_timestamp() + self.buff_spec.duration_seconds
        assert buff_id == self.buff_spec.buff_id

    def test_getting_expired_buffs(self):
        register_expiry_time(self.buffable, self.buff_spec)

        assert len(list(get_expired_buffs(self.buffable))) == 0

        with FixedTime(get_timestamp() + self.buff_spec.duration_seconds):
            assert len(list(get_expired_buffs(self.buffable))) == 1

    def test_getting_expired_buffs_removing_from_expired_list(self):
        register_expiry_time(self.buffable, self.buff_spec)

        assert len(self.buffable.expiry_times) == 1

        with FixedTime(get_timestamp() + self.buff_spec.duration_seconds):

            # Run the generator
            list(get_expired_buffs(self.buffable))

            assert len(self.buffable.expiry_times) == 0

    def test_expiry_time_is_fifo(self):

        expiry_times_to_add = [1, 6, 3, 5, 2, 4, 7, 9, 0, 8]

        for i in range(len(expiry_times_to_add)):
            buff_id = i + 100
            expiry_time = expiry_times_to_add[i]
            _add_expiry_time_to_fifo_list(self.buffable, expiry_time, buff_id)

        # Check if we stored in FIFO order (lowest expiry first)
        for i in range(len(expiry_times_to_add)):
            expiry_time, buff_id = self.buffable.expiry_times[i]
            assert expiry_time == i

