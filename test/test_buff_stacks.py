import buffspecs

from test.test_data.buff_builder import BuffBuilder
from test.test_data.specs import CompleteBuildingEvent, FartEvent

from buffs.api import call_event, add_buff, remove_buff
from buffs.models import Buffable, BuffSpec, Modifier, BuffEvent

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