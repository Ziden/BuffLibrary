import buffspecs

from test.test_data.buff_builder import BuffBuilder
from test.test_data.specs import Player, Equipment, CompleteBuildingEvent, Castle

from api import call_event, add_buff, pull_propagated_buffs, remove_buff
from models import Buffable, BuffSpec, Modifier, BuffEvent, BuffModification, BuffPropagatedEvent, AddBuffEvent


from test.test_data.specs import (
	Attributes
)


import unittest

class Test_Buff_Propagation_With_Derivation(unittest.TestCase):

	def setUp(self):
		buffspecs.clear()

	"""
	A derivated propagation is when a source buffable will propagate part of his own attributes to a
	propagation target. For instance a buffable that has 100 HP, propagating 50% of this value (50 HP)
	as a flat modifier to his propagation targets DEF attribute.
	"""

	def test_derivating_the_propagated_value(self):
		player = Player()
		player.attributes[Attributes.ATK] = 200

		equipment = Equipment()
		equipment.attributes[Attributes.ATK] = 100
		equipment.owner = player

		# 50% of equipment attack goes to player DEF
		equipment_buff_2 = BuffBuilder().modify("%", 0.5, Attributes.ATK)\
			.propagates_to_attribute(Attributes.DEF).propagates_to(Player).build()
		add_buff(equipment, equipment_buff_2, CompleteBuildingEvent())

		# Atk should not be modified
		assert player.attributes[Attributes.ATK] == 200

		# 50% of the EQUIPMENT ATK (100) should have gone to player DEF
		assert player.attributes[Attributes.DEF] == equipment.attributes[Attributes.ATK] * 0.5

		# Equipment should not be affected
		assert equipment.attributes[Attributes.ATK] == 100
		assert equipment.attributes[Attributes.DEF] == 0

		# Derivation should be stored in the target, not the propagator
		assert len(equipment.attributes.get_data(Attributes.ATK).derivations) == 0
		assert len(player.attributes.get_data(Attributes.ATK).derivations) == 1

	def test_removing_propagation_source(self):
		player = Player()
		player.attributes[Attributes.ATK] = 200

		equipment = Equipment()
		equipment.attributes[Attributes.ATK] = 100
		equipment.owner = player

		# 50% of equipment attack goes to player DEF
		equipment_buff_2 = BuffBuilder().modify("%", 0.5, Attributes.ATK) \
			.propagates_to_attribute(Attributes.DEF).propagates_to(Player).build()
		add_buff(equipment, equipment_buff_2, CompleteBuildingEvent())

		# 50% of the EQUIPMENT ATK (100) should have gone to player DEF
		assert player.attributes[Attributes.DEF] == equipment.attributes[Attributes.ATK] * 0.5

		# If we remove the propagation source, the propagation targets attributes needs to be updated
		remove_buff(equipment, equipment_buff_2.buff_id)
		assert player.attributes[Attributes.DEF] == 0

	def test_propagating_a_derivation_buff(self):
		player = Player()
		player.attributes[Attributes.ATK] = 50
		player.attributes[Attributes.DEF] = 75

		equipment = Equipment()
		equipment.attributes[Attributes.ATK] = 100
		equipment.owner = player

		castle = Castle()
		castle.players = [player]

		# 50% of player def becomes player HP
		add_buff(equipment,
				 BuffBuilder(1).modify("%", 0.5, Attributes.DEF).to_attribute(Attributes.HP) \
				 .propagates_to(Player).build(),
				 CompleteBuildingEvent()
				 )

		assert player.attributes[Attributes.DEF] == 75
		assert player.attributes[Attributes.HP] == 75 / 2

		# 50% of equipment attack goes to player DEF
		add_buff(equipment,
				 BuffBuilder(2).modify("%", 0.5, Attributes.ATK).propagates_to_attribute(Attributes.DEF) \
				 .propagates_to(Player).build(),
				 CompleteBuildingEvent()
				 )

		assert player.attributes[Attributes.DEF] == 125
		assert player.attributes[Attributes.HP] == 125 / 2

		# Remove the player DEF -> HP derivation
		remove_buff(equipment, 1)

		foka = (125 + 40 + 40 + 50) / 2
		asd = player.attributes[Attributes.HP]
		assert player.attributes[Attributes.DEF] == 125
		assert player.attributes[Attributes.HP] == 0

	def test_increasing_propagation_source_attribute_repropagates_derivation(self):
		player = Player()
		player.attributes[Attributes.ATK] = 200

		equipment = Equipment()
		equipment.attributes[Attributes.ATK] = 100
		equipment.owner = player

		# 50% of equipment attack goes to player DEF
		add_buff(equipment,
				 BuffBuilder().modify("%", 0.5, Attributes.ATK)\
				 .propagates_to_attribute(Attributes.DEF).propagates_to(Player).build(),
				 CompleteBuildingEvent()
				 )

		# 50% of the EQUIPMENT ATK (100) should have gone to player DEF
		assert equipment.attributes[Attributes.ATK] == 100
		assert player.attributes[Attributes.DEF] == equipment.attributes[Attributes.ATK] * 0.5

		# +100 to Equipment ATTACK, it should propagate 50% of it to player DEF
		add_buff(equipment,
				 BuffBuilder().modify("+", 100, Attributes.ATK).build(),
				 CompleteBuildingEvent()
				 )

		assert equipment.attributes[Attributes.ATK] == 200
		assert player.attributes[Attributes.DEF] == equipment.attributes[Attributes.ATK] * 0.5

	def test_chaining_propagation(self):
		player = Player()
		player.attributes[Attributes.ATK] = 100

		equipment = Equipment()
		equipment.attributes[Attributes.ATK] = 100
		equipment.owner = player

		# 50% of player DEF becomes player HP
		add_buff(equipment,
				 BuffBuilder().modify("%", 0.5, Attributes.DEF).to_attribute(Attributes.HP) \
				 .propagates_to(Player).build(),
				 CompleteBuildingEvent()
				 )

		# 50% of equipment attack goes to player DEF
		add_buff(equipment,
				 BuffBuilder().modify("%", 0.5, Attributes.ATK).propagates_to_attribute(Attributes.DEF) \
				 .propagates_to(Player).build(),
				 CompleteBuildingEvent()
				 )

		assert player.attributes[Attributes.DEF] == 50
		assert player.attributes[Attributes.HP] == 25


