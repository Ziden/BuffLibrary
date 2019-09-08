import buffspecs
from debug.strack_tracer import TrackStack

from test.test_data.buff_builder import BuffBuilder
from test.test_data.specs import Castle, Player, Equipment, CompleteBuildingEvent

from api import call_event, add_buff, remove_buff

from test.test_data.specs import (
    Attributes
)

import unittest


"""
Personal test. If only this test fails after a change, slap me, means test coverage is shit.
"""


class Test_Buff_Propagation_With_Derivation(unittest.TestCase):

    def setUp(self):
        buffspecs.clear()

    def test_propagating_a_derivation_buff(self):
        player = Player()
        player.attributes[Attributes.ATK] = 50
        player.attributes[Attributes.DEF] = 75

        equipment = Equipment()
        equipment.attributes[Attributes.ATK] = 100
        equipment.owner = player

        castle = Castle()
        castle.players = [player]

        # 50% of player def becomes player HP
        add_buff(equipment,
                 BuffBuilder(1).modify("%", 0.5, Attributes.DEF).to_attribute(Attributes.HP) \
                 .propagates_to(Player).build(),
                 CompleteBuildingEvent()
                 )

        assert player.attributes[Attributes.HP] == 75 / 2

        # 50% of equipment attack goes to player DEF
        add_buff(equipment,
                 BuffBuilder(2).modify("%", 0.5, Attributes.ATK).propagates_to_attribute(Attributes.DEF)\
                 .propagates_to(Player).build(),
                 CompleteBuildingEvent()
        )

        assert player.attributes[Attributes.DEF] == 125
        assert player.attributes[Attributes.HP] == 125 / 2

        # 25% of castle DEF becomes player DEF
        add_buff(castle,
                 BuffBuilder(3).modify("%", 0.5, Attributes.DEF).propagates_to_attribute(Attributes.DEF) \
                 .propagates_to(Player).build(),
                 CompleteBuildingEvent()
                 )

        assert castle.attributes[Attributes.DEF] == 0
        assert player.attributes[Attributes.DEF] == 125
        assert player.attributes[Attributes.HP] == 125 / 2

        # Castle buff of +80 DEF, 50% should derivate to player
        add_buff(castle,
                 BuffBuilder(4).modify("+", 80, Attributes.DEF).build(),
                 CompleteBuildingEvent()
                 )

        assert castle.attributes[Attributes.DEF] == 80
        assert player.attributes[Attributes.DEF] == 125+40
        assert player.attributes[Attributes.HP] == (125+40) / 2

        # Another Castle buff of +80 DEF, 50% should derivate to player
        add_buff(castle,
                 BuffBuilder(5).modify("+", 80, Attributes.DEF).build(),
                 CompleteBuildingEvent()
                 )

        assert castle.attributes[Attributes.DEF] == 80 + 80
        assert player.attributes[Attributes.DEF] == 125 + 40 + 40
        assert player.attributes[Attributes.HP] == (125 + 40 + 40) / 2

        # Just bumping player + 100 ATK. To remember:
        add_buff(equipment,
                 BuffBuilder(6).modify("+", 100, Attributes.ATK).build(),
                 CompleteBuildingEvent()
                 )

        assert castle.attributes[Attributes.DEF] == 80 + 80
        assert player.attributes[Attributes.DEF] == 125 + 40 + 40 + 50
        assert player.attributes[Attributes.HP] == (125 + 40 + 40 + 50) / 2

        # 100% of castle DEF goes to player HP
        add_buff(castle,
                 BuffBuilder(7).modify("%", 1, Attributes.DEF).propagates_to_attribute(Attributes.HP)
                 .propagates_to(Player).build(),
                 CompleteBuildingEvent()
                 )

        assert castle.attributes[Attributes.DEF] == 80 + 80
        assert player.attributes[Attributes.DEF] == 125 + 40 + 40 + 50
        assert player.attributes[Attributes.HP] == ((125 + 40 + 40 + 50) / 2) + castle.attributes[Attributes.DEF]

        # 50% of HP to CRIT_DAMAGE on player
        add_buff(player,
                 BuffBuilder(8).modify("%", 0.5, Attributes.HP).to_attribute(Attributes.CRIT_DAMAGE).build(),
                 CompleteBuildingEvent()
                 )

        assert player.attributes[Attributes.HP] == ((125 + 40 + 40 + 50) / 2) + castle.attributes[Attributes.DEF]
        assert player.attributes[Attributes.CRIT_DAMAGE] == player.attributes[Attributes.HP] / 2
        assert castle.attributes[Attributes.DEF] == 80 + 80
        assert player.attributes[Attributes.DEF] == 125 + 40 + 40 + 50

        with TrackStack() as track:

            # 50% of castle def to player def
            add_buff(castle,
                 BuffBuilder(9).modify("%", 0.5, Attributes.DEF).propagates_to_attribute(Attributes.DEF) \
                 .propagates_to(Player).build(),
                 CompleteBuildingEvent()
            )

            # Printing the stack, this buff should trigger a 4 step derivation chain 
            track.print_stack()

            assert player.attributes[Attributes.DEF] == 125 + 40 + 40 + 50 + 80
            assert player.attributes[Attributes.HP] == ((125 + 40 + 40 + 50 + 80) / 2) + castle.attributes[Attributes.DEF]
            assert player.attributes[Attributes.CRIT_DAMAGE] == player.attributes[Attributes.HP] / 2
            assert castle.attributes[Attributes.DEF] == 80 + 80
