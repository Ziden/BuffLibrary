from collections import defaultdict
from utils.dict_magic import defaultdictlist
import buffspecs
from enum import Enum
import uuid


class Attribute(object):
	def __init__(self, mod_add=0, mod_mult=0):
		self.mod_add = mod_add
		self.mod_mult = mod_mult
		self.final_value = 0
		self.history = {}
		self.derivations = defaultdictlist()

	def calculate(self):
		self.final_value = self.mod_add * (1 + self.mod_mult)


class BuffableAttributes(object):
	def __init__(self):
		self.attribute_data = defaultdict(Attribute)

	def __getitem__(self, attribute_id):
		return self.attribute_data[attribute_id].final_value

	def __setitem__(self, attribute_id, raw_value):
		self.attribute_data[attribute_id].mod_add = raw_value
		self.attribute_data[attribute_id].mod_pct = 0
		self.attribute_data[attribute_id].calculate()

	def get_data(self, attribute_id):
		return self.attribute_data[attribute_id]


class TriggerType(object):
	ACTIVATION = 1
	DEACTIVATION = 2
	PROPAGATION = 3


class BuffSpec(object):
	def __init__(self, spec_id=None, name=None):
		self.buff_id = spec_id or buffspecs.IDGen.next()
		self.modifiers = []
		self.conditions = []
		self.activation_triggers = []
		self.deactivation_triggers = []
		self.propagation_triggers = []
		self.to_attribute = None
		self.propagates_to_attribute = None
		self.propagates_to = []
		self.propagation_conditions = []
		self.name = name
		buffspecs.register_buff(self)

	@property
	def propagates(self):
		return len(self.propagates_to) > 0

	@property
	def auto_triggers(self):
		return len(self.activation_triggers) == 0

	def can_target(self, target_name):
		return not self.propagates or target_name in self.propagates_to

	def get_remove_triggers(self):
		if len(self.conditions) > 0 and len(self.deactivation_triggers) == 0:
			return self.activation_triggers # if i have conditions by default my remove trigger is the activation trigger
		return self.deactivation_triggers

	def get_triggers(self):
		if len(self.activation_triggers) == 0:
			return ["AddBuffEvent"]
		return self.activation_triggers
		#return self.activation_triggers + ["AddBuffEvent"] # Default trigger, buff is triggered as soon its adde

	def get_propagation_triggers(self):
		if len(self.propagation_triggers) == 0:
			return ["AddBuffEvent"]  # Default trigger, buff is triggered as soon its added
		return self.propagation_triggers


class BuffModification(object):
	def __init__(self, modifier, source_event=None, buff_id=None, derivated_modifier=None):
		self.id = uuid.uuid1()
		self.buff_id = buff_id
		self.source_event = source_event
		self.modifier = modifier
		self.derivated_modifier = derivated_modifier


class ActiveBuff(object):
	def __init__(self, buff_id, source_event):
		self.source_event = source_event
		self.buff_id = buff_id


class BuffCondition(object):
	def __init__(self, condition_function, parameter=None):
		self.condition_name = condition_function.__name__
		self.parameter = parameter


class Buffable(object):
	def __init__(self):
		self.id = 0  # your game identification
		self.attributes = BuffableAttributes()
		self.active_buffs = {}
		self.activation_triggers = defaultdictlist()
		self.deactivation_triggers = defaultdictlist()
		self.propagation_triggers = defaultdictlist()

	@property
	def name(self):
		return self.__class__.__name__


class Modifier(object):
	def __init__(self, operator, value, attribute_id):
		self.attribute_id = attribute_id
		self.value = value
		self.operator = operator


class BuffEvent(object):
	def __init__(self, buffable):
		self.buffable = buffable

	def get_name(self):
		return self.__class__.__name__

	def get_event_chain(self, event_chain=None):
		if not isinstance(self, _InternalChainEvent):
			return [self]

		if not event_chain:
			event_chain = [self]
		if self.trigger_event:
			event_chain.append(self.trigger_event)
			self = self.trigger_event
			self.get_event_chain(event_chain)
		return event_chain


class _InternalChainEvent(BuffEvent):
	def __init__(self, buffable, trigger_event):
		super(_InternalChainEvent, self).__init__(buffable)
		self.trigger_event = trigger_event


class AddBuffEvent(_InternalChainEvent):
	def __init__(self, buffable, buff_id, trigger_event):
		super(AddBuffEvent, self).__init__(buffable, trigger_event)
		self.buff_id = buff_id


class BuffPropagatedEvent(_InternalChainEvent):
	def __init__(self, buffable, source_buffable, buff_id, trigger_event):
		super(BuffPropagatedEvent, self).__init__(buffable, trigger_event)
		self.buff_id = buff_id
		self.source_buffable = source_buffable


class EventResult(object):
    def __init__(self):
        self.added_modifications = []
        self.removed_modifications = []
        self.propagated_modifications = defaultdict(list)
