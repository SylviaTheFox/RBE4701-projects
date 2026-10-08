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
from qlearner import QLearner, Drill2

features = [
    lambda x: 0 if x is None else 1/(1+x),
    lambda x: 0 if x is None else 1/(1+x),
    lambda x: 0 if x is None else x, 
    lambda x: 0 if x is None else x,
    lambda x: 0,
    lambda x: 0 if x is None else x,
    lambda x: 0 if x is None else 1/(2+x),
    lambda x: 0 if x is None else 1/(2+x)
]

weights = [-1, -1, -10, -10, 0, -10, 1, 1]
wins = 0
for i in range(1000):
    # Create the game
    g = Game.fromfile('map_train_2.txt')
    bomb_x = randint(0, 7)
    learner = Drill2(weights=weights, features=features, bomb=(bomb_x, 2))
    
    char = TestCharacter("me", # name
                              "C",  # avatar
                              bomb_x, 2,  # position
                              mover=learner
    )
    g.add_character(char)
    g.add_monster(SelfPreservingMonster("selfpreserving", # name
                                    "S",              # avatar
                                    randint(0, 7), randint(2, 4),             # position
                                    2                 # detection range
    ))
    # Run!
    g.world.grid[randint(max(bomb_x-1, 0), min(bomb_x+1, g.world.width()-1))][1] = False
    g.world.add_bomb(bomb_x, 2, char)
    g.go(1)
    if not(g.world.explosion_at(bomb_x, 2)) and not(g.world.bomb_at(bomb_x, 2)):
        wins += 1

    weights = learner.weights
    print(weights)

print(wins)