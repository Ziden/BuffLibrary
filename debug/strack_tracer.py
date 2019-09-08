from functools import wraps
import types

from models import *

import inspect

import time

"""
This module is simply for help debugging. It allows to track function performance bottlenecks and code stack.
"""

# TODO: Read env variable or config
_tracking = False


class FunctionTracker(object):
    def __init__(self):
        self.context = None


_tracker = FunctionTracker()


class FunctionStack(object):
    def __init__(self, func, args, kwargs):
        self.function_reference = func
        self.function_name = func.__name__
        self.value = None
        self.args = args
        self.kwargs = kwargs
        self.delay = 0
        self.called = []


class TrackStack(object):
    def __init__(self):
        self.root_functions = []
        self.current_stack = []
        self.active_parent = None

    def __enter__(self):
        _tracker.context = self
        return self

    def __exit__(self, exception_type, exception_value, traceback):
        _tracker.context = None
        if exception_type:
            raise
        return self

    def print_stack(self):
        for stack in self.root_functions:
            level = 0
            string = stack_to_string(stack, level)
            if string:
                print(string)


def stack_to_string(stack, level):
    string = ""
    for i in range(level):
        string += "|   "

    function_str = ""
    if isinstance(stack.value, list):
        function_str += " [{}] ".format(len(stack.value))

    if isinstance(stack.value, bool):
        function_str += "[{}] ".format(str(stack.value))

    if isinstance(stack.value, types.GeneratorType):
        function_str += " [gen] "

    function_str += "{}(".format(stack.function_name)
    for arg in stack.args:
        if arg and isinstance(arg, (int, float, str)):
            function_str += str(arg)

        elif hasattr(arg, "name") and arg.name:
            function_str += arg.name

        elif isinstance(arg, object):
            function_str += arg.__class__.__name__
            if hasattr(arg, "buff_id"):
                function_str += "[id={}]".format(arg.buff_id)

        else:
            function_str += "_"

        if len(function_str) > 1 and arg != stack.args[-1]:
            function_str += ", "

    function_str += ")"
    string += "{} - {}ms".format(function_str, stack.delay)

    if stack.called:
        level += 1
        for called_stack in stack.called:
            string += "\n"
            string += stack_to_string(called_stack, level)
        level -= 1
    return string


def Track(func):

    if not _tracking:
        return func

    @wraps(func)
    def wrapper(*args, **kw):
        if not _tracking or not _tracker.context:
            return func(*args, **kw)

        # Create the track object
        stack = FunctionStack(func, args, kw)

        context = _tracker.context

        # If i got the stack open, add this as a child
        if context.current_stack:
            last_stack = context.current_stack[-1]
            last_stack.called.append(stack)
        else:
            context.root_functions.append(stack)

        context.current_stack.append(stack)

        # Run the function
        start_time = _get_timestamp_ms()
        ret_value = func(*args, **kw)
        end_time = _get_timestamp_ms()

        stack.value = ret_value

        context.current_stack.remove(stack)

        # Record the delay
        stack.delay = end_time - start_time
        return ret_value
    return wrapper


def _get_timestamp_ms():
    return int(round(time.time() * 1000))