from attributes import _apply_modifier_to_attributes
from models import Modifier

from debug import strack_tracer
import buffspecs

from propagation import get_propagated_targets_of_given_attribute, get_propagation_source


@strack_tracer.Track
def create_derivation_modifier(buffable_attributes, modifier, to_attribute_id):
    """ Creates a derivation modifier from another source modifier. This new modifier will have flat add attributes
    to the target attribute, where the value of that flat add is the result of the derivation of another attribute.

    :param BuffableAttributes buffable_attributes:
    :param Modifier modifier:
    :param int to_attribute_id:
    :return:
    """
    # Get current value of the source attribute to derivate
    derivated_bonus = buffable_attributes[modifier.attribute_id]

    if modifier.operator == "+":
        derivated_bonus += modifier.value
    elif modifier.operator == "%":
        derivated_bonus *= modifier.value

    # Create a new modifier to add flat bonus of the derivated value
    return Modifier("+", derivated_bonus, to_attribute_id)


@strack_tracer.Track
def update_derivated_attributes(buffable, source_attribute_id):
    """ Updates derived attributes that depends on the given attribute that is changing.

    :param BuffableAttribute buffable_attributes:
    :param int source_attribute_id:  The attribute source of the derivations
    """

    # Check if the current buffable has any derivations based on the changing attribute
    _recalculate_derivated_values_from_attribute(buffable, source_attribute_id)

    # Check if i have any propagations that affect this attribute and update the target buffable
    for buffable_target in get_propagated_targets_of_given_attribute(buffable, source_attribute_id):
        _recalculate_derivated_values_from_attribute(buffable_target, source_attribute_id)


@strack_tracer.Track
def _recalculate_derivated_values_from_attribute(buffable, source_attribute_id):
    """ For existing derivated modifications on the buffable that are based on the source attribute ID,
    Recalculate the derivation modifiers by removing and re-appliyng them, updating the derivated values.

    :param Buffable buffable:
    :param int source_attribute_id:  The attribute that changed
    """

    # Get all modifications this attribute we are changing derivates to on this buffable
    for modification in _get_modifications_derived_by_attribute(buffable.attributes, source_attribute_id):

        # In case this modification is a derivation from a propagation, we need to calculate the derived value
        # with basis on the source buffable attributes
        buff_spec = buffspecs.get_buff_spec(modification.buff_id)
        buffable_propagator = buffable
        if buff_spec.propagates_to_attribute:
            buffable_propagator = get_propagation_source(modification.source_event)

        # Recalculate the derivated value
        new_derivated_modifier = create_derivation_modifier(
            buffable_propagator.attributes, modification.modifier, modification.derivated_modifier.attribute_id
        )

        # Keeping track of old derivated value because we will need to check it changed
        old_derivated_value = modification.derivated_modifier.value

        if old_derivated_value != new_derivated_modifier.value:

            # Undo the changes, just apply inversed
            _apply_modifier_to_attributes(buffable.attributes, modification.derivated_modifier, inverse=True)

            # Apply again with updated modifier
            _apply_modifier_to_attributes(buffable.attributes, new_derivated_modifier)

            # The final modifier of the derivated value is stored in derivated modifier, keeping the original intact
            modification.derivated_modifier = new_derivated_modifier

            # Since we changed an attribute, we need to chain derivation modifiers recalculation
            _recalculate_derivated_values_from_attribute(buffable, new_derivated_modifier.attribute_id)


@strack_tracer.Track
def _get_modifications_derived_by_attribute(buffable_attributes, source_attribute_id):
    """ Get all modifications that were derivated from a source attribute.
    Those modifications are stored in the target attribute history, because its the attribute that got modified.

    :param BuffableAttributes buffable_attributes:
    :param int source_attribute_id:
    :rtype: generator[BuffModification]
    """
    attribute_data = buffable_attributes.get_data(source_attribute_id)
    for target_attribute_id, modification_ids in attribute_data.derivations.items():
        for modification_id in modification_ids:
            yield buffable_attributes.get_data(target_attribute_id).history[modification_id]