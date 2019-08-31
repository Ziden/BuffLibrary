import buffspecs

from test.test_data.buff_builder import BuffBuilder

from controller import call_event, add_buff, remove_buff
from models import Buffable, BuffSpec, Modifier, BuffEvent, BuffModification, AddBuffEvent


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


class Test_Buff_Derivations(unittest.TestCase):

	"""
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
		assert list(buffable.attributes.get_data(Attributes.ATK).derivations.keys())[0] == Attributes.ATK


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
	"""

	def test_changing_source_attribute_affecting_derivated_attribute(self):
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
		"""
		# Player defense should be updated as his attack increased
		assert buffable.attributes[Attributes.DEF] == 100
		assert buffable.attributes[Attributes.ATK] == 200
		
		# Now removing the buff should re-calculate the derivation as well
		remove_buff(buffable, buff_2.buff_id)

		# Player should have got 50% of his atk (50) to def as it should be derivating from 100 atk again
		assert buffable.attributes[Attributes.DEF] == 50
		assert buffable.attributes[Attributes.ATK] == 100
		"""
