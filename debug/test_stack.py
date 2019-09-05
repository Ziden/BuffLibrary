from debug.strack_tracer import TrackStack, Track

import unittest
from time import sleep



@Track
def heavy_function():
    sleep(0.10)
    return


@Track
def quick_function():
    return medium_function()


@Track
def medium_function():
    sleep(0.05)


@Track
def parent_function():
    quick_function()
    heavy_function()
    pass


class Test_Function_Tracking(unittest.TestCase):


    def test_propagating_a_derivation_buff(self):

        # We want to track the performance of this
        with TrackStack() as track:

            parent_function()
            parent_function()

            root_calls = track.root_functions

            assert root_calls[0].function_name == "parent_function"
            assert root_calls[1].function_name == "parent_function"

            assert root_calls[0].called[0].function_name == "quick_function"
            assert root_calls[0].called[1].function_name == "heavy_function"

            # TODO: Finish this test
            # track.print_stack()