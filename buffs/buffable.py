from debug import strack_tracer
import buffspecs

from models import BuffModification, ActiveBuff
from utils.arrays import delete_triggers, copy_triggers

from propagation import get_propagation_source, get_propagation_target_buffables
from attributes import get_all_buff_modifications, remove_attribute_modification, apply_attributes_modification
from derivation import create_derivation_modifier, update_derivated_attributes
from expiry import get_timestamp, register_expiry_time, get_expired_buffs


@strack_tracer.Track
def create_buff_modifications(buffable, buff_id, source_event, current_stack=1):
    """ Generates a list of buff modifications a buff will have to apply a buffable.
    Buff modifications are changes that can be applied to attributes as a whole.
    This list contains all changes that will update the buffable attributes.

    :param Buffable buffable:
    :param int buff_id:
    :param BuffEvent source_event:
    :param int current-stack:
    :rtype: list[BuffModification]
    """
    modifications = []
    buff_spec = buffspecs.get_buff_spec(buff_id)
    for modifier in buff_spec.modifiers:
        buff_modification = BuffModification(modifier, source_event, buff_id)

        # In case this derivates to another attribute we need to generate the derivation modifier
        # This modifier contains the calculated derivated value as a "flat add" modifier to the derivated attribute.
        if buff_spec.to_attribute:
            buff_modification.derivated_modifier = create_derivation_modifier(
                buffable.attributes, modifier, buff_spec.to_attribute
            )

        # If this buff propagates an derived attribute from a buffable to another, we need to calculate the
        # derived value based on the propagator source and not this buffable
        if buff_spec.propagates_to_attribute:
            source_buffable = get_propagation_source(source_event)
            buff_modification.derivated_modifier = create_derivation_modifier(
                source_buffable.attributes, modifier, buff_spec.propagates_to_attribute
            )

        buff_modification.stack_count = current_stack
        modifications.append(buff_modification)
    return modifications


@strack_tracer.Track
def get_attributes(buffable):
    """ Check if there is any expired buffs on this buffable, then return the attributes.

    :param Buffable buffable:
    :rtype: BuffableAttributes
    """
    for buff_spec in get_expired_buffs(buffable):
        inactivate_buff(buffable, buff_spec, None)

        # If this buff has not activation triggers he should never be activated again if expired
        if not buff_spec.activation_triggers:
            delete_triggers(buff_spec.buff_id, buff_spec.get_triggers(), buffable.activation_triggers)

    return buffable._attributes


def has_reached_max_stacks(buffable, buff_spec):
    """ Checks if a buff has reached max stack count.

    :param Buffable buffable:
    :param BuffSpec buff_spec:
    :rtype: bool
    """
    if buff_spec.buff_id in buffable.active_buffs:
        active_buff = buffable.active_buffs[buff_spec.buff_id]
        if active_buff.stack >= buff_spec.max_stack:
            return True
    return False


@strack_tracer.Track
def activate_buff(buffable, buff_spec, source_event):
    """ Handles when a activation trigger is met - activating buffs from the buffable.

    :param Buffable buffable:
    :param BuffSpec buff_spec:
    :param BuffEvent source_event:
    :rtype: list[ BuffModification ]
    """
    modifications = []
    if has_reached_max_stacks(buffable, buff_spec):
        return modifications

    active_buff = buffable.active_buffs.get(buff_spec.buff_id) or ActiveBuff(buff_spec.buff_id, source_event)
    active_buff.stack += 1
    buffable.active_buffs[buff_spec.buff_id] = active_buff

    # Remove the activation triggers because we just used em to activate this buff
    delete_triggers(buff_spec.buff_id, buff_spec.get_triggers(), buffable.activation_triggers)

    if buff_spec.can_target(buffable.name):

        # Just in case this is the first stack
        if active_buff.stack == 1:

            # Copy the remove triggers so this buff could potentially be inactivated
            copy_triggers(buff_spec.buff_id, buff_spec.get_remove_triggers(), buffable.deactivation_triggers)

        # Add an expiry time if needed
        register_expiry_time(buffable, buff_spec)

        # Create all modifications i need to apply to this buffable
        modifications = create_buff_modifications(buffable, buff_spec.buff_id, source_event, active_buff.stack)

        # Apply the modifications and update derivated attributes if we updating a source attribute of derivation
        for modification in modifications:
            apply_attributes_modification(buffable.attributes, modification)
            update_derivated_attributes(buffable, modification.applied_modifier.attribute_id)

    return modifications


@strack_tracer.Track
def inactivate_buff(buffable, buff_spec, source_event):
    """ Handles when a inactivation trigger is met - inactivating buffs from the buffable.

    :param Buffable buffable:
    :param BuffSpec buff_spec:
    :param BuffEvent source_event:
    :rtype: list[ BuffModification ]
    """
    stacks = buffable.active_buffs[buff_spec.buff_id].stack

    # Remove one stack of the buff, removing its modifications
    modifications_removed = remove_all_buff_modifications(buffable, buff_spec, stacks)
    buffable.active_buffs[buff_spec.buff_id].stack -= 1

    # In case there are no stacks left, buff becomes inactive
    if buffable.active_buffs[buff_spec.buff_id].stack == 0:
        del buffable.active_buffs[buff_spec.buff_id]
        delete_triggers(buff_spec.buff_id, buff_spec.get_remove_triggers(), buffable.deactivation_triggers)
        copy_triggers(buff_spec.buff_id, buff_spec.get_triggers(), buffable.activation_triggers)

    return modifications_removed


@strack_tracer.Track
def remove_all_buff_modifications(buffable, buff_spec, specific_stack=None):
    """ Removes all buff modifications a buff made. This takes into account propagations and derivations as well.

    :param buffable:
    :param buff_spec:
    :param int specific_stack: When only removing one stack, what stack is being removed
    :return:
    """
    modifications_removed = []
    for target in get_propagation_target_buffables(buffable, buff_spec):
        for modification in get_all_buff_modifications(target.attributes, buff_spec.buff_id):
            if not specific_stack or modification.stack_count == specific_stack:
                remove_attribute_modification(target.attributes, modification)
                update_derivated_attributes(target, modification.applied_modifier.attribute_id)
                modifications_removed.append(modification)
    return modifications_removed

