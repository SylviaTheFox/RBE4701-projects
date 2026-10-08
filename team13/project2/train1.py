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
    lambda x: 0 if x<0 else 1/(1+x),
    lambda x: 0 if x<0 else 1/(1+x),
    lambda x: 0, 
    lambda x: 0,
    lambda x: 0,
    lambda x: 0,
    lambda x: 1/(2+x),
    lambda x: 1/(2+x)
]

weights = [-1, -1, 0, 0, 0, 0, 1, 1, 1]
wins = 0
for i in range(100):
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
    # Run!
    g.go(1)
    weights = learner.weights
    if (g.world.characters):
        wins += 1
    print(weights)
print(wins)
