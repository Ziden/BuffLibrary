import buffspecs
from debug.strack_tracer import TrackStack

from models import Buffable
from test.test_data.buff_builder import BuffBuilder
from test.test_data.specs import CompleteBuildingEvent

from api import add_buff

from test.test_data.specs import (
    Attributes
)

import unittest


class Test_Buff_Propagation_With_Derivation(unittest.TestCase):

    def setUp(self):
        buffspecs.clear()

    def test_propagating_a_derivation_buff(self):

        # Simple derivation buff
        buffable = Buffable()
        buffable.attributes[Attributes.ATK] = 100
        buff = BuffBuilder().modify("%", 0.5, Attributes.ATK).to_attribute(Attributes.DEF).build()

        # We want to track the performance of this
        with TrackStack() as track:

            add_buff(buffable, buff, CompleteBuildingEvent())

            #print(track)
