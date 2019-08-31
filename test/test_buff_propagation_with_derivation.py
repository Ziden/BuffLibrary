import buffspecs

from test.test_data.buff_builder import BuffBuilder

from controller import call_event, add_buff, pull_propagated_buffs
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

	def test_basic_propagation_with_derivation(self):
		player = Player()
		player.attributes[Attributes.ATK] = 100

		equipment = Equipment()
		equipment.owner = player

		equipment.attributes[Attributes.ATK] = 100
		# +100 ATK to equipment
		#equipment_buff_1 = BuffBuilder().modify("+", 100, Attributes.ATK).build()

		# 50% of equipment attack goes to player DEF
		equipment_buff_2 = BuffBuilder().modify("%", 0.5, Attributes.ATK)\
			.propagates_to(Player).to_attribute(Attributes.DEF).build()

		#add_buff(equipment, equipment_buff_1, CompleteBuildingEvent())
		add_buff(equipment, equipment_buff_2, CompleteBuildingEvent())

		# 50% of the item ATK (100) should have gone to player DEF
		assert player.attributes[Attributes.DEF] == 50
		assert player.attributes[Attributes.ATK] == 100  # initial atk
		assert equipment.attributes[Attributes.DEF] == 0  # should not be affected

		# Now we add another buff giving more atk to the equipment
		equipment_buff_3 = BuffBuilder().modify("+", 100, Attributes.ATK).build()
		add_buff(equipment, equipment_buff_3, CompleteBuildingEvent())

		assert player.attributes[Attributes.DEF] == 100