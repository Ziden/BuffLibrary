from utils.arrays import copy_triggers, delete_triggers

import buffspecs
from debug import strack_tracer

from models import AddBuffEvent, EventResult, BuffPropagatedEvent

from events import get_buff_specs_triggered_by_event, handle_event_conditions
from propagation import get_buff_propagation_events, get_propagation_target_buffables_including_self
from buffable import (
    activate_buff, inactivate_buff, remove_all_buff_modifications, has_reached_max_stacks
)
from errors import BuffException, BuffErrorCodes

@strack_tracer.Track
def call_event(event):
    """ Calls an event and try to trigger any remaining triggers on the event buffable.

    :param BuffEvent event:
    :rtype EventResult
    :returns An event result with all added, removed and propagated modifications.
    """
    buffable = event.buffable
    result = EventResult()

    # Activation Triggers
    for triggered_buff_spec in get_buff_specs_triggered_by_event(event, buffable.activation_triggers):
        result.added_modifications = activate_buff(buffable, triggered_buff_spec, event)

    # Deactivation Triggers
    for triggered_buff_spec in get_buff_specs_triggered_by_event(event, buffable.deactivation_triggers, condition_inverse=True):
        result.removed_modifications = inactivate_buff(buffable, triggered_buff_spec, event)

    # Propagation Triggers
    for triggered_buff_spec in get_buff_specs_triggered_by_event(event, buffable.propagation_triggers, propagation=True):
        for propagation_event in get_buff_propagation_events(buffable, triggered_buff_spec, event):
            buff_spec = buffspecs.get_buff_spec(propagation_event.buff_id)
            result.propagated_modifications[propagation_event.buffable.id].append(
                add_buff(propagation_event.buffable,buff_spec, propagation_event, propagated=True)
             )
            # In case this buff spec has no propagation triggers and was just propagated by "AddBuffEvent"
            # means this buff wont be able to re-propagate ever again.
            if not buff_spec.propagation_triggers:
                delete_triggers(propagation_event.buff_id, ["AddBuffEvent"], buffable.propagation_triggers)

    return result


@strack_tracer.Track
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

    # We add the buff triggers or AddBuffEvent trigger if theres no trigger so it auto triggers
    copy_triggers(buff_spec.buff_id, buff_spec.get_triggers(), buffable.activation_triggers)

    # Call add buff event, auto triggering the buff if needed
    return call_event(AddBuffEvent(buffable, buff_spec.buff_id, source_event))


@strack_tracer.Track
def remove_buff(buffable, buff_id):
    """ Removes a buff from a buffable

    :param Buffable buffable:
    :param int buff_id:
    """
    if buff_id in buffable.active_buffs:

        buff_spec = buffspecs.get_buff_spec(buff_id)
        if buffable.name in buff_spec.propagates_to:
            raise BuffException(BuffErrorCodes.REMOVING_BUFF_NOT_FROM_SOURCE)

        del buffable.active_buffs[buff_id]
        buff_spec = buffspecs.get_buff_spec(buff_id)
        delete_triggers(buff_id, buff_spec.get_triggers(), buffable.activation_triggers)
        delete_triggers(buff_id, buff_spec.get_propagation_triggers(), buffable.propagation_triggers)
        delete_triggers(buff_id, buff_spec.get_remove_triggers(), buffable.deactivation_triggers)
        for target in get_propagation_target_buffables_including_self(buffable, buff_spec):
            remove_all_buff_modifications(target, buff_spec)


@strack_tracer.Track
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
            if handle_event_conditions(propagation_event, buff_spec.conditions):
                event_results.append(
                    add_buff(destination_buffable, buff_spec, propagation_event, propagated=True)
                )
    return event_results
