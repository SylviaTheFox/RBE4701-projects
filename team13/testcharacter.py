# This is necessary to find the main code
import sys
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back

class TestCharacter(CharacterEntity):

    def do(self, wrld):
        # Your code here
        pass
    
    def createHeuristic(self, wrld):
        heuristics = [[0]*wrld.width()]*wrld.height()
        # monster
        for x in range(wrld.width()):
            for y in range(wrld.height()):
                if wrld.monster_at(x,y):
                    heuristics[y][x] += 100
                    if y > 0:
                        heuristics[y-1][x] += 50
                        if x > 0:
                            heuristics[y-1][x-1] += 15
                        if x < wrld.width() - 1:
                            heuristics[y-1][x+1] += 15
                    if x > 0:
                        heuristics[y][x-1] += 50
                    if y < wrld.height() - 1:
                        heuristics[y+1][x] += 50
                        if x > 0:
                            heuristics[y+1][x-1] += 15
                        if x < wrld.width() - 1:
                            heuristics[y+1][x+1] += 15
                    if x < wrld.width() - 1:
                        heuristics[y][x+1] += 50
                    if y > 1:
                        heuristics[y-2][x] += 15
                    if x > 1:
                        heuristics[y][x-2] += 15
                    if y < wrld.height() - 2:
                        heuristics[y+2][x] += 15
                    if x < wrld.width() - 2:
                        heuristics[y][x+2] += 15
                    
        
        # wall
        for x in range(wrld.width()):
            for y in range(wrld.height()):
                if wrld.wall_at(x, y):
                    heuristics[y][x] = 1000
                
        pass
    
    def calcMoveAstar(self, wrld, heur):
        pass
    
    
