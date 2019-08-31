import buffspecs

from buffs.controller import call_event, add_buff
from buffs.models import Buffable, BuffSpec, Modifier, BuffEvent
from test.test_data.buff_builder import BuffBuilder

from test.test_data.test_specs import (
	Attributes
)

import unittest


class CompleteBuildingEvent(BuffEvent):
	def __init__(self):
		super(CompleteBuildingEvent, self).__init__(self)


class DamageEvent(BuffEvent):
	def __init__(self, buffable):
		super(DamageEvent, self).__init__(buffable)


class Test_Buff_Dependency(unittest.TestCase):

	def test_basic_buff_dependency(self):
		buffable = Buffable()

		buff_id_1 = 1
		buff_id_2 = 2

		buff_1 = BuffBuilder().modify("+", 50, Attributes.ATK).just_if("has_buff 2").build()
		buff_2 = BuffBuilder().modify("+", 50, Attributes.ATK).build()

		# A condition that can be triggered by a MockEvent
		@buffspecs.AddConditionFor([BuffEvent])
		def has_buff(event, buff_id):
			return buff_id in event.buffable.active_buffs

		add_buff(buffable, buff_1, CompleteBuildingEvent())

		# Player should not be modified because he did not have buff 2
		assert buffable.attributes[Attributes.ATK] == 0

		# Adding the second buff should trigger the first one because his condidion matched
		add_buff(buffable, buff_2, CompleteBuildingEvent())

		# Both buffs should be applied now
		assert buffable.attributes[Attributes.ATK] == 100
		assert buff_id_1 in buffable.active_buffs
		assert buff_id_2 in buffable.active_buffs

	def test_buff_cancelling_when_other_buff_triggering(self):
		buffable = Buffable()

		buff_id_1 = 1
		buff_id_2 = 2

		buff_1 = BuffBuilder(buff_id_1).modify("+", 50, Attributes.ATK).whenever(DamageEvent)\
			.just_if("not has_buff 2").build()
		buff_2 = BuffBuilder(buff_id_2).modify("+", 75, Attributes.ATK).whenever(DamageEvent).build()

		# A condition that can be triggered by a MockEvent
		@buffspecs.AddConditionFor([BuffEvent])
		def has_buff(event, buff_id):
			return buff_id in event.buffable.active_buffs

		add_buff(buffable, buff_1, CompleteBuildingEvent())
		call_event(DamageEvent(buffable))

		# Player does not have buff 2 so he should be getting buff 1
		assert buffable.attributes[Attributes.ATK] == 50
		assert buff_id_1 in buffable.active_buffs

		add_buff(buffable, buff_2, CompleteBuildingEvent())
		call_event(DamageEvent(buffable))

		# Now that he got buff 2 applied, buff 1 should be removed and only buff 2 is applied
		assert buffable.attributes[Attributes.ATK] == 75
		assert buff_id_1 not in buffable.active_buffs
		assert buff_id_2 in buffable.active_buffs
