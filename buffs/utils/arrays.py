

def copy_triggers(buff_id, spec_triggers, buffable_triggers):
    for trigger in spec_triggers:
        buffable_triggers[trigger].append(buff_id)


def delete_triggers(buff_id, spec_triggers, buffable_triggers):
    for trigger in spec_triggers:
        buffable_triggers.remove_from_list(trigger, buff_id)
