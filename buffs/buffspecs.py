from collections import defaultdict
from functools import wraps


class SpecCache(object):
    def __init__(self):
        # Map of buff_id to buff_spec
        self.buff_specs = {}
        # Map of condition names (function names) and the function reference
        self.conditions = {}
        # Map of propagator to propagable and the propagation function
        self.propagation_map = defaultdict(list)
        # Map of target buffable class and the list of buffables
        self.propagation_contexts = {}


_cache = SpecCache()


def clear():
    _cache.buff_specs = {}


#################
# SPEC HANDLING #
#################

def register_buff(buff_spec):
    _cache.buff_specs[buff_spec.buff_id] = buff_spec


def register_condition_function(condition_function, event_class=None, buffable_class=None):
    _cache.conditions[condition_function.__name__] = condition_function


def register_propagation_function(propagation_function, from_class, to_class):
    _cache.propagation_map[from_class.__name__].append((to_class.__name__, propagation_function))


def get_buff_spec(buff_id):
    return _cache.buff_specs[buff_id]


def get_condition(condition_spec_string):
    condition_split = condition_spec_string.split(" ")
    function_name = condition_split.pop(0)
    should_be_true = True
    if function_name == "not":
        should_be_true = False
        function_name = condition_split.pop(0)
    condition_function = _cache.conditions[function_name]
    condition_args = [float(arg) if arg.isdigit() else arg for arg in condition_split]
    return condition_function, condition_args, should_be_true


def get_propagation_targets(buffable, target_class_name):
    targets = []
    for class_name, get_targets_function in _cache.propagation_map[buffable.__class__.__name__]:
        if class_name == target_class_name:
            targets += get_targets_function(buffable)
    return targets


#####################
# INTEGRATION SUGAR #
#####################

def AddConditionFor(event_classes=None, buffable_class=None):
    def decorator(condition_function):
        register_condition_function(condition_function)
        @wraps(condition_function)
        def wrapper(*args, **kw):
            return condition_function(*args, **kw)
        return wrapper
    return decorator


def AddPropagation(from_class, to_class):
    def decorator(propagation_function):
        register_propagation_function(propagation_function, from_class, to_class)
        @wraps(propagation_function)
        def wrapper(*args, **kw):
            return propagation_function(*args, **kw)
        return wrapper
    return decorator


class ConditionHandlerContext(object):
    def __init__(self, condition_handler):
        self.condition_handler = condition_handler


class PropagationTargets(object):
    def __init__(self, targets):
        self.targets = targets

    def __enter__(self):
        _cache.propagation_contexts[self.buffable_class] = self.buffable_instances

    def __exit__(self, exception_type, exception_value, traceback):
        del _cache.propagation_contexts[self.buffable_class]


# TODO: JUST FOR TESTS... MOVE TO TESTS !
class _IDGen(object):
	ID = 0

	def next(self):
		self.ID = self.ID + 1
		return self.ID


IDGen = _IDGen()
