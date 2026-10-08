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
from qlearner import Drill1, Drill2, Drill3

#[abs(dx to closest monster), 
# dy to closest monster, 
# on bomb x
# on bomb y, 
# abs(dy to closest wall), 
# on explosion, 
# abs(dx to hole or exit), 
# dy to hole or exit]

mover3 = Drill3(weights=[-150.95228131826397, -1.0, 0.0, 0.0, 0.0, -10.0, 32.9713332267997, 184.983074579649],
                features = [
        lambda x: 0 if x is None else 1/(1+x),
        lambda x: 0 if x is None else 1/(2+x),
        lambda x: 0,
        lambda x: 0,
        lambda x: 0,
        lambda x: 0,
        lambda x: 0 if x is None else 1/(3+x),
        lambda x: 0 if x is None else 1/(2+x)
])

drill2_features = [
    lambda x: 0 if x is None else 1/(1+x),
    lambda x: 0 if x is None else 1/(1+x),
    lambda x: 0 if x is None else x, 
    lambda x: 0 if x is None else x,
    lambda x: 0,
    lambda x: 0 if x is None else x,
    lambda x: 0 if x is None else 1/(2+x),
    lambda x: 0 if x is None else 1/(2+x)
]

drill2_weights = [-4735.706896961447, -1.0, -323.73951212945417, -116.00925059963089, 0.0, -3469.112334856907, 1.0, 1.0]


class TestCharacter(CharacterEntity):
    # Represent theb y location of the walls, each block is one of the rectangular regions between two walls
    wall_ys = [3, 7, 11, 15, 18]
    block = 0
    # State 0 is haven't done A*, state 1 is following A*
    state = 0
    # Exit coords in our current map
    exit = (8, 18)
    optimal_path = []
    heuristic = []
    bomb_coords = ()
    # INITIAL WEIGHTS FOR PARAMETERS: exit dist, monster dist, bomb dx, bomb dy, hole dist, 
    weights = [1, -1, -1, -1, 1]

    def __init__(self, name, avatar, x, y, mover):
        CharacterEntity.__init__(self, name=name, avatar=avatar, x=x, y=y)
        self.mover = mover

    def do(self, wrld):
        dx = 0
        dy = 0
        # get optimal path to goal
        if self.state == 0:
            self.optimal_path = self.a_star(wrld)
            self.state = 1

        if self.state == 1:
            next = self.optimal_path.pop(0)
            dx = next[0] - self.x
            dy = next[1] - self.y
            # If a wall is on the way, blow it up!
            if (wrld.wall_at(self.x + dx, min(self.y + dy + 3, wrld.height()-1)) or 
            wrld.wall_at(self.x + dx, min(self.y + dy + 2, wrld.height()-1)) or 
            wrld.wall_at(self.x + dx, min(self.y + dy + 1, wrld.height()-1)) or 
            wrld.wall_at(self.x + dx, min(self.y + dy, wrld.height()-1))):
                self.place_bomb()
                self.bomb_coords = (self.x, self.y)
                self.state = 3
                dy = 0
            
            self.move(dx, dy)
            return

        # Drill in which we're trying to reach the next hole to place a bomb OR the exit if we're at the end
        if self.state == 2:
            # If we're at the hole, recompute optimal path. This will either head straight to exit if path exists or restart the blowing up process
            if self.block <= 3 and self.y > self.wall_ys[self.block] - 1:
                self.state = 0
                self.block += 1
                self.do(wrld) 

            # Get the best possible move
            mover = mover3
            possible_moves = self.look_for_empty_cell(wrld, (self.x, self.y), in_a_star=False)
            moves_dict = {}
            for move in possible_moves:
                if self.block <= 3:
                    moves_dict[move] = mover.get_parameters(wrld, move, self.wall_ys[self.block])
                else:
                    moves_dict[move] = mover.get_parameters(wrld, move, wrld.height())
            (best_move, _) = mover.best_move(moves_dict)
            self.move(best_move[0] - self.x, best_move[1] - self.y)

            # TRAINING CODE
            # possible_moves = self.look_for_empty_cell(wrld, (self.x, self.y), in_a_star=False)
            # moves_dict = {}
            # for move in possible_moves:
            #     moves_dict[move] = self.mover.get_parameters(wrld, move, 2)
            
            # (best_move, _) = self.mover.best_move(moves_dict)
            # print(best_move)
            # self.move(best_move[0] - self.x, best_move[1] - self.y)
        
            # (next_wrld, _) = wrld.next()
            # reward = self.mover.reward(wrld, best_move)
            
            # future_moves = self.look_for_empty_cell(next_wrld, best_move, in_a_star=False)
            # moves_dict = {}
            # for move in future_moves:
            #     moves_dict[move] = self.mover.get_parameters(next_wrld, move, 2)

            # self.mover.update(reward, moves_dict, self.mover.get_parameters(wrld, best_move, 2))

        # State in which we wait for a bomb to blow up and try to stay alive
        if self.state == 3:
            # If the explosion and bomb is gone from where we placed it, we're done waiting
            if not(wrld.explosion_at(self.bomb_coords[0], self.bomb_coords[1])) and not(wrld.bomb_at(self.bomb_coords[0], self.bomb_coords[1])):
                # If the wall is gone, head to the hole that was left there
                if self.block <= 3 and not(wrld.wall_at(self.bomb_coords[0], self.wall_ys[self.block])):
                    self.state = 2
                    self.do(wrld)
                # If the wall is still there, recompute the best path and blow up obstacles
                elif self.block <= 3 and wrld.wall_at(self.bomb_coords[0], self.wall_ys[self.block]):
                    self.state = 0
                    self.do(wrld)
                    return
                # If we're at the last block, try to head for the exit
                elif self.block > 3:
                    self.state = 2
                    self.do(wrld)
                    return
                
            # Get the best possible move
            mover = Drill2(weights=drill2_weights, features=drill2_features, bomb=(self.bomb_coords[0], self.bomb_coords[1]))
            possible_moves = self.look_for_empty_cell(wrld, (self.x, self.y), in_a_star=False)
            moves_dict = {}
            for move in possible_moves:
                moves_dict[move] = mover.get_parameters(wrld, move)

            (best_move, _) = mover.best_move(moves_dict)
            self.move(best_move[0] - self.x, best_move[1] - self.y)
    
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

    def look_for_empty_cell(self, wrld, current, rnge=1, in_a_star=True):
        # List of empty cells
        cells = []
        # Go through neighboring cells
        for dx in range(-rnge, rnge+1):
            # Avoid out-of-bounds access
            if ((current[0] + dx >= 0) and (current[0] + dx < wrld.width())):
                for dy in range(-rnge, rnge+1):
                    # Avoid out-of-bounds access
                    if ((current[1] + dy >= 0) and (current[1] + dy < wrld.height())):
                        if in_a_star or not wrld.wall_at(current[0] + dx, current[1] + dy):
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
