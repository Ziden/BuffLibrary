
"""

TODO LIST

 implement excel integration http://docs.xlwings.org/en/v0.6.4/vba.html?highlight=python

 implement interface for https://cython.org/

 UNIT TESTS

 TEST STACKS WITH PROPAGATION

 TEST STACKS WITH DERIVATION

 HANDLE STACK INACTIVATION ?

 BUFF VALIDATION (CHECK SPEC INCONSISTENCIES ETC)

 CONDITION TARGET EVENTS / BUFFABLES VALIDATIONM

 HANDLE INFINITE DERIVATION LOOP

 MAKE BUFFABLE TYPE - STOP USING CLASS NAMES

 PROPAGATION MAP CONTEXT

 BUFFABLE VERSIONING - UPDATE BUFF SPECS -> UPDATE BUFFABLES

"""

"""
HIDDEN GEMS:

- Conditions can be used for chance in buffs
    - Whenever a ship wins a battle, theres 50% chance he gets a bonus atk for few minutes.

- Dependency buffs
    - a buff that gives your fleet defense and make it "blinded"
    - a global buff that makes your "blinded" buffables get
    
- Propagation and Propagated triggers 
    - global buff that only propagates to ships if you have at least 3 ships docked  
    - when it propagates, it makes your deployed ships whenever docked in a mine, get a DEFENSE buff

"""