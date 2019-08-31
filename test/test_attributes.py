
from buffs.models import BuffableAttributes, Buffable, BuffSpec, Modifier, BuffCondition, BuffModification
from buffs.buffspecs import register_buff

from test.test_data.test_specs import (
	Attributes
)

from buffs.models import Attribute

import unittest


class Test_Attributes(unittest.TestCase):

	def test_buffable_force_attributes_setter(self):
		buffable = Buffable()

		# Forcing an attribute final value to be 10
		buffable.attributes[Attributes.MAX_HP] = 10

		attr_data = buffable.attributes.get_data(Attributes.MAX_HP)
		assert attr_data.final_value == 10
		assert attr_data.mod_add == 10  # Automatically granted 10 of the add modifier
		assert attr_data.mod_pct == 0   # no bonus pct

	def test_pct_modifier(self):
		buffable = Buffable()
		buffable.attributes[Attributes.MAX_HP] = 10

		attr_data = buffable.attributes.get_data(Attributes.MAX_HP)
		assert attr_data.final_value == 10

		# Adding 50% bonus to the the attribute modifiers
		attr_data.mod_mult = 0.5
		attr_data.calculate()

		# +10 + 50% of that (5) is 15
		assert attr_data.final_value == 15
		assert attr_data.mod_add == 10
		assert attr_data.mod_mult == 0.5
