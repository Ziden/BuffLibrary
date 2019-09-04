import buffspecs

from models import *

from test.test_data.buff_builder import BuffBuilder
from test.test_data.specs import Castle, Player, Equipment, CompleteBuildingEvent

from api import call_event, add_buff, remove_buff

from test.test_data.specs import (
    Attributes
)

import unittest
import random

class Test_Buff_Propagation_With_Derivation(unittest.TestCase):

    def setUp(self):
        buffspecs.clear()

    def test_performance(self):

        player1 = Player()
        player1_equips = []
        for i in range(10):
          equip = Equipment()
          equip.owner = player1
          player1_equips.append(equip)

        player2 = Player()
        player2_equips = []
        for i in range(10):
          equip = Equipment()
          equip.owner = player2
          player2_equips.append(equip)

        castle = Castle()
        castle.players = [player1, player2]

        seed = 1234

        random.seed(seed)

        buff_targets = {}

        for i in range(10):

            builder = BuffBuilder()
            modifier = random_modifier()
            builder.modify(*modifier)

            propagates = False

            apply_to, propagate_to = random_targets()

            if chance_pct(25):
                builder.to_attribute(random_attribute(exlude=modifier[2]))

            if chance_pct(25):
                propagates = True
                builder.propagates_to_attribute(random_attribute())

            #builder.propagates_to()


def chance_pct(pct):
    return pct >= random.randrange(0, 100)


def random_targets():
    possible_targets = [Player, Equipment, Castle]
    apply_on = random.choice(possible_targets)

    if apply_on == Player:
        possible_targets = []

    if apply_on == Castle:
        possible_targets = [Player, Equipment]

    if apply_on == Equipment:
        possible_targets = [Player]

    propagate_to = None
    if possible_targets:
        propagate_to = random.choice(possible_targets)
    return apply_on, propagate_to

def random_attribute(exlude=None):
    attrs = list(Attributes)
    if exlude:
        attrs.remove(exlude)
    return random.choice(attrs)


def random_modifier():
    op = "+"
    attribute_id = random_attribute()
    value = random.randrange(1, 150)
    if bool(random.getrandbits(1)):
        op = "%"
        value = value / 100
    return op, value, attribute_id



