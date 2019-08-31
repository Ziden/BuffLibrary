import buffspecs

from test.test_data.buff_builder import BuffBuilder

from buffs.controller import call_event, add_buff
from buffs.models import Buffable, BuffSpec, Modifier, BuffEvent, BuffModification


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
		self.equipments = []
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


class Test_Buff_Propagation_triggers(unittest.TestCase):

	def test_propagation_condition_and_trigger(self):
		player1 = Player()
		player1.attributes[Attributes.ATK] = 100

		castle = Castle()
		castle.players.append(player1)

		# A global castle buff that propagates that 50% ATK to players if a castle has 3 or more players
		castle_buff = BuffBuilder().modify("%", 0.5, Attributes.ATK)\
			.propagates_when(RecruitPlayerEvent).only_propagates_if("cond_has_qtd_players 2").propagates_to(Player).build()

		@buffspecs.AddConditionFor([BuffEvent])
		def cond_has_qtd_players(event, amt):
			return len(event.buffable.players) >= amt

		add_buff(castle, castle_buff, CompleteBuildingEvent())

		# The buff is not active on the player
		assert castle_buff.buff_id in castle.active_buffs
		assert castle_buff.buff_id not in player1.active_buffs

		# Castle should have registered the trigger
		assert "RecruitPlayerEvent" not in castle.activation_triggers
		assert "RecruitPlayerEvent" in castle.propagation_triggers

		# add another player to the castle
		player2 = Player()
		player2.attributes[Attributes.ATK] = 200

		castle.players.append(player2)
		call_event(RecruitPlayerEvent(castle))

		# Now that we matched the condition all 3 players should have been propagated and have 50% bonus
		assert player1.attributes[Attributes.ATK] == 100 * 1.5
		assert player2.attributes[Attributes.ATK] == 200 * 1.5

		# Adding a new player should propagate the buff to the new player as well
		player3 = Player()
		player3.attributes[Attributes.ATK] = 300
		castle.players.append(player3)
		call_event(RecruitPlayerEvent(castle))
		# Should not affect the other players
		assert player1.attributes[Attributes.ATK] == 100 * 1.5
		assert player2.attributes[Attributes.ATK] == 200 * 1.5
		# Should propagate to the new player
		assert player3.attributes[Attributes.ATK] == 300 * 1.5

