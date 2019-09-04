
import buffspecs
from debug import strack_tracer


@strack_tracer.Track
def get_buff_specs_triggered_by_event(event, possible_trigger_list, condition_inverse=False, propagation=False):
    """ Obtains all triggered buffs by a given possible trigger list and conditions.
    The buffs are triggered from the newest to the oldest, and its a very important aspect
    of this function is that is a generator - because this allow the code to process the older buffs only after the
    first one is processed, allowing buff dependency out of the box.

    :param BuffEvent event:
    :param dict[str, list [ int ]] possible_trigger_list:  A dictionary of triggers to a list of buffs ids to trigger
    :param bool condition_inverse:
    :param bool propagation:
    :rtype: generator[BuffSpec]
    """
    #list = []
    for buff_id in reversed(possible_trigger_list[event.get_name()]):
        buff_spec = buffspecs.get_buff_spec(buff_id)
        conditions = buff_spec.conditions if not propagation else buff_spec.propagation_conditions
        if handle_event_conditions(event, conditions) is not condition_inverse:
            yield buff_spec


@strack_tracer.Track
def handle_event_conditions(event, conditions):
    """ Check if all conditions match for a given event.

    :param BuffEvent event:
    :param list[str] conditions:
    :rtype bool
    """
    for condition in conditions:
        condition_function, condition_args, should_be_true = buffspecs.get_condition(condition)
        if not condition_function(event, *condition_args) == should_be_true:
            return False
    return True