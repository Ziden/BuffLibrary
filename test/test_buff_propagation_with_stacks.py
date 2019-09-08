import buffspecs

from test.test_data.buff_builder import BuffBuilder

from api import call_event, add_buff, pull_propagated_buffs, remove_buff
from models import Buffable, BuffSpec, Modifier, BuffEvent, BuffModification, BuffPropagatedEvent, AddBuffEvent
from test.test_data.specs import Player, Castle, CompleteBuildingEvent, Equipment, RecruitPlayerEvent

from buffable import inactivate_buff

from test.test_data.specs import (
	Attributes
)

import unittest


class Test_Buff_Propagation(unittest.TestCase):

	def setUp(self):
		buffspecs.clear()

	def test_propagation_with_stacks(self):
		player = Player()

		castle = Castle()
		castle.players.append(player)

		# A global castle buff of +50 ATK
		castle_buff = BuffBuilder().modify("+", 50, Attributes.ATK).propagates_to(Player).stacks(3).build()

		# Add the first stack
		add_buff(castle, castle_buff, CompleteBuildingEvent())
		assert player.attributes[Attributes.ATK] == 50
		assert player.active_buffs[castle_buff.buff_id].stack == 1
		assert castle.active_buffs[castle_buff.buff_id].stack == 1

		# Add a second stack
		add_buff(castle, castle_buff, CompleteBuildingEvent())

		assert player.active_buffs[castle_buff.buff_id].stack == 2
		assert castle.active_buffs[castle_buff.buff_id].stack == 2
		assert player.attributes[Attributes.ATK] == 100

		# Add a the third stack
		add_buff(castle, castle_buff, CompleteBuildingEvent())
		assert player.attributes[Attributes.ATK] == 150

		# An extra stack should not propagate the buff anymore
		add_buff(castle, castle_buff, CompleteBuildingEvent())
		assert player.attributes[Attributes.ATK] == 150

	def test_inactivating_propagated_buff_stack_from_source(self):
		player = Player()

		castle = Castle()
		castle.players.append(player)

		# A global castle buff of +50 ATK
		castle_buff = BuffBuilder().modify("+", 50, Attributes.ATK).propagates_to(Player).stacks(3).build()

		# Add thre stacks of the buff
		add_buff(castle, castle_buff, CompleteBuildingEvent())
		add_buff(castle, castle_buff, CompleteBuildingEvent())
		add_buff(castle, castle_buff, CompleteBuildingEvent())
		assert player.attributes[Attributes.ATK] == 150

		# Stacks are added both to source as well to propagation target
		assert player.active_buffs[castle_buff.buff_id].stack == 3
		assert castle.active_buffs[castle_buff.buff_id].stack == 3

		inactivate_buff(castle, castle_buff, None)

		assert player.attributes[Attributes.ATK] == 100
		assert castle.active_buffs[castle_buff.buff_id].stack == 2
		assert player.active_buffs[castle_buff.buff_id].stack == 2

