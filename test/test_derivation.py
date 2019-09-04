import buffspecs

from test.test_data.buff_builder import BuffBuilder
from test.test_data.specs import CompleteBuildingEvent

from api import call_event, add_buff, remove_buff
from models import Buffable, BuffSpec, Modifier, BuffEvent, BuffModification, AddBuffEvent


from test.test_data.specs import (
	Attributes
)

import unittest

class Test_Buff_Derivations(unittest.TestCase):

	def setUp(self):
		buffspecs.clear()

	def test_simple_derivation(self):
		buffable = Buffable()
		buffable.attributes[Attributes.ATK] = 100

		# Simple buff that 50% of your attack goes to your def
		buff = BuffBuilder().modify("%", 0.5, Attributes.ATK).to_attribute(Attributes.DEF).build()
		add_buff(buffable, buff, CompleteBuildingEvent())

		# Player should have got 50% of his atk (50) to def
		assert buffable.attributes[Attributes.DEF] == 50
		assert buffable.attributes[Attributes.ATK] == 100
		assert buff.buff_id in buffable.active_buffs

		# Checking the derivation has been registered
		assert list(buffable.attributes.get_data(Attributes.ATK).derivations.keys())[0] == Attributes.DEF

	def test_derivation_debug_history(self):
		buffable = Buffable()
		buffable.attributes[Attributes.ATK] = 100
		buff = BuffBuilder().modify("%", 0.5, Attributes.ATK).to_attribute(Attributes.DEF).build()
		add_buff(buffable, buff, CompleteBuildingEvent())

		atk_modification_history = list(buffable.attributes.get_data(Attributes.DEF).history.values())
		last_modification = atk_modification_history[0]

		# The original modifier should be in history as well
		assert last_modification.modifier.value == 0.5
		assert last_modification.modifier.attribute_id == Attributes.ATK
		assert last_modification.modifier.operator == "%"

		# It should have created an modifier of 50% of user atk, since atk was 100, thats +50 DEF
		assert last_modification.derivated_modifier.value == 50
		assert last_modification.derivated_modifier.attribute_id == Attributes.DEF
		assert last_modification.derivated_modifier.operator == "+"

		assert last_modification.buff_id == buff.buff_id

		event_chain = last_modification.source_event.get_event_chain()
		assert isinstance(event_chain[0], AddBuffEvent)
		assert isinstance(event_chain[1], CompleteBuildingEvent)

	def test_changing_source_attribute_affects_derivated_attribute(self):
		buffable = Buffable()
		buffable.attributes[Attributes.ATK] = 100

		# Simple buff that 50% of your attack goes to your def
		buff = BuffBuilder().modify("%", 0.5, Attributes.ATK).to_attribute(Attributes.DEF).build()
		add_buff(buffable, buff, CompleteBuildingEvent())

		# Player should have got 50% of his atk (50) to def
		assert buffable.attributes[Attributes.DEF] == 50
		assert buffable.attributes[Attributes.ATK] == 100

		# Now we add +100 attack to the player, his 50% buff instead of giving 50 def should give 100 def
		buff_2 = BuffBuilder().modify("+", 100, Attributes.ATK).build()
		add_buff(buffable, buff_2, CompleteBuildingEvent())

		# Player defense should be updated as his attack increased
		assert buffable.attributes[Attributes.DEF] == 100
		assert buffable.attributes[Attributes.ATK] == 200
		
		# Now removing the buff should re-calculate the derivation as well
		remove_buff(buffable, buff_2.buff_id)

		# Player should have got 50% of his atk (50) to def as it should be derivating from 100 atk again
		assert buffable.attributes[Attributes.DEF] == 50
		assert buffable.attributes[Attributes.ATK] == 100

	def test_removing_derivation_buff_updates_derivated_attributes(self):
		buffable = Buffable()
		buffable.attributes[Attributes.ATK] = 100
		buffable.attributes[Attributes.DEF] = 100

		# Simple buff that 50% of your attack goes to your def
		buff = BuffBuilder().modify("%", 0.5, Attributes.ATK).to_attribute(Attributes.DEF).build()
		add_buff(buffable, buff, CompleteBuildingEvent())

		# 50% of your def, goes to your HP
		buff_2 = BuffBuilder().modify("%", 0.5, Attributes.DEF).to_attribute(Attributes.HP).build()
		add_buff(buffable, buff_2, CompleteBuildingEvent())

		# Player defense should be updated as his attack increased
		assert buffable.attributes[Attributes.DEF] == 150
		assert buffable.attributes[Attributes.HP] == 75

		remove_buff(buffable, buff.buff_id)

		assert buffable.attributes[Attributes.DEF] == 100
		assert buffable.attributes[Attributes.HP] == 50

