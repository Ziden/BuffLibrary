from buffs.models import BuffableAttributes, Buffable, BuffSpec, Modifier, BuffCondition, BuffModification, BuffEvent
from buffs.buffspecs import register_buff

from controller import apply_attributes_modification

from test.test_data.test_specs import (
	Attributes
)

import unittest


# Example Event
class BuildingCompleteEvent(BuffEvent):
	def __init__(self, building_name):
		super(BuildingCompleteEvent, self).__init__(self)
		self.building_name = building_name


class Test_2_Modifiers(unittest.TestCase):

	def test_apply_modifiers_not_cumulative(self):
		buffable = Buffable()
		attributes = buffable.attributes
		# +25 ATK
		apply_attributes_modification(attributes, BuffModification(Modifier("+", 25, Attributes.ATK)))
		assert buffable.attributes[Attributes.ATK] == 25

		# 100% Bonus Atk
		apply_attributes_modification(attributes, BuffModification(Modifier("%", 1.00, Attributes.ATK)))
		assert buffable.attributes[Attributes.ATK] == 50

		# 100% Bonus Atk Again
		apply_attributes_modification(attributes, BuffModification(Modifier("%", 1.00, Attributes.ATK)))
		assert buffable.attributes[Attributes.ATK] == 75

	def test_modification_history(self):
		buffable = Buffable()
		attributes = buffable.attributes

		# Create an event with fake event data
		barracks = "barracks"
		source_event = BuildingCompleteEvent(barracks)

		apply_attributes_modification(attributes, BuffModification(Modifier("+", 25, Attributes.ATK), source_event))
		apply_attributes_modification(attributes, BuffModification(Modifier("%", 1.00, Attributes.ATK), source_event))
		apply_attributes_modification(attributes, BuffModification(Modifier("%", 1.00, Attributes.ATK), source_event))
		assert buffable.attributes[Attributes.ATK] == 75

		# Checking if we has history of those 3 modifications
		attribute_history = list(buffable.attributes.get_data(Attributes.ATK).history.values())

		assert attribute_history[0].modifier.operator == "+"
		assert attribute_history[0].modifier.value == 25
		assert attribute_history[0].modifier.attribute_id == Attributes.ATK
		assert attribute_history[0].source_event.building_name == source_event.building_name

		assert attribute_history[1].modifier.operator == "%"
		assert attribute_history[1].modifier.value == 1.00
		assert attribute_history[1].modifier.attribute_id == Attributes.ATK
		assert attribute_history[1].source_event.building_name == source_event.building_name

		assert attribute_history[2].modifier.operator == "%"
		assert attribute_history[2].modifier.value == 1.00
		assert attribute_history[2].modifier.attribute_id == Attributes.ATK
		assert attribute_history[2].source_event.building_name == source_event.building_name
