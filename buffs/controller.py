from collections import defaultdict
from utils.arrays import copy_triggers, delete_triggers
import buffspecs
from models import AddBuffEvent, BuffModification, ActiveBuff, EventResult, BuffPropagatedEvent

from derivation import recalculate_derivated_attributes, create_derivation_modifier

from attributes import remove_attribute_modification, apply_attributes_modification, get_all_buff_modifications


def call_event(event):
    """ Calls an event and try to trigger any remaining triggers on the event buffable.

    :param BuffEvent event:
    :rtype EventResult
    :returns An event result with all added, removed and propagated modifications.
    """
    buffable = event.buffable
    result = EventResult()

    for triggered_buff_spec in _event_triggered_buffs(event, buffable.activation_triggers):
        result.added_modifications = _activate_buff_trigger(buffable, triggered_buff_spec, event)

    for triggered_buff_spec in _event_triggered_buffs(event, buffable.deactivation_triggers, condition_inverse=True):
        result.removed_modifications = _inactivate_buff_trigger(buffable, triggered_buff_spec, event)

    for triggered_buff_spec in _event_triggered_buffs(event, buffable.propagation_triggers, propagation=True):
        result.propagated_modifications = _propagate_buff_trigger(buffable, triggered_buff_spec, event)

    return result


def _event_triggered_buffs(event, possible_trigger_list, condition_inverse=False, propagation=False):
    """ Obtains all triggered buffs by a given possible trigger list

    :param BuffEvent event:
    :param dict[str, list [ int ]] possible_trigger_list:  A dictionary of triggers to a list of buffs ids to trigger
    :param bool condition_inverse:
    :param bool propagation:
    :rtype: generator[BuffSpec]
    """
    for buff_id in reversed(possible_trigger_list[event.get_name()]):
        buff_spec = buffspecs.get_buff_spec(buff_id)
        conditions = buff_spec.conditions if not propagation else buff_spec.propagation_conditions
        if _handle_event_conditions(event, conditions) is not condition_inverse:
            yield buff_spec


def _handle_event_conditions(event, conditions):
    """ Check if all conditions match for a given event

    :param BuffEvent event:
    :param list[str] conditions:
    :rtype bool
    """
    for condition in conditions:
        condition_function, condition_args, should_be_true = buffspecs.get_condition(condition)
        if not condition_function(event, *condition_args) == should_be_true:
            return False
    return True


def _activate_buff_trigger(buffable, buff_spec, source_event):
    """ Handles when a activation trigger is met - activating buffs from the buffable.

    :param Buffable buffable:
    :param BuffSpec buff_spec:
    :param BuffEvent source_event:
    :rtype: list[ BuffModification ]
    """
    if buff_spec.buff_id in buffable.active_buffs:
        return []
    buffable.active_buffs[buff_spec.buff_id] = ActiveBuff(buff_spec.buff_id, source_event)
    delete_triggers(buff_spec.buff_id, buff_spec.get_triggers(), buffable.activation_triggers)
    if buff_spec.can_target(buffable.name):
        copy_triggers(buff_spec.buff_id, buff_spec.get_remove_triggers(), buffable.deactivation_triggers)
        modifications = _create_buff_modifications(buffable, buff_spec.buff_id, source_event)
        for modification in modifications:
            apply_attributes_modification(buffable.attributes, modification)
            apply_mod = modification.derivated_modifier or modification.modifier
            recalculate_derivated_attributes(buffable.attributes, apply_mod.attribute_id)
        return modifications


def _inactivate_buff_trigger(buffable, buff_spec, source_event):
    """ Handles when a inactivation trigger is met - inactivating buffs from the buffable.

    :param Buffable buffable:
    :param BuffSpec buff_spec:
    :param BuffEvent source_event:
    :rtype: list[ BuffModification ]
    """
    del buffable.active_buffs[buff_spec.buff_id]
    delete_triggers(buff_spec.buff_id, buff_spec.get_remove_triggers(), buffable.deactivation_triggers)
    copy_triggers(buff_spec.buff_id, buff_spec.get_triggers(), buffable.activation_triggers)
    modifications = get_all_buff_modifications(buffable.attributes, buff_spec.buff_id)
    for modification in modifications:
        remove_attribute_modification(buffable.attributes, modification)
        recalculate_derivated_attributes(buffable.attributes, modification.modifier.attribute_id)
    return modifications


def _propagate_buff_trigger(buffable, buff_spec, source_event):
    """ Handles when a propagation trigger is met - add buffs to propagation targets.

    :param Buffable buffable:
    :param BuffSpec buff_spec:
    :param BuffEvent source_event:
    :rtype: dict[int, list[ BuffModification ]]
    :returns A dictionary of buffable ids and a list of modifications applied
    """
    modifications = defaultdict(list)
    for target in buff_spec.propagates_to:
        for target_buffable in buffspecs.get_propagation_targets(buffable, target):
            event = BuffPropagatedEvent(target_buffable, buffable, buff_spec.buff_id, source_event)
            modifications[target_buffable.id].append(
                add_buff(target_buffable, buff_spec, event, propagated=True)
            )
    return modifications


def add_buff(buffable, buff_spec, source_event, propagated=False):
    """ Add a buff to a buffable. This means copy the buff triggers (or 'AddBuffEvent' as a trigger isf theres none)
        then calls AddBuffEvent. If the buff had no triggers, AddBuffEvent itself will auto-activate the buff.

    :param Buffable buffable:
    :param BuffSpec buff_spec:
    :param BuffEvent source_event:
    :param bool propagated:
    :rtype: EventResult
    """
    # If this buff can propagate, copy its propagation triggers (or AddBuffEvent if there's none)
    if not propagated and buff_spec.propagates:
        copy_triggers(buff_spec.buff_id, buff_spec.get_propagation_triggers(), buffable.propagation_triggers)
    copy_triggers(buff_spec.buff_id, buff_spec.get_triggers(), buffable.activation_triggers)
    return call_event(AddBuffEvent(buffable, buff_spec.buff_id, source_event))


def remove_buff(buffable, buff_id):
    """ Removes a buff from a buffable

    :param Buffable buffable:
    :param int buff_id:
    """
    if buff_id in buffable.active_buffs:
        del buffable.active_buffs[buff_id]

        buff_spec = buffspecs.get_buff_spec(buff_id)
        delete_triggers(buff_id, buff_spec.get_triggers(), buffable.activation_triggers)
        delete_triggers(buff_id, buff_spec.get_propagation_triggers(), buffable.propagation_triggers)

        # For everything this buff modified, we need to undo that
        for modification in get_all_buff_modifications(buffable.attributes, buff_id):
            remove_attribute_modification(buffable.attributes, modification)
            recalculate_derivated_attributes(buffable.attributes, modification.modifier.attribute_id)


def pull_propagated_buffs(source_buffable, destination_buffable, source_event):
    """ Pull all propagation buffs from a source to a target. Usually when creating a new buffable.

    :param Buffable source_buffable:
    :param Buffable destination_buffable:
    :param BuffEvent source_event:
    :rtype list[EventResult]
    :returns A list of event results containing all added, removed or propagated modifications
    """
    event_results = []
    for buff_id in source_buffable.active_buffs:
        buff_spec = buffspecs.get_buff_spec(buff_id)

        # If the destination contains any buff that targets my buffable type and is auto triggered, propagate
        if buff_spec.auto_triggers and destination_buffable.name in buff_spec.propagates_to:
            propagation_event = BuffPropagatedEvent(destination_buffable, source_buffable, buff_id, source_event)
            if _handle_event_conditions(propagation_event, buff_spec.conditions):
                event_results.append(add_buff(destination_buffable, buff_spec, propagation_event, propagated=True))
    return event_results


def _create_buff_modifications(buffable, buff_id, source_event):
    """ Generates a list of buff modifications a buff would have in a buffable.
    Buff modifications are changes that can be applied to attributes as a whole.

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
            derivated_modifier = create_derivation_modifier(
                buffable.attributes, modifier, buff_spec.to_attribute
            )
            buff_modification.derivated_modifier = derivated_modifier
        modifications.append(buff_modification)
    return modifications
