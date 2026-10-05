# This is necessary to find the main code
import sys
sys.path.insert(0, '../../bomberman')
sys.path.insert(1, '..')

# Import necessary stuff
from game import Game

# TODO This is your code!
sys.path.insert(1, '../team13')
from testcharacter import TestCharacter
from interactivecharacter import InteractiveCharacter

# Create the game
g = Game.fromfile('map_train_2.txt')

# # TODO Add your character
# g.add_character(TestCharacter("me", # name
#                               "C",  # avatar
#                               0, 0  # position
# ))

# # Uncomment this if you want the interactive character
g.add_character(InteractiveCharacter("me", # name
                                     "C",  # avatar
                                     0, 0  # position
))

# Run!
g.go()