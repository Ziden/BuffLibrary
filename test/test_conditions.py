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
	def __init__(self, buffable, damage):
		super(DamageEvent, self).__init__(buffable)
		self.damage = damage


class Test_4_Conditions(unittest.TestCase):

	def test_basic_condition_failing(self):
		buffable = Buffable()
		buff = BuffSpec()
		buff.activation_triggers = {}  # no triggers
		buff.conditions = ["cond_is_blue_yellow"]
		buff.buff_id = 5
		buff.modifiers = [Modifier("+", 30, Attributes.DEF)]
		buffspecs.register_buff(buff)

		# A condition that can be triggered by a MockEvent
		@buffspecs.AddConditionFor([CompleteBuildingEvent])
		def cond_is_blue_yellow(event):
			return False

		add_buff(buffable, buff, CompleteBuildingEvent())

		# This buff should not be applied
		assert buff.buff_id not in buffable.active_buffs

	def test_negating_condition(self):
		buffable = Buffable()
		buff = BuffSpec()
		buff.activation_triggers = {}  # no triggers
		buff.conditions = ["not cond_is_blue_yellow"]
		buff.buff_id = 5
		buff.modifiers = [Modifier("+", 30, Attributes.DEF)]
		buffspecs.register_buff(buff)

		@buffspecs.AddConditionFor([CompleteBuildingEvent])
		def cond_is_blue_yellow(event):
			return False

		add_buff(buffable, buff, CompleteBuildingEvent())

		# This buff should be be applied as the condition was negated
		assert buff.buff_id in buffable.active_buffs

	def test_condition_switching_buff(self):
		buffable = Buffable()
		buff = BuffSpec()
		buff.activation_triggers = ["DamageEvent"]
		buff.deactivation_triggers = ["DamageEvent"]
		buff.conditions = ["is_burning"]
		buff.buff_id = 5
		buff.modifiers = [Modifier("+", 30, Attributes.DEF)]
		buffspecs.register_buff(buff)

		buffable.attributes["Burning"] = 0  # example to set a state, not burning

		@buffspecs.AddConditionFor([DamageEvent])
		def is_burning(event):
			return event.buffable.attributes["Burning"] == 1

		# Add the buff
		add_buff(buffable, buff, CompleteBuildingEvent())

		# The buff should not be applied because the buffable is not burning
		assert buff.buff_id not in buffable.active_buffs
		assert buffable.attributes[Attributes.DEF] == 0

		# Now make it burn
		damage = 10
		buffable.attributes["Burning"] = 1
		call_event(DamageEvent(buffable, damage))

		# Now the buff should have applied
		assert buff.buff_id in buffable.active_buffs
		assert buffable.attributes[Attributes.DEF] == 30

		# And we should have added the remove trigger
		assert buff.buff_id in buffable.deactivation_triggers["DamageEvent"]
		# Buff history contains this modification
		assert len(buffable.attributes.get_data(Attributes.DEF).history) == 1

		# Now After calling the other event the buff should be removed
		buffable.attributes["Burning"] = 0
		call_event(DamageEvent(buffable, damage))

		# Now the buff should be removed
		assert buff.buff_id not in buffable.active_buffs
		assert buff.buff_id not in buffable.deactivation_triggers
		assert buffable.attributes[Attributes.DEF] == 0

		# And the trigger should be added again and the remove trigger should be removed
		assert buff.buff_id not in buffable.deactivation_triggers["DamageEvent"]
		assert buff.buff_id in buffable.activation_triggers["DamageEvent"]
		# Also the modification history is removed because this buff is inactive and not modifyng anything
		assert len(buffable.attributes.get_data(Attributes.DEF).history) == 0
		
		# In case we burn again...
		buffable.attributes["Burning"] = 1
		call_event(DamageEvent(buffable, damage))

		# Buff is activated again
		assert buff.buff_id in buffable.active_buffs
		assert buffable.attributes[Attributes.DEF] == 30

	def test_condition_parameters(self):
		buffable = Buffable()
		buff = BuffSpec()
		buff.activation_triggers = ["DamageEvent"]
		buff.deactivation_triggers = ["DamageEvent"]
		buff.conditions = ["is_damage_higher_then 10"]  # condition parameters after condition name
		buff.buff_id = 5
		buff.modifiers = [Modifier("+", 30, Attributes.DEF)]
		buffspecs.register_buff(buff)

		@buffspecs.AddConditionFor([DamageEvent])
		def is_damage_higher_then(event, param):
			return event.damage > param

		# Add the buff
		add_buff(buffable, buff, CompleteBuildingEvent())

		# Damage lower then condition threshhold
		call_event(DamageEvent(buffable, 8))

		# Buff should not have been activated
		assert buff.buff_id not in buffable.active_buffs
		assert buffable.attributes[Attributes.DEF] == 0

		# Now a damage higher
		call_event(DamageEvent(buffable, 12))
		# Buff should have been activated
		assert buff.buff_id in buffable.active_buffs
		assert buffable.attributes[Attributes.DEF] == 30

	def test_reuse_conditions_with_abstraction(self):
		# Lets say our game has an economy, of multiple types of coins.
		example_coin_types = [
			"gold", "silver", "copper"
		]

		class EconomyEvent(BuffEvent):
			def __init__(self, buffable, coin_type_changed, coin_amount):
				super(EconomyEvent, self).__init__(buffable)
				self.coin_type_changed = coin_type_changed
				self.coin_amount = coin_amount

		# The player can get coins by mining for instance
		class PlayerMineCoinsEvent(EconomyEvent):
			def __init__(self, buffable, coin_type_changed, coin_amount):
				super(PlayerMineCoinsEvent, self).__init__(buffable, coin_type_changed, coin_amount)

		# The player can also get coins by looting enemies
		class PlayerLootEnemyEvent(EconomyEvent):
			def __init__(self, buffable, coin_type_changed, coin_amount):
				super(PlayerLootEnemyEvent, self).__init__(buffable, coin_type_changed, coin_amount)

		# Now this condition works for any economy event generically
		@buffspecs.AddConditionFor([EconomyEvent])
		def is_coin_type(event, *coin_types):
			return event.coin_type_changed in coin_types

		# Now we create a buff that
		buffable = Buffable()

		# Making a buff that gives player DEF when if he mines a gold coin
		bdr = BuffBuilder().modify("+", 5, Attributes.DEF).whenever(PlayerMineCoinsEvent).just_if("is_coin_type gold")
		bonus_mine_gold_buff = bdr.build()

		# Making a buff that gives player ATK if he loots silver or copper coins
		bdr = BuffBuilder().modify("+", 5, Attributes.ATK).whenever(PlayerLootEnemyEvent).just_if(
			"is_coin_type copper silver"  # Multiple parameters in the condition
		)
		bonus_loot_copper_silver_buff = bdr.build()

		# Add the buffs
		add_buff(buffable, bonus_loot_copper_silver_buff, CompleteBuildingEvent())
		add_buff(buffable, bonus_mine_gold_buff, CompleteBuildingEvent())

		# Now we mine some silver
		call_event(PlayerMineCoinsEvent(buffable, "silver", 10))

		# No buffs should be applied as no conditions matched
		assert len(buffable.active_buffs) == 0

		# Now he mines gold, should activate the buff cause the condition matched
		call_event(PlayerMineCoinsEvent(buffable, "gold", 10))
		assert bonus_mine_gold_buff.buff_id in buffable.active_buffs

		# Now he will loot gold, condition should not match
		call_event(PlayerLootEnemyEvent(buffable, "gold", 10))
		assert bonus_loot_copper_silver_buff.buff_id not in buffable.active_buffs

		# Now he finally loots silver or copper (in this case, silver) and the buff should apply
		call_event(PlayerLootEnemyEvent(buffable, "silver", 10))
		assert bonus_loot_copper_silver_buff.buff_id in buffable.active_buffs

