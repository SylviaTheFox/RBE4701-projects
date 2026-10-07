# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')
from monsters.stupid_monster import StupidMonster
# Import necessary stuff
from game import Game

# TODO This is your code!
sys.path.insert(1, '../team13')
from testcharacter import TestCharacter
from interactivecharacter import InteractiveCharacter
from qlearner import QLearner, Drill1

features = [
    lambda x: 1/(1+x),
    lambda x: 1/(1+x),
    lambda x: 0, 
    lambda x: 0,
    lambda x: 0,
    lambda x: 0,
    lambda x: 1/(1+x),
    lambda x: 0,
    lambda x: 0
]

weights = [-1, -1, 0, 0, 0, 0, 1, 0, 0]

for i in range(20):
    # Create the game
    g = Game.fromfile('map_train_1.txt')
    learner = Drill1(weights=weights, features=features)
    char = TestCharacter("me", # name
                              "C",  # avatar
                              0, 0,  # position
                              mover=learner
    )
    g.add_character(char)
    g.add_monster(StupidMonster("stupid", # name
                            "S",      # avatar
                            6, 2      # position
    ))
    weights = learner.weights
    # Run!
    g.go(0)
    print(weights)
