import buffspecs

from test.test_data.buff_builder import BuffBuilder
from test.test_data.specs import CompleteBuildingEvent, FartEvent

from api import call_event, add_buff, remove_buff
from models import Buffable, BuffSpec, Modifier, BuffEvent
from expiry import FixedTime, get_timestamp, get_expired_buffs, clear_fixed_time

from test.test_data.specs import (
	Attributes
)

import unittest


class Test_3_Buffs(unittest.TestCase):

	def setUp(self):
		buffspecs.clear()

	def tearDown(self):
		clear_fixed_time()

	def test_adding_buff(self):
		buffable = Buffable()

		buff = BuffSpec(1)
		buff.activation_triggers = []  # no triggers
		buff.conditions = []  # no conditions
		buff.max_stack = 3    # 3 stacks max
		buff.modifiers = [Modifier("+", 10, Attributes.DEF)]

		# Add the buff
		add_buff(buffable, buff,  CompleteBuildingEvent())

		# Since it has no triggers or conditions, it was added automatically
		assert buffable.attributes[Attributes.DEF] == 10
		assert buff.buff_id in buffable.active_buffs
		assert buffable.active_buffs[buff.buff_id].stack == 1

		# Add the buff again, should be in 2 stacks now
		add_buff(buffable, buff, CompleteBuildingEvent())
		assert buffable.attributes[Attributes.DEF] == 20
		assert buffable.active_buffs[buff.buff_id].stack == 2

		# Add the buff again, should be in 2 stacks now
		add_buff(buffable, buff, CompleteBuildingEvent())
		assert buffable.attributes[Attributes.DEF] == 30
		assert buffable.active_buffs[buff.buff_id].stack == 3

		# Now we reached our max stack, it should always be 3 stacks.
		add_buff(buffable, buff, CompleteBuildingEvent())
		assert buffable.attributes[Attributes.DEF] == 30
		assert buffable.active_buffs[buff.buff_id].stack == 3

		# If we remove the buff, all stacks should be removed
		remove_buff(buffable, 1)
		assert buffable.attributes[Attributes.DEF] == 0
		assert buff.buff_id not in buffable.active_buffs

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

			# Add the buff 3 stacks
			add_buff(buffable, buff, CompleteBuildingEvent())
			add_buff(buffable, buff, CompleteBuildingEvent())
			add_buff(buffable, buff, CompleteBuildingEvent())

			with FixedTime(expiry_time):

				expired_buffs = list(get_expired_buffs(buffable))
				assert len(expired_buffs) == 3

				# Calling expired buffs should have removed them from expiry list
				assert len(buffable.expiry_times) == 0

	def test_buff_stack_with_expiry_all_at_once(self):
		buffable = Buffable()

		buff = BuffSpec()
		buff.activation_triggers = []  # no triggers
		buff.conditions = []  # no conditions
		buff.max_stack = 3    # 3 stacks max#
		buff.duration_seconds = 10
		buff.modifiers = [Modifier("+", 10, Attributes.DEF)]

		with FixedTime(get_timestamp()):

			expiry_time = get_timestamp() + buff.duration_seconds

			# Add the buff for full 3 stacks
			add_buff(buffable, buff, CompleteBuildingEvent())
			add_buff(buffable, buff, CompleteBuildingEvent())
			add_buff(buffable, buff, CompleteBuildingEvent())

			assert buffable.attributes[Attributes.DEF] == 30
			assert buffable.active_buffs[buff.buff_id].stack == 3
			assert len(buffable.expiry_times) == 3

			with FixedTime(expiry_time):

				assert buffable.attributes[Attributes.DEF] == 0
				assert len(buffable.expiry_times) == 0
				assert buff.buff_id not in buffable.active_buffs


