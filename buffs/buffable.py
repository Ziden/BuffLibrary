from debug import strack_tracer
import buffspecs

from models import BuffModification, ActiveBuff
from utils.arrays import delete_triggers, copy_triggers

from propagation import get_propagation_source, get_propagation_target_buffables
from attributes import get_all_buff_modifications, remove_attribute_modification, apply_attributes_modification
from derivation import create_derivation_modifier, update_derivated_attributes
from expiry import get_timestamp, register_expiry_time, get_expired_buffs


@strack_tracer.Track
def create_buff_modifications(buffable, buff_id, source_event):
    """ Generates a list of buff modifications a buff will have to apply a buffable.
    Buff modifications are changes that can be applied to attributes as a whole.
    This list contains all changes that will update the buffable attributes.

    :param Buffable buffable:
    :param int buff_id:
    :param BuffEvent source_event:
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

        modifications.append(buff_modification)
    return modifications


@strack_tracer.Track
def get_attributes(buffable):
    """ Check if there is any expired buffs on this buffable, then return the attributes.

    :param Buffable buffable:
    :return:
    """
    for buff_spec in get_expired_buffs(buffable):
        inactivate_buff(buffable, buff_spec, None)
        # If this buff has not activation triggers he should never be activated again
        if not buff_spec.activation_triggers:
            delete_triggers(buff_spec.buff_id, buff_spec.get_triggers(), buffable.activation_triggers)

    return buffable._attributes


def increment_buff_stack(buffable, buff_spec):

    if buff_spec.buff_id in buffable.active_buffs:
        active_buff = buffable.active_buffs[buff_spec.buff_id]
        if active_buff.stack >= buff_spec.max_stack:
            return False

        active_buff.stack += 1
    return True


@strack_tracer.Track
def activate_buff(buffable, buff_spec, source_event):
    """ Handles when a activation trigger is met - activating buffs from the buffable.

    :param Buffable buffable:
    :param BuffSpec buff_spec:
    :param BuffEvent source_event:
    :rtype: list[ BuffModification ]
    """
    modifications = []
    if not increment_buff_stack(buffable, buff_spec):
        return modifications

    active_buff = buffable.active_buffs.get(buff_spec.buff_id) or ActiveBuff(buff_spec.buff_id, source_event)
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
        modifications = create_buff_modifications(buffable, buff_spec.buff_id, source_event)

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
    del buffable.active_buffs[buff_spec.buff_id]
    delete_triggers(buff_spec.buff_id, buff_spec.get_remove_triggers(), buffable.deactivation_triggers)
    copy_triggers(buff_spec.buff_id, buff_spec.get_triggers(), buffable.activation_triggers)

    # Removing Modifications and Recalculating Possible Affected Derivations
    return remove_all_buff_modifications(buffable, buff_spec)


@strack_tracer.Track
def remove_all_buff_modifications(buffable, buff_spec):
    modifications_removed = []
    for target in get_propagation_target_buffables(buffable, buff_spec):
        for modification in get_all_buff_modifications(target.attributes, buff_spec.buff_id):
            remove_attribute_modification(target.attributes, modification)
            update_derivated_attributes(target, modification.applied_modifier.attribute_id)
            modifications_removed.append(modification)
    return modifications_removed

