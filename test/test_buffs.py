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

		buff = BuffSpec()
		buff.activation_triggers = []  # no triggers
		buff.conditions = []  # no conditions
		buff.modifiers = [Modifier("+", 30, Attributes.DEF)]

		# Add the buff
		add_buff(buffable, buff,  CompleteBuildingEvent())

		# Since it has no triggers or conditions, it was added automatically
		assert buffable.attributes[Attributes.DEF] == 30
		assert buff.buff_id in buffable.active_buffs

	def test_removing_buff(self):
		buffable = Buffable()
		buffable.attributes[Attributes.ATK] = 100

		buff = BuffSpec()
		buff.modifiers = [Modifier("%", 0.5, Attributes.ATK)]

		add_buff(buffable, buff, CompleteBuildingEvent())

		assert buffable.attributes[Attributes.ATK] == 150

		remove_buff(buffable, buff.buff_id)

		assert buffable.attributes[Attributes.ATK] == 100
		assert buff.buff_id not in buffable.active_buffs

	def test_buff_modification_history(self):
		buffable = Buffable()

		buff = BuffSpec()
		buff.modifiers = [Modifier("+", 30, Attributes.DEF)]

		# Faking an event that would result in adding a buff
		event_to_get_the_buff = CompleteBuildingEvent()

		# Add the buff
		event_result = add_buff(buffable, buff, event_to_get_the_buff)
		added_modifications = event_result.added_modifications
		# Check modification history to debug/backtrack
		assert added_modifications[0].modifier.operator == "+"
		assert added_modifications[0].modifier.attribute_id == Attributes.DEF
		assert added_modifications[0].source_event.trigger_event == event_to_get_the_buff

	def test_adding_multiple_modifiers(self):
		buffable = Buffable()

		buff = BuffSpec()
		buff.activation_triggers = []  # no triggers
		buff.conditions = []  		   # no conditions
		buff.modifiers = [
			Modifier("+", 50, Attributes.DEF),
			Modifier("+", 50, Attributes.DEF),
			Modifier("%", 0.5, Attributes.DEF)
		]
		buffspecs.register_buff(buff)  # Add buff to registry

		# Adding a possible buff
		add_buff(buffable, buff, CompleteBuildingEvent())

		# +50 +50 + 50% is 100 + 50% = 150
		asd = buffable.attributes.get_data(Attributes.DEF)
		assert buffable.attributes[Attributes.DEF] == 150

	def test_buff_trigger(self):
		buffable = Buffable()
		buff = BuffSpec()
		buff.activation_triggers = ["FartEvent"]
		buff.conditions = []
		buff.buff_id = 5
		buff.modifiers = [Modifier("+", 30, Attributes.DEF)]
		buffspecs.register_buff(buff)

		add_buff(buffable, buff, CompleteBuildingEvent())

		# The buff was not triggered yet as "FartEvent" was not called
		assert buffable.attributes[Attributes.DEF] == 0
		# Instead, we did not added a buff, we just added a trigger for a buff
		assert "FartEvent" in buffable.activation_triggers

		# Now we call the event
		call_event(FartEvent(buffable))

		# Now the buff should be added
		assert buffable.attributes[Attributes.DEF] == 30
		# And the trigger removed
		assert "FartEvent" not in buffable.activation_triggers

	def test_buff_event_modifications_log(self):
		buffable = Buffable()

		# Building a buff with the builder
		buff = BuffBuilder().modify("+", 5, Attributes.ATK).whenever(FartEvent).build()
		add_buff(buffable, buff, CompleteBuildingEvent())

		fart_event = FartEvent(buffable)
		event_result = call_event(fart_event)
		modifications = event_result.added_modifications

		# Check if the event returns the correct modifications that happened
		assert len(modifications) == 1
		assert modifications[0].buff_id == buff.buff_id
		assert modifications[0].source_event == fart_event
		assert modifications[0].modifier.operator == "+"
		assert modifications[0].modifier.value == 5
		assert modifications[0].modifier.attribute_id == Attributes.ATK