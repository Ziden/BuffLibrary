import buffspecs

from debug import strack_tracer


def apply_attributes_modification(buffable_attributes, buff_modification):
    """ Applies a buff modification to attributes, calculating the final values.
    Also registers any derivations recieved (keeping track of the source)

    :param BuffableAttributes buffable_attributes:
    :param BuffModification buff_modification:
    :return:
    """

    # First we apply the modifier of the modification, changing the attributes values
    to_apply_modifier = buff_modification.applied_modifier
    attribute_data = buffable_attributes.attribute_data[to_apply_modifier.attribute_id]
    _apply_modifier_to_attributes(buffable_attributes, to_apply_modifier)

    # Checking if we recieved a derivation, we register the source attribute of the derivation to know its origin
    if buff_modification.derivated_modifier:
        source_attributes = buffable_attributes
        source_modifier = buff_modification.modifier
        source_attribute_data = source_attributes.attribute_data[source_modifier.attribute_id]

        # Source attribute will contain a reference to the target attribute and a modification id for the changes
        source_attribute_data.derivations[to_apply_modifier.attribute_id].append(buff_modification.id)

    # This modification is stored in this attribute data history
    attribute_data.history[buff_modification.id] = buff_modification


def remove_attribute_modification(buffable_attributes, buff_modification):
    """ Removes a buff modification from attributes, calculating the final attributes and updating any required
        derivated attributes.

    :param BuffableAttributes buffable_attributes:
    :param BuffModification buff_modification:
    :return:
    """
    modifier = buff_modification.applied_modifier
    attr_data = buffable_attributes.attribute_data[modifier.attribute_id]

    # To remove a modification, we simply apply the inverse of it
    _apply_modifier_to_attributes(buffable_attributes, modifier, inverse=True)

    # And remove from history of that attribute
    del attr_data.history[buff_modification.id]


def get_all_buff_modifications(buffable_attributes, buff_id):
    """ Gets all buff_modifications that buff is causing to attributes

    :param BuffableAttributes buffable_attributes:
    :param int buff_id:
    :rtype: list[BuffModification]
    """
    modifications = []
    buff = buffspecs.get_buff_spec(buff_id)
    for modifier in buff.modifiers:

        # The changed attribute we looking for can be the derivated attribute or the modifier itself
        # TODO: Make propagates_to_attribute works with to_attribute, could it be useful ?
        affected_attribute_id = buff.to_attribute or buff.propagates_to_attribute or modifier.attribute_id

        attr_data = buffable_attributes.attribute_data[affected_attribute_id]
        for buff_modification in attr_data.history.values():
            if buff_modification.buff_id == buff_id:
                modifications.append(buff_modification)
    return modifications


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
