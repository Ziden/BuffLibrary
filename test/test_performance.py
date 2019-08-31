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


class Test_Performance(unittest.TestCase):

    def test_performance(self):
        player = Player()

        player_buffs = []
        initial_stat_value = 100
        player_initial_stats = BuffSpec()
        player_initial_stats.modifiers = [
            Modifier("+", initial_stat_value, Attributes.ATK),
            Modifier("+", initial_stat_value, Attributes.MAX_HP),
            Modifier("+", initial_stat_value, Attributes.DEF),
            Modifier("+", initial_stat_value, Attributes.CRIT_CHANCE),
            Modifier("+", initial_stat_value, Attributes.CRIT_DAMAGE),
            Modifier("+", initial_stat_value, Attributes.HP),
        ]
        player_buffs.append(player_initial_stats)

        # 50% ATK to DEF
        player_buffs.append(BuffBuilder().modify("%", 0.5, Attributes.ATK).to_attribute(Attributes.DEF).build())
        # 250% bonus ATK
        player_buffs.append(BuffBuilder().modify("%", 1.5, Attributes.ATK).build())

        for buff in player_buffs:
            add_buff(player, buff, CompleteBuildingEvent())

        # TODO: Finish this





