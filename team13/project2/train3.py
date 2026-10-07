# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')
from monsters.stupid_monster import StupidMonster
from monsters.selfpreserving_monster import SelfPreservingMonster
# Import necessary stuff
from game import Game
from random import randint
# TODO This is your code!
sys.path.insert(1, '../team13')
from testcharacter import TestCharacter
from interactivecharacter import InteractiveCharacter
from qlearner import QLearner, Drill2, Drill3

#[abs(dx to closest monster), 
# abs(dy to closest monster), 
# time till explosion or 0, 
# abs(dx to closest wall), 
# abs(dy to closest wall), 
# bomb planted?, 
# abs(dx to hole or exit), 
# dy to hole or exit]
features = [
    lambda x: 1/(1+x),
    lambda x: 1/(1+x),
    lambda x: 0, 
    lambda x: 0,
    lambda x: 0,
    lambda x: 0,
    lambda x: 1/(1+x),
    lambda x: 1/(1+x)
]

weights = [-1, -1, 0, 0, 0, -10, 1, 1, 1]
wins = 0
for i in range(1000):
    # Create the game
    g = Game.fromfile('map_train_3.txt')
    learner = Drill3(weights=weights, features=features)
    char = TestCharacter("me", # name
                              "C",  # avatar
                              randint(0, 8), randint(0, 2),  # position
                              mover=learner
    )
    g.add_character(char)
    g.add_monster(SelfPreservingMonster("selfpreserving", # name
                                    "S",              # avatar
                                    randint(0, 8), randint(0, 2),             # position
                                    2                 # detection range
    ))
    # Run!
    g.go(1)
    if not(g.world.explosion_at(4, 2)) and not(g.world.bomb_at(4, 2)):

        wins += 1
        exit()
    weights = learner.weights
    print(weights)

print(wins)