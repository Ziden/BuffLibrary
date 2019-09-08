import buffspecs
from mock import patch, MagicMock

from test.test_data.buff_builder import BuffBuilder
from test.test_data.specs import CompleteBuildingEvent, FartEvent

from buffs.api import call_event, add_buff, remove_buff
from buffs.models import Buffable, BuffSpec, Modifier, BuffEvent

from expiry import get_timestamp, FixedTime, _get_next_expiry_time, get_expired_buffs, clear_fixed_time

from test.test_data.specs import (
	Attributes
)

import unittest


class Test_3_Buffs(unittest.TestCase):

	def setUp(self):
		buffspecs.clear()

	def tearDown(self):
		clear_fixed_time()

	"""
	def test_adding_buff(self):
		buffable = Buffable()

		buff = BuffSpec(1)
		buff.activation_triggers = []  # no triggers
		buff.conditions = []  # no conditions
		buff.duration_seconds = 10  # Only lasts for 10 seconds
		buff.modifiers = [Modifier("+", 50, Attributes.DEF)]

		with FixedTime(get_timestamp()):
			# Add the buff
			expiry_time = get_timestamp() + 10

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

		with FixedTime(expiry_time):
			# Simply by reading the attribute we will expire that buff
			assert buffable.attributes[Attributes.DEF] == 0
			# Should not be an active buff anymore
			assert buff.buff_id not in buffable.active_buffs
			# Expiry time and activation triggers should be gone as we do not want to reactivate this buff
			assert len(buffable.expiry_times) == 0
			assert len(buffable.activation_triggers) == 0

	def test_registering_1_expiry_per_stack(self):
		buffable = Buffable()

		buff = BuffSpec(1)
		buff.activation_triggers = []  # no triggers
		buff.conditions = []  # no conditions
		buff.duration_seconds = 10  # Only lasts for 10 seconds
		buff.max_stack = 2
		buff.modifiers = [Modifier("+", 50, Attributes.DEF)]

		# Add the buff 2 times
		add_buff(buffable, buff, CompleteBuildingEvent())
		add_buff(buffable, buff, CompleteBuildingEvent())

		# Should have registered one expiry time per stack
		assert buffable.attributes[Attributes.DEF] == 100
		assert buffable.active_buffs[buff.buff_id].stack == 2
		assert len(buffable.expiry_times) == 2

	def test_expiring_stacks(self):
		buffable = Buffable()

		buff = BuffSpec(1)
		buff.activation_triggers = []  # no triggers
		buff.conditions = []  # no conditions
		buff.duration_seconds = 10  # Only lasts for 10 seconds
		buff.max_stack = 2
		buff.modifiers = [Modifier("+", 50, Attributes.DEF)]

		# Add the buff 2 times, one in the future
		add_buff(buffable, buff, CompleteBuildingEvent())
		with FixedTime(get_timestamp() + 5):
			add_buff(buffable, buff, CompleteBuildingEvent())

		expiry_time_1 = get_timestamp() + buff.duration_seconds
		expiry_time_2 = expiry_time_1 + 5

		assert buffable.attributes[Attributes.DEF] == 100
		assert buffable.active_buffs[buff.buff_id].stack == 2
		assert len(buffable.expiry_times) == 2

		with FixedTime(expiry_time_1):
			assert buffable.attributes[Attributes.DEF] == 50
			assert buffable.active_buffs[buff.buff_id].stack == 1
			assert len(buffable.expiry_times) == 1

		with FixedTime(expiry_time_2):
			assert buffable.attributes[Attributes.DEF] == 0
			assert buff.buff_id not in buffable.active_buffs
			assert len(buffable.expiry_times) == 0

	"""
	def test_next_to_expire(self):
		buffable = Buffable()

		buff = BuffSpec()
		buff.activation_triggers = []  # no triggers
		buff.conditions = []  # no conditions
		buff.duration_seconds = 10  # Only lasts for 10 seconds
		buff.max_stack = 3
		buff.modifiers = [Modifier("+", 50, Attributes.DEF)]

		with FixedTime(get_timestamp()):

			expiry_time = get_timestamp() + buff.duration_seconds

			# Add the buff
			add_buff(buffable, buff, CompleteBuildingEvent())
			add_buff(buffable, buff, CompleteBuildingEvent())
			add_buff(buffable, buff, CompleteBuildingEvent())

			assert _get_next_expiry_time(buffable) == expiry_time

			expired_buffs = list(get_expired_buffs(buffable))
			assert len(expired_buffs) == 0

			with FixedTime(expiry_time):

				expired_buffs = list(get_expired_buffs(buffable))
				assert len(expired_buffs) == 3

				# Calling expired buffs should have removed them from expiry list
				assert len(buffable.expiry_times) == 0


