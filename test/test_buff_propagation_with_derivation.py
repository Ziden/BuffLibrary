import buffspecs

from test.test_data.buff_builder import BuffBuilder

from controller import call_event, add_buff, pull_propagated_buffs, remove_buff
from models import Buffable, BuffSpec, Modifier, BuffEvent, BuffModification, BuffPropagatedEvent, AddBuffEvent


from test.test_data.test_specs import (
	Attributes
)

import unittest


class CompleteBuildingEvent(BuffEvent):
	def __init__(self):
		super(CompleteBuildingEvent, self).__init__(self)


class RecruitPlayerEvent(BuffEvent):
	def __init__(self, buffable):
		super(RecruitPlayerEvent, self).__init__(buffable)


class Castle(Buffable):
	def __init__(self):
		super(Castle, self).__init__()
		self.players = []


class Player(Buffable):
	def __init__(self):
		super(Player, self).__init__()
		self.castle = None


class Equipment(Buffable):
	def __init__(self):
		super(Equipment, self).__init__()
		self.owner = None


@buffspecs.AddPropagation(Castle, Player)
def castle_to_player_propagation(player_castle):
	return player_castle.players


@buffspecs.AddPropagation(Equipment, Player)
def equipment_to_player_propagation(equipment):
	return [equipment.owner]


class Test_Buff_Propagation_With_Derivation(unittest.TestCase):

	def test_propagating_a_derivation_buff(self):
		player = Player()
		player.attributes[Attributes.ATK] = 200

		equipment = Equipment()
		equipment.owner = player

		# 50% of equipment attack goes to player DEF
		equipment_buff_2 = BuffBuilder().modify("%", 0.5, Attributes.ATK).to_attribute(Attributes.DEF)\
			.propagates_to(Player).build()
		add_buff(equipment, equipment_buff_2, CompleteBuildingEvent())

		# 50% of the PLAYER ATK (100) should have gone to player DEF
		assert player.attributes[Attributes.DEF] == 100

		# Equipment should not be affected
		assert equipment.attributes[Attributes.ATK] == 0
		assert equipment.attributes[Attributes.DEF] == 0

		# Derivation should be stored in the target, not the propagator
		assert len(equipment.attributes.get_data(Attributes.ATK).derivations) == 0
		assert len(player.attributes.get_data(Attributes.ATK).derivations) == 1

	def test_removing_propagation_source(self):
		player = Player()
		player.attributes[Attributes.ATK] = 200

		equipment = Equipment()
		equipment.owner = player

		# 50% of equipment attack goes to player DEF
		equipment_buff_2 = BuffBuilder().modify("%", 0.5, Attributes.ATK).to_attribute(Attributes.DEF) \
			.propagates_to(Player).build()
		add_buff(equipment, equipment_buff_2, CompleteBuildingEvent())

		# 50% of the PLAYER ATK (100) should have gone to player DEF
		assert player.attributes[Attributes.DEF] == 100

		# If we remove the propagation source, the propagation target should be affected
		remove_buff(equipment, equipment_buff_2.buff_id)
		assert player.attributes[Attributes.DEF] == 0

	def test_changing_propagation_source_affecting_propagation_target(self):
		player = Player()
		player.attributes[Attributes.ATK] = 100

		equipment = Equipment()
		equipment.owner = player

		# Equipment buff that 50% of player ATK goes to player DEF
		equipment_buff_2 = BuffBuilder().modify("%", 0.5, Attributes.ATK) \
			.propagates_to(Player).to_attribute(Attributes.DEF).build()
		add_buff(equipment, equipment_buff_2, CompleteBuildingEvent())

		# 50% of the player ATK (100) should have gone to player DEF
		assert player.attributes[Attributes.DEF] == 50

		# Changing +100 ATK to player after propagating the derivation, should propagate another 50 to player DEF
		more_atk_buff = BuffBuilder().modify("+", 100, Attributes.ATK).build()
		add_buff(player, more_atk_buff, CompleteBuildingEvent())

		# more 50% of the total attack that is 200 now should be propagated to player DEF
		assert player.attributes[Attributes.DEF] == 100

