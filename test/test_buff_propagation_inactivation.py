import buffspecs

from test.test_data.buff_builder import BuffBuilder

from api import call_event, add_buff, pull_propagated_buffs, remove_buff
from models import Buffable, BuffSpec, Modifier, BuffEvent, BuffModification, BuffPropagatedEvent, AddBuffEvent
from test.test_data.specs import Player, Castle, CompleteBuildingEvent, FartEvent
from buffable import inactivate_buff

from test.test_data.specs import (
	Attributes
)

import unittest


class Test_Buff_Propagation_Inactivation(unittest.TestCase):

	def setUp(self):
		buffspecs.clear()

	def test_inactivating_propagation_target(self):
		player = Player()

		castle = Castle()
		castle.players.append(player)

		# A global castle buff of +50 ATK
		castle_buff = BuffBuilder().modify("+", 50, Attributes.ATK).propagates_to(Player).build()
		add_buff(castle, castle_buff, CompleteBuildingEvent())

		assert player.attributes[Attributes.ATK] == 50

		inactivate_buff(player, castle_buff, None)

		assert castle_buff.buff_id not in player.active_buffs
		assert len(player.activation_triggers) == 0
		assert player.attributes[Attributes.ATK] == 0

	def test_inactivating_propagator(self):
		player = Player()

		castle = Castle()
		castle.players.append(player)

		# A global castle buff of +50 ATK
		castle_buff = BuffBuilder().modify("+", 50, Attributes.ATK).propagates_to(Player).build()
		add_buff(castle, castle_buff, CompleteBuildingEvent())

		assert player.attributes[Attributes.ATK] == 50

		inactivate_buff(castle, castle_buff, None)

		assert player.attributes[Attributes.ATK] == 0

	def test_inactivating_propagation_target(self):
		player = Player()
		player.attributes[Attributes.HP] = 10

		castle = Castle()
		castle.players.append(player)

		# A global castle buff of +50 ATK
		castle_buff = BuffBuilder().modify("+", 50, Attributes.ATK).propagates_to(Player)\
			.whenever(FartEvent).just_if("is_healthy").build()

		@buffspecs.AddConditionFor([BuffEvent])
		def is_healthy(event):
			return event.buffable.attributes[Attributes.HP] > 0

		add_buff(castle, castle_buff, CompleteBuildingEvent())

		# Call the event triggering the buff
		call_event(FartEvent(player))

		assert player.attributes[Attributes.ATK] == 50

		inactivate_buff(player, castle_buff, None)

		assert player.attributes[Attributes.ATK] == 0
		assert castle_buff.buff_id not in player.active_buffs

		# Activation trigger should be registered because buff had a condition that can change
		assert len(player.activation_triggers["FartEvent"]) == 1



