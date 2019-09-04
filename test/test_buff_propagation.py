import buffspecs

from test.test_data.buff_builder import BuffBuilder

from api import call_event, add_buff, pull_propagated_buffs, remove_buff
from models import Buffable, BuffSpec, Modifier, BuffEvent, BuffModification, BuffPropagatedEvent, AddBuffEvent
from test.test_data.specs import Player, Castle, CompleteBuildingEvent, Equipment, RecruitPlayerEvent

from test.test_data.specs import (
	Attributes
)

import unittest


class Test_Buff_Propagation(unittest.TestCase):

	def setUp(self):
		buffspecs.clear()

	def test_simple_propagation(self):
		player = Player()
		player.attributes[Attributes.ATK] = 100

		castle = Castle()
		castle.players.append(player)

		# A global castle buff of +50 ATK
		castle_buff = BuffBuilder().modify("+", 50, Attributes.ATK).propagates_to(Player).build()

		add_buff(castle, castle_buff, CompleteBuildingEvent())

		# The buff should be active in the owner and target
		assert castle_buff.buff_id in castle.active_buffs
		assert castle_buff.buff_id in player.active_buffs

		# Since castle buffs are propagated to the players in that castle, the player should have got +50% ATK
		assert player.attributes[Attributes.ATK] == 150
		# However even tho the castle has this buff as active, since its not a target it did not change ATK
		assert castle.attributes[Attributes.ATK] == 0

	"""
	def test_propagation_also_modifyng_source(self):
		player = Player()
		player.attributes[Attributes.ATK] = 100

		castle = Castle()
		castle.players.append(player)

		# A global castle buff of +50 ATK but also affects the castle
		castle_buff = BuffBuilder().modify("+", 50, Attributes.ATK)\
			.propagates_to(Player, Castle).build()

		add_buff(castle, castle_buff, CompleteBuildingEvent())

		# The buff should be active in the owner and target
		assert castle_buff.buff_id in castle.active_buffs
		assert castle_buff.buff_id in player.active_buffs

		# Since castle buffs are propagated to the players in that castle, the player should have got +50% ATK
		assert player.attributes[Attributes.ATK] == 150
		# However even tho the castle has this buff as active, since its not a target it did not change ATK
		assert castle.attributes[Attributes.ATK] == 50

	def test_removing_propagation(self):
		player = Player()
		player.attributes[Attributes.ATK] = 100

		castle_buff = BuffBuilder().modify("%", 0.5, Attributes.ATK).propagates_to(Player).build()

		castle = Castle()
		castle.players.append(player)

		add_buff(castle, castle_buff, CompleteBuildingEvent())
		assert player.attributes[Attributes.ATK] == 150

		remove_buff(castle, castle_buff.buff_id)
		assert player.attributes[Attributes.ATK] == 100

	def test_propagation_debug_tracking(self):
		player = Player()
		player.attributes[Attributes.ATK] = 100

		castle = Castle()
		castle.players.append(player)

		# A global castle buff of 50% ATK
		castle_buff = BuffBuilder().modify("%", 0.5, Attributes.ATK).propagates_to(Player).build()
		event_result = add_buff(castle, castle_buff, CompleteBuildingEvent())

		# The event result should let us know about the propagation
		propagated_modifications = event_result.propagated_modifications
		added_modifications_on_propagation = propagated_modifications[player.id][0].added_modifications[0]

		# We also have the history in the attribute modification history
		attribute_history_modification = list(player.attributes.get_data(Attributes.ATK).history.values())[0]

		for modification in [added_modifications_on_propagation, attribute_history_modification]:

			# Asserting this stored the modifier correctly
			assert modification.modifier.value == 0.5
			assert modification.modifier.operator == "%"
			assert modification.modifier.attribute_id == Attributes.ATK

			# Asserting the buff chain, we added a buff, caused a propagation to add a buff in another buffable
			event_chain = modification.source_event.get_event_chain()
			assert isinstance(event_chain[0], AddBuffEvent)

			assert isinstance(event_chain[1], BuffPropagatedEvent)
			assert event_chain[1].source_buffable == castle

			assert isinstance(event_chain[2], AddBuffEvent)
			assert isinstance(event_chain[3], CompleteBuildingEvent)

	def test_double_propagation(self):
		player = Player()
		player.attributes[Attributes.ATK] = 100

		castle = Castle()
		castle.players.append(player)

		equipment = Equipment()
		equipment.owner = player

		# A global castle buff of 50% ATK
		castle_buff = BuffBuilder().modify("%", 0.5, Attributes.ATK).propagates_to(Player).build()
		# Equipment buff of 100% bonus atk
		equipment_buff = BuffBuilder().modify("%", 1, Attributes.ATK).propagates_to(Player).build()

		add_buff(castle, castle_buff, CompleteBuildingEvent())
		add_buff(equipment, equipment_buff, CompleteBuildingEvent())

		assert len(player.active_buffs) == 2
		# flat bonus = 100, 250% total bonus from propagations, so 250 final value
		assert player.attributes[Attributes.ATK] == 250

	def test_propating_two_targets(self):
		player = Player()
		player.attributes[Attributes.ATK] = 100

		castle = Castle()
		player.castle = castle
		castle.players.append(player)

		# A global castle buff of bonus coins collected that can affect both players and castles
		castle_buff = BuffBuilder().modify("+", 10, Attributes.BONUS_COINS_COLLECTED).propagates_to(Player, Castle).build()
		add_buff(castle, castle_buff, CompleteBuildingEvent())

		# Both players and castles shall have bonus coins collected
		assert player.attributes[Attributes.BONUS_COINS_COLLECTED] == 10
		assert castle.attributes[Attributes.BONUS_COINS_COLLECTED] == 10

	def test_propagation_with_triggers(self):
		player = Player()
		player.attributes[Attributes.ATK] = 100

		# A global castle buff of 50% ATK
		castle_buff = BuffBuilder().modify("%", 0.5, Attributes.ATK)\
			.propagates_when(RecruitPlayerEvent).propagates_to(Player).build()

		castle = Castle()
		castle.players.append(player)

		add_buff(castle, castle_buff, CompleteBuildingEvent())

		# Castle should have a propagation trigger not a activation trigger
		assert castle_buff.buff_id not in castle.activation_triggers["RecruitPlayerEvent"]
		assert castle_buff.buff_id in castle.propagation_triggers["RecruitPlayerEvent"]

		# Event was not triggered, so player should not get modified
		assert player.attributes[Attributes.ATK] == 100

		# Now we trigger the event and expect the propagation to happen
		call_event(RecruitPlayerEvent(castle))

		# Now the buff should have been applied
		assert player.attributes[Attributes.ATK] == 150
		assert castle_buff.buff_id in player.active_buffs
		assert castle_buff.buff_id in castle.active_buffs

		# The propagation trigger should not consumed
		assert castle_buff.buff_id in castle.propagation_triggers["RecruitPlayerEvent"]

	def test_pulling_propagated_buffs(self):
		player = Player()
		player.attributes[Attributes.ATK] = 100

		castle_buff = BuffBuilder().modify("%", 0.5, Attributes.ATK).propagates_to(Player).build()

		castle = Castle()
		castle.players.append(player)

		add_buff(castle, castle_buff, CompleteBuildingEvent())

		# First player should be updated
		assert player.attributes[Attributes.ATK] == 150

		# Adding another player
		player2 = Player()
		player2.attributes[Attributes.ATK] = 100

		# We can enforce a propagation to happen in case we just created a new buffable and we have "global buffs"
		pull_propagated_buffs(castle, player2, CompleteBuildingEvent())

		# Player should have pulled the propagation from his castle
		assert player2.attributes[Attributes.ATK] == 150

	def test_propagation_wont_duplicate_buffs(self):
		player = Player()
		player.attributes[Attributes.ATK] = 100

		castle_buff = BuffBuilder().modify("%", 0.5, Attributes.ATK) \
			.propagates_when(RecruitPlayerEvent).propagates_to(Player).build()

		castle = Castle()
		castle.players.append(player)

		add_buff(castle, castle_buff, CompleteBuildingEvent())

		# Trigger the event twice
		call_event(RecruitPlayerEvent(castle))
		call_event(RecruitPlayerEvent(castle))

		# The propagation should have happened only once
		assert len(player.active_buffs) == 1
		assert player.attributes[Attributes.ATK] == 150
	"""