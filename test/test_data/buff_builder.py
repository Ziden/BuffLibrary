from models import BuffSpec, Modifier
import buffspecs


class BuffBuilder():
    
    def __init__(self, id=None):
        self.buff_spec = BuffSpec(id)

    def modify(self, operator, value, modifier):
        self.buff_spec.modifiers.append(Modifier(operator, value, modifier))
        return self

    def whenever(self, event_class):
        self.buff_spec.activation_triggers.append(event_class.__name__)
        return self

    def to_attribute(self, attribute):
        self.buff_spec.to_attribute = attribute
        return self

    def propagates_to_attribute(self, attribute):
        self.buff_spec.propagates_to_attribute = attribute
        return self

    def just_if(self, condition):
        self.buff_spec.conditions.append(condition)
        return self

    def only_propagates_if(self, condition):
        self.buff_spec.propagation_conditions.append(condition)
        return self

    def stacks(self, stack):
        self.buff_spec.max_stack = stack
        return self

    def propagates_when(self, event_class):
        self.buff_spec.propagation_triggers.append(event_class.__name__)
        return self

    def propagates_to(self, *buffable_classes):
        for buffable_class in buffable_classes:
            self.buff_spec.propagates_to.append(buffable_class.__name__)
        return self

    def build(self):
        buffspecs.register_buff(self.buff_spec)
        return self.buff_spec