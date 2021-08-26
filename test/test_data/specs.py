from enum import Enum

from buffs.models import BuffEvent, Buffable
import buffspecs

"""
This file contains the data that is provided to the buff library as an example. 
The goal is that the user of the library has to implement
attributes, events and conditions. This means using the attributes in some way, calling the events when
necesary and implementing conditional functions for the events implemented.
"""


##############
# ATTRIBUTES #
##############

class Attributes(Enum):
	MAX_HP = 1
	HP = 2
	ATK = 3
	DEF = 4
	CRIT_CHANCE = 5
	CRIT_DAMAGE = 6
	BONUS_COINS_COLLECTED = 7

#############
# BUFFABLES #
#############

class Castle(Buffable):
	def __init__(self):
		super(Castle, self).__init__()
		self.players = []


class Player(Buffable):
	def __init__(self):
		super(Player, self).__init__()
		self.castle = None


class Equipment(Buffable):
	def __init__(self):
		super(Equipment, self).__init__()
		self.owner = None


####################
# PROPAGATION MAPS #
####################

@buffspecs.AddPropagation(Castle, Player)
def castle_to_player_propagation(player_castle):
	return player_castle.players


@buffspecs.AddPropagation(Equipment, Player)
def equipment_to_player_propagation(equipment):
	return [equipment.owner]

##########
# EVENTS #
##########


class FartEvent(BuffEvent):
	def __init__(self, buffable):
		super(FartEvent, self).__init__(buffable)


class CompleteBuildingEvent(BuffEvent):
	def __init__(self):
		super(CompleteBuildingEvent, self).__init__(self)


class RecruitPlayerEvent(BuffEvent):
	def __init__(self, buffable):
		super(RecruitPlayerEvent, self).__init__(buffable)


class CompleteBuildingEvent(BuffEvent):
	def __init__(self):
		super(CompleteBuildingEvent, self).__init__(self)


class DamageEvent(BuffEvent):
	def __init__(self, buffable):
		super(DamageEvent, self).__init__(buffable)

