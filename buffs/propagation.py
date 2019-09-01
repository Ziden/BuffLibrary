
from models import BuffPropagatedEvent
import buffspecs


def get_propagation_source(event):
    for chain_event in event.get_event_chain():
        if isinstance(chain_event, BuffPropagatedEvent):
            return chain_event.source_buffable


def get_propagation_targets(buffable, buff_spec):
    if buff_spec.propagates:
        for target in buff_spec.propagates_to:
            for buffable_target in buffspecs.get_propagation_targets(buffable, target):
                yield buffable_target
    else:
        yield buffable

