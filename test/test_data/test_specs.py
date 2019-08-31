from enum import Enum

from buffs.models import BuffEvent
from buffs.buffspecs import AddConditionFor

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
