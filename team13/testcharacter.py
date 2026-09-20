# This is necessary to find the main code
import sys
from queue import PriorityQueue
sys.path.insert(0, '../bomberman')
# Import necessary stuff
from entity import CharacterEntity
from colorama import Fore, Back
from random import random
from monsters.stupid_monster import StupidMonster
from monsters.selfpreserving_monster import SelfPreservingMonster
import math

class TestCharacter(CharacterEntity):

    # State 0 is haven't done A*, state 1 is following A*
    state = 0
    # Exit coords in our current map
    exit = (8, 18)
    optimal_path = []
    prev_monster = None

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
    

        # Find the best path to the exit
        if self.state == 0:
            self.optimal_path = self.a_star(wrld)
            self.state = 1

        if self.state == 1:
            next = self.optimal_path.pop(0)
            dx = next[0] - self.x
            dy = next[1] - self.y
            monsters = self.look_for_monster(wrld, 5)
            if monsters:
                # If we found a monster, either move away from it or be brave and continue on optimal path based on how close monster is and how far the exit is
                bravery = 2 * math.sqrt(1.5/self.square_dist((self.x, self.y), self.exit)) * math.log(self.square_dist((0, 0), monsters))
                # If we run into the very aggressive monster, being brave is stupid and we should just try to avoid being seen by it to win
                if (monsters[2]):
                    # If below the monster, most likely already passed it and are safe so don't waste time escaping and just run for the exit
                    if monsters[1] < 0:
                        bravery = 1
                    # If we saw this monster before, take into account his previous movements to determine where he's heading.
                    elif self.prev_monster:
                        m_dx = self.x + monsters[0] - self.prev_monster[0]
                        m_dy = self.y + monsters[1] - self.prev_monster[1]
                        # If he moves the same way and we move how we want and are still outside of its sight, good to move. Else stay away
                        if abs(-dx + (m_dx + monsters[0])) >= 3 or abs(-dy + (m_dy + monsters[1])) >= 3:
                            bravery = 1
                        else:
                            bravery = 0
                    # Haven't seen it before, stay away
                    else:
                        bravery = 0

                    self.prev_monster = (monsters[0] + self.x, monsters[1] + self.y)

                # If monster is level on x or y moving away is better than staying put
                if monsters[0] != 0 and random() > bravery:
                    new_dx = -self.clamp(monsters[0], -1, 1)
                    if (self.x + new_dx < wrld.width()) and not wrld.wall_at(self.x + new_dx, self.y + dy):
                        dx = new_dx
                    else:
                        dx = 0

                if monsters[1] != 0 and random() > bravery:
                    new_dy = -self.clamp(monsters[1], -1, 1)
                    if not wrld.wall_at(self.x + dx, self.y + new_dy) and (self.y + new_dy < wrld.height()):
                        dy = new_dy
                    else:
                        dy = 0
                # recalculate optimal path because we deviated from it after escaping
                self.state = 0
            self.move(dx, dy)
            
    def clamp(self, num, min_val, max_val):
        return max(min_val, min(num, max_val))

    def look_for_monster(self, wrld, rnge=1):
        monsters = []
        for dx in range(-rnge, rnge+1):
            # Avoid out-of-bounds access
            if ((self.x + dx >= 0) and (self.x + dx < wrld.width())):
                for dy in range(-rnge, rnge+1):
                    # Avoid out-of-bounds access
                    if ((self.y + dy >= 0) and (self.y + dy < wrld.height())):
                        # Is a monster at this position?
                        mons = wrld.monsters_at(self.x + dx, self.y + dy)
                        if (mons):
                            # if monster isn't aggressive, only take it into account if it's close enough
                            if mons[0].avatar != "A" and math.sqrt(dx**2 + dy**2) < 4:
                                monsters.append((dx, dy, False))
                            elif mons[0].avatar == "A":
                                # If monster has high range, be more careful
                                monsters.append((dx, dy, True))

        if monsters:
            # Only return the closest monster
            return min(monsters, key=lambda x: x[0]^2 + x[1]^2)

    def look_for_empty_cell(self, wrld, current, rnge=1):
        # List of empty cells
        cells = []
        # Go through neighboring cells
        for dx in range(-rnge, rnge+1):
            # Avoid out-of-bounds access
            if ((current[0] + dx >= 0) and (current[0] + dx < wrld.width())):
                for dy in range(-rnge, rnge+1):
                    # Avoid out-of-bounds access
                    if ((current[1] + dy >= 0) and (current[1] + dy < wrld.height())):
                        # Is this cell walkable?
                        if not wrld.wall_at(current[0] + dx, current[1] + dy):
                            cells.append((current[0] + dx, current[1] + dy))
        # All done
        return cells

    def square_dist(self, current, other):
        return (current[0] - other[0]) ** 2 + (current[1] - other[1]) ** 2
    
    def a_star(self, wrld):
        """
        A* Algorithm found in the slides for search, searches for optimal path from current position to end
        """
        
        frontier = PriorityQueue()
        frontier.put((self.x,self.y), 0)
        came_from = {}
        cost_so_far = {}
        came_from[(self.x,self.y)] = None
        cost_so_far[(self.x,self.y)] = 0

        while not frontier.empty():
            current = frontier.get()

            if wrld.exit_at(current[0], current[1]):
                # At exit, backtrack
                path = []
                while current != (self.x, self.y):
                    path.insert(0, current)
                    current = came_from[current]

                return path

            for next in self.look_for_empty_cell(wrld, current):
                # Cost increases by abs of dx and dy only
                new_cost = cost_so_far[current] + abs(next[0] - current[0]) + abs(next[1] - current[1])
                if next not in cost_so_far or new_cost < cost_so_far[next]:
                    cost_so_far[next] = new_cost
                    priority = new_cost + math.sqrt(self.square_dist(current, self.exit))
                    frontier.put(next, priority)
                    came_from[next] = current
