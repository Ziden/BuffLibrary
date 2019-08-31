from attributes import _apply_modifier_to_attributes
from models import Modifier


def recalculate_derivated_attributes(buffable_attributes, attribute_id):
    """ Updates derived attributes that depends on the given attribute

    :param BuffableAttribute buffable_attributes:
    :param int attribute_id:
    """
    # Get all modifications this attribute we are changing derivates to
    for modification in _get_modifications_derived_by_attribute(buffable_attributes, attribute_id):
        # Undo them
        _apply_modifier_to_attributes(buffable_attributes, modification.derivated_modifier, inverse=True)
        # Recalculate the derivated value
        new_derivated_modifier = create_derivation_modifier(
            buffable_attributes, modification.modifier, modification.derivated_modifier.attribute_id
        )
        # Apply again with updated value
        _apply_modifier_to_attributes(buffable_attributes, new_derivated_modifier)
        # The final modifier of the derivated value is stored in derivated modifier, keeping the original intact
        modification.derivated_modifier = new_derivated_modifier


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


def _get_modifications_derived_by_attribute(buffable_attributes, source_attribute_id):
    """ Get all attributes that were derivated from a source attribute

    :param BuffableAttributes buffable_attributes:
    :param int source_attribute_id:
    :rtype: generator[BuffModification]
    """
    attribute_data = buffable_attributes.get_data(source_attribute_id)
    for attribute_id, modification_ids in attribute_data.derivations.items():
        for modification_id in modification_ids:
            yield buffable_attributes.get_data(attribute_id).history[modification_id]