
import buffspecs

from models import BuffModification

from propagation import get_propagation_source
from derivation import create_derivation_modifier


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
