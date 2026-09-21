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
    heuristic = []

    def do(self, wrld):
        # self.heuristic = self.createHeuristic(wrld)

        # path = self.a_star(wrld)

        # dx = path[0][0] - self.x
        # dy = path[0][1] - self.y

        # self.move(dx, dy)
        if self.state == 0:
            self.optimal_path = self.a_star(wrld)
            self.state = 1

        if self.state == 1:
            next = self.optimal_path.pop(0)
            dx = next[0] - self.x
            dy = next[1] - self.y
            monsters = self.look_for_monster(wrld, 5)
            if monsters:
                bravery = 0
                # If below the monster, most likely already passed it and are safe so don't waste time escaping and just run for the exit
                if monsters[0].y < self.y:
                    bravery = 1
                # If we are a certain distance from monster after we both move, proceed. otherwise go the other way to
                elif abs((self.x + dx) - (monsters[0].dx + monsters[0].x)) >= monsters[1] or abs((self.y + dy) - (monsters[0].dy + monsters[0].y)) >= monsters[1]:
                    bravery = 1
                else:
                    bravery = 0

                # If monster is level on x or y moving away is better than staying put
                if monsters[0].x != self.x and not bravery:
                    new_dx = -self.clamp(monsters[0].x, -1, 1)
                    if (self.x + new_dx > 0) and (self.x + new_dx < wrld.width()) and not wrld.wall_at(self.x + new_dx, self.y + dy):
                        dx = new_dx
                    else:
                        dx = 0
                        # Stuck against a wall most likely, try to move away from monster if coming at us and not doing so already
                        if dy == 0 and monsters[0].dy == 0:
                            dy = 1
                        elif dy == 0:
                            dy = -self.clamp(monsters[0].y, -1, 1)


                if monsters[0].y != self.y and not bravery:
                    new_dy = -self.clamp(monsters[0].y, -1, 1)
                    if not wrld.wall_at(self.x + dx, self.y + new_dy) and (self.y + new_dy < wrld.height()) and (self.y + new_dy > 0):
                        dy = new_dy
                    else:
                        # Stuck against a wall most likely, try to move away from monster if coming at us and not doing so already
                        dy = 0
                        if dx == 0 and monsters[0].dx == 0:
                            dx = 1
                        elif dx == 0:
                            dx = -self.clamp(monsters[0].x, -1, 1)

                # recalculate optimal path because we deviated from it after escaping
                self.state = 0
            print(dx, dy)
            self.move(dx, dy)        
    
    def createHeuristic(self, wrld):
        heuristics = [[0]*wrld.width()]*wrld.height()
        # monster
        for x in range(wrld.width()):
            for y in range(wrld.height()):
                if wrld.monsters_at(x,y):
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

        return heuristics
    
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
                            if mons[0].avatar == "A" or math.sqrt(dx**2 + dy**2) <= 4:
                                monsters.append((mons[0], 3))


        if monsters:
            # Only return the closest monster
            return min(monsters, key=lambda x: x[0].x^2 + x[0].y^2)

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
                    priority = new_cost + math.sqrt(self.square_dist(current, self.exit)) # + self.heuristic[next[1]][next[0]]
                    frontier.put(next, priority)
                    came_from[next] = current
