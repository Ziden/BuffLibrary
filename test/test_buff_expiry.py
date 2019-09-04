import buffspecs
from mock import patch, MagicMock

from test.test_data.buff_builder import BuffBuilder
from test.test_data.specs import CompleteBuildingEvent, FartEvent

from buffs.api import call_event, add_buff, remove_buff
from buffs.models import Buffable, BuffSpec, Modifier, BuffEvent

from expiry import _add_expiry_time_to_fifo_list, get_timestamp, MockTime

from test.test_data.specs import (
	Attributes
)

import unittest


class Test_3_Buffs(unittest.TestCase):

	def setUp(self):
		buffspecs.clear()

	def test_adding_buff(self):
		buffable = Buffable()

		buff = BuffSpec(1)
		buff.activation_triggers = []  # no triggers
		buff.conditions = []  # no conditions
		buff.duration_seconds = 10  # Only lasts for 10 seconds
		buff.modifiers = [Modifier("+", 50, Attributes.DEF)]

		expiry_time = get_timestamp() + 10

		# Add the buff
		add_buff(buffable, buff,  CompleteBuildingEvent())

		# Since it has no triggers or conditions, it was added automatically
		assert buffable.attributes[Attributes.DEF] == 50
		assert buff.buff_id in buffable.active_buffs

		# Check the expiry time was registered
		registered_expiry_time, buff_id = buffable.expiry_times[0]
		assert registered_expiry_time == expiry_time
		assert buff_id == buff.buff_id

	def test_buff_expiring(self):
		buffable = Buffable()

		buff = BuffSpec(1)
		buff.activation_triggers = []  # no triggers
		buff.conditions = []  # no conditions
		buff.duration_seconds = 10  # Only lasts for 10 seconds
		buff.modifiers = [Modifier("+", 50, Attributes.DEF)]

		expiry_time = get_timestamp() + buff.duration_seconds

		# Add the buff
		add_buff(buffable, buff,  CompleteBuildingEvent())

		assert buffable.attributes[Attributes.DEF] == 50

		with MockTime(expiry_time):
			# Simply by reading the attribute we will expire that buff
			assert buffable.attributes[Attributes.DEF] == 0
			# Should not be an active buff anymore
			assert buff.buff_id not in buffable.active_buffs
			# Expiry time and activation triggers should be gone as we do not want to reactivate this buff
			assert len(buffable.expiry_times) == 0
			assert len(buffable.activation_triggers) == 0

	def test_expiry_time_fifo(self):
		buffable = Buffable()

		expiry_times_to_add = [1,6,3,5,2,4,7,9,0,8]

		for i in range(len(expiry_times_to_add)):
			buff_id = i+100
			expiry_time = expiry_times_to_add[i]
			_add_expiry_time_to_fifo_list(buffable, expiry_time, buff_id)

		# Check if we stored in FIFO order (lowest expiry first)
		for i in range(len(expiry_times_to_add)):
			expiry_time, buff_id = buffable.expiry_times[i]
			assert expiry_time == i