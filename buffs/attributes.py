import buffspecs

from models import BuffModification, BuffPropagatedEvent


def apply_attributes_modification(buffable_attributes, buff_modification):
    """ Applies a buff modification to attributes, calculating the final values.
    Also registers any derivations recieved (keeping track of the source)

    :param BuffableAttributes buffable_attributes:
    :param BuffModification buff_modification:
    :return:
    """
    # First we apply the modifier or the modification, changing the attributes values
    to_apply_modifier = buff_modification.derivated_modifier or buff_modification.modifier
    attribute_data = buffable_attributes.attribute_data[to_apply_modifier.attribute_id]
    _apply_modifier_to_attributes(buffable_attributes, to_apply_modifier)

    # Checking if we recieved a derivation, we register the source attribute of the derivation to know about this link
    if buff_modification.derivated_modifier:
        source_attributes = buffable_attributes
        trigger_event = buff_modification.source_event.trigger_event

        # If this was propagated, we save in the propagated source about this derivation
        if isinstance(trigger_event, BuffPropagatedEvent):
            source_attributes = buff_modification.source_event.trigger_event.source_buffable.attributes

        source_modifier = buff_modification.modifier
        source_attribute_data = source_attributes.attribute_data[source_modifier.attribute_id]
        source_attribute_data.derivations[to_apply_modifier.attribute_id].append(buff_modification.id)

    # Looking for propagated derivations
    for attribute_id, buff_modification_id in attribute_data.derivations.items():
        asd = 123

    attribute_data.history[buff_modification.id] = buff_modification


def remove_attribute_modification(buffable_attributes, buff_modification):
    """ Removes a buff modification from attributes, calculating the final attributes and updating any required
        derivated attributes.

    :param BuffableAttributes buffable_attributes:
    :param BuffModification buff_modification:
    :return:
    """
    modifier = buff_modification.modifier
    attr_data = buffable_attributes.attribute_data[modifier.attribute_id]

    # To remove a modification, we simply apply the inverse of it
    _apply_modifier_to_attributes(buffable_attributes, modifier, inverse=True)

    del attr_data.history[buff_modification.id]


def _apply_modifier_to_attributes(buffable_attributes, modifier, inverse=False):
    """ Applies a modifier to an attribute, calculating its final value.

    :param BuffableAttributes buffable_attributes:
    :param Modifier modifier:
    :param bool inverse:
    :rtype int
    """
    attr_data = buffable_attributes.attribute_data[modifier.attribute_id]
    value = modifier.value if not inverse else -modifier.value
    if modifier.operator == "+":
        attr_data.mod_add += value
    elif modifier.operator == "%":
        attr_data.mod_mult += value
    attr_data.calculate()
    return attr_data.final_value


def get_all_buff_modifications(buffable_attributes, buff_id):
    """ Gets all buff_modifications that buff is causing to attributes

    :param BuffableAttributes buffable_attributes:
    :param int buff_id:
    :rtype: list[BuffModification]
    """
    modifications = []
    buff = buffspecs.get_buff_spec(buff_id)
    for modifier in buff.modifiers:
        attr_data = buffable_attributes.attribute_data[modifier.attribute_id]
        for buff_modification in attr_data.history.values():
            if buff_modification.buff_id == buff_id:
                modifications.append(buff_modification)
    return modifications