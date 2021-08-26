from debug import strack_tracer

from models import BuffPropagatedEvent
import buffspecs


def get_buff_propagation_events(buffable, buff_spec, source_event):
    """ Gets all propagations events that should happen for a specific buff.

    :param Buffable buffable:
    :param BuffSpec buff_spec:
    :param BuffEvent source_event:
    :rtype: generator[BuffPropagatedEvent]
    :returns A list of generated events for the propagation
    """
    for target_buffable in get_propagation_target_buffables(buffable, buff_spec):
        yield BuffPropagatedEvent(target_buffable, buffable, buff_spec.buff_id, source_event)


def get_propagated_targets_of_given_attribute(buffable, attribute_id):
    """ Obtain a lists of targets that are affected by a propagator attribute, for instance in a derivation.

    :param Buffable buffable:
    :param int attribute_id:
    :rtype: generator[Buffable]
    """
    for active_buff_id in buffable.active_buffs:
        buff_spec = buffspecs.get_buff_spec(active_buff_id)

        # If i have a buff that propagates to an attribute
        if buff_spec.propagates_to_attribute:
            targets = get_propagation_target_buffables(buffable, buff_spec)
            for source_modifier in buff_spec.modifiers:

                # In case the target attribute i propagate comes from this attribute that im changing
                if source_modifier.attribute_id == attribute_id:
                    for target in targets:

                        # Need to track that for that target because he will be affected
                        yield target


def get_propagation_source(event):
    """ Obtain the buffable that caused a propagation event, if there is one.

    :param BuffEvent event:
    :rtype Buffable | None
    """
    for chain_event in event.get_event_chain():
        if isinstance(chain_event, BuffPropagatedEvent):
            return chain_event.source_buffable


def get_propagation_target_buffables_including_self(buffable, buff_spec):
    targets = list(get_propagation_target_buffables(buffable, buff_spec))
    if buffable not in targets:
        targets.append(buffable)
    return targets


def get_propagation_target_buffables(buffable, buff_spec):
    """ Get all possible targets of a propagation for a buff spec.

    :param Buffable buffable:
    :param BuffSpec buff_spec:
    :rtype: generator[Buffable]
    """
    if buff_spec.propagates:
        for target in buff_spec.propagates_to:
            for buffable_target in buffspecs.get_propagation_targets(buffable, target):
                yield buffable_target
    else:
        yield buffable

