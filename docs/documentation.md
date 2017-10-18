# Documentation

## General Overview and Rules

Seekers is a game where _n_ players control _m_ magnets,
called seekers, to collect randomly appearing _goals_ and
transport them back to their base. If they can keep the
goals within their base for some amount of time then they
earn a point. When this happens, the goal dissappears and
a new one appears at a random spot on the board.

The seekers are controlled by writing a program that has
access to the state of the game and can apply some logic
to make decisions. In particular this means that every
round (of which there are about 20 per second) a player
knows

* the position, speed and destination (i.e. acceleration)
of every seeker on the board
* the position and speed of all the goals
* the state of the magnets of all seekers

and from this determines what to do, i.e.

* set the destination of each of its one seekers (this
determines the acceleration direction of the seekers but
not its magnitude) or
* change the state of the magnet of each of its seekers,
i.e. either _off_, _repelling_ or _attractive_

The code of the players is called every round and the
final properties of the objects are then applied to the
state of the game. The **board** is a torus of size
768 x 768 pixels.

**Collisions** are handled in an elastic way, in particular
seekers and goals have a non-zero size. There is **friction**
on the ground, so objects will stop moving after stopping
to accelerate.

**Magnetic fields** can attract and repel goals but no seekers.
However, if two seekers collide they are disabled for a
certain amount of time. How long depends on the magnetic
fields, e.g. if both have their magnetic fields activated
they are both disabled, if only one has it turned on then
only this seeker will receive the penalty. 

## Game Parameters

There exist quite a few parameters that are hard-coded
at the moment but which can be used to fine-tune the game.
In particular this includes

* world size
* number of goals
* number of seekers
* (winning condition)
* camp sizes
* strength of attractive magnets
* strength of repulsive magnets
* acceleration
* friction coefficient

## Winning Conditions

At the moment, there are no actual winning conditions implemented, however there
is a corresponding issue. Tournaments have so far been executed by stopping the
game after a fixed amount of time, e.g. 90s and comparing the points.

## Members and Methods

Here we list all the members and methods of the classes necessary or helpful
for playing Seekers.

### Vectors

Note that all vectorial objects are indeed vectors and can thus be added
and subtracted in the obvious way. Its components are accessed by the **x**
and **y** members. There exist **norm** and **normalized** methods to calculate
norms or normalize vectors.

### Seekers

Seekers are collected in the lists **all_seekers**, **other_seekers** and
**own_seekers**. They have members **position**, **velocity** and **target** for
describing their movement, all three of which are vectors. In particular
**target** can be set by the player to a position and then the seeker will
accelerate in that direction. The member **disabled** is a Boolean describing
whether the seeker is disabled from a collision.

The methods **set_magnet_repulsive**, **set_magnet_attractive** and **set_magnet_disabled**
change the state of the magnet in the obvious ways.

### Goals

Goals can be accessed via the list **goals**. It has vector members
**position**, **velocity** and **acceleration** describing its movement.
Individual goals can be distinguished by their **uid** which changes when
a new goal is created.

Seekers and goals are collectively referred to as **physical objects** as they
have a position and a velocity and they can collide.

### Camps

All camps are contained in the list **camps**. A camp has the members **owner**,
**position**, **width** and **height**. The position is at the center of the rectangular
camp. The standard camp is a square of side length 1/20 of the diameter of the
board which yields usually something like 55 pixels. The method **contains**
gives back a Boolean describing whether a given position is contained in the camp.

### World

The world class offers a few helper methods for calcuations on the torus. In
particular **torus_distance** calculates the distance between two positions on
the torus. The method **index_of_nearest** takes one position and a list
of positions as arguments and returns the index of the list element
closest to the first position. The most important variations of this
method are **nearest_goal** and **nearest_seeker** which can be used to find
the goal or seeker (not just the position) from a list closest to a given position.
The players are saved in the lists **all_players** and **other_players**.