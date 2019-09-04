
def buff_spec_to_string(buff_spec):
    result = "< Id={} ".format(buff_spec.buff_id)

    if buff_spec.triggers:
        result += " Whenever "
        for trigger in buff_spec.triggers:
            result += trigger

    if buff_spec.conditions:
        result += " Just if "
        for condition in buff_spec.conditions:
            result += str(condition)

    result += " Modify "
    for modifier in buff_spec.modifiers:
        result += str(modifier)

    if buff_spec.to_attribute:
        result += "to attribute {}".format(buff_spec.to_attribute)

    return "{}>".format(result)