from buffs.models import Buffable, Modifier, BuffModification

from test.test_data.specs import CompleteBuildingEvent

from attributes import apply_attributes_modification

from test.test_data.specs import (
	Attributes
)

import unittest


class Test_2_Modifiers(unittest.TestCase):

	def setUp(self):
		pass
		# buffspecs.clear()

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
		source_event = CompleteBuildingEvent()

		apply_attributes_modification(attributes, BuffModification(Modifier("+", 25, Attributes.ATK), source_event))
		apply_attributes_modification(attributes, BuffModification(Modifier("%", 1.00, Attributes.ATK), source_event))
		apply_attributes_modification(attributes, BuffModification(Modifier("%", 1.00, Attributes.ATK), source_event))
		assert buffable.attributes[Attributes.ATK] == 75

		# Checking if we has history of those 3 modifications
		attribute_history = list(buffable.attributes.get_data(Attributes.ATK).history.values())

		assert attribute_history[0].modifier.operator == "+"
		assert attribute_history[0].modifier.value == 25
		assert attribute_history[0].modifier.attribute_id == Attributes.ATK
		assert attribute_history[0].source_event == source_event

		assert attribute_history[1].modifier.operator == "%"
		assert attribute_history[1].modifier.value == 1.00
		assert attribute_history[1].modifier.attribute_id == Attributes.ATK
		assert attribute_history[1].source_event == source_event

		assert attribute_history[2].modifier.operator == "%"
		assert attribute_history[2].modifier.value == 1.00
		assert attribute_history[2].modifier.attribute_id == Attributes.ATK
		assert attribute_history[2].source_event == source_event
