# Game / RPG Buff Calculator

Simple Python Project for simple buff calculations. 

Buffs are commonly used in games as attribute modifiers, things that increase your attack, defence, health etc.

# Features

## Additives and Multipliers

Able to add both flat values and multipliers/percentages (IE +10 Attack or +10% Attack)

## Buff Propagation

A player can have equipment that propagates modifications to the player actor.
A "guild" can also have a set of players to propagate modifications to those actors.

## Buff Derivation

One attribute can be derived into other attributes, example is a sword that makes 50% of the player's defence, becomes player attack.

## Data Driven

You tell the library the attributes, the library handles the rest.

## Expiry Times

Buffs that expire after a set amount of time.

## Buff Stacks

Buffs can stack and be applied multiple times upon a limit

## Triggers

Buffs that require specific events to be fired to become active

## Condition Hooks

Able to hook conditional functions to know if a buff should be activated or not.

# How to use ?

Best guide on how to use would be checking the tests. They are very straight forward.
