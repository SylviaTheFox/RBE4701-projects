import math
import pygame

class QLearner():

    weights = []
    features = []

    def __init__(self, weights, features, learning_rate=0.01):
        """
        
        Keyword arguments:
        weights -- An array of numerical weights
        features -- An array of lambda functions to use when computing each feature
        """
        
        self.weights = weights
        self.features = features
        self.learning_rate = learning_rate

    def best_move(self, moves):
        """Chooses the best possible move
        
        Keyword arguments:
        moves -- A dictionary of the form {move: parameters[]} containing all possible moves and their respective parameters
        Return: the best possible move along its score
        """
        best_move = None
        best_score = -1000000
        for move, parameters in moves.items():
            # Iterate through all features to compute their score and keep the best
            score = self.evaluate_score(parameters)

            if score >= best_score:
                best_score = score
                best_move = move

        return (best_move, best_score)

    def evaluate_score(self, parameters):
        """Computes the score for a specific set of parameters
        
        Keyword arguments:
        parameters -- An array of numbers corresponding to the parameters for each move (e.g. dist to exit, dist to monster, etc.)
        Return: The score using our current weights
        """
        score = 0
        for i, feature in enumerate(self.features):
            score += self.weights[i] * feature(parameters[i])
        return score


    def update(self, reward, future_moves, current_move):
        """Updates the weights based on the current move made and the reward obtained
        
        Keyword arguments:
        reward -- Reward gotten from making the current move
        future_moves -- Set of possible moves from the current state
        current_move -- Parameters corresponding to the move we just made
        Return: None
        """
        current_score = self.evaluate_score(current_move)
        (_, best_score) = self.best_move(future_moves)
        delta = (reward + 0.9 * best_score) - current_score
        for i, feature in enumerate(self.features):
            self.weights[i] += self.learning_rate * feature(current_move[i]) * delta
        
        
    def get_parameters(self, wrld, curr_pos, start_y):
        """
        self = self
        wrld = world object
        curr_pos = where we are looking at
        start_y = the hole we're trying to reach
            
        return: [abs(dx to closest monster), abs(dy to closest monster), time till explosion or 0, abs(dx to closest wall), abs(dy to closest wall), bomb planted?, abs(dx to hole or exit), dy to hole or exit]
        """
        parameters = [None] * 8
        monsters = []
        parameters[5] = -1
        # Find monsters at a reasonable distance from us
        for x in range(wrld.width()):
            for y in range(max(curr_pos[1] - 3, 0), start_y+4):
                mons = wrld.monsters_at(x, y)
                if mons:
                    monsters.append((x, y))
                
        if (wrld.explosion_at(curr_pos[0], curr_pos[1])):
            parameters[5] = 1
                    
        dist = 9999999999999999
        closest_m = None
        for m in monsters:
            dx = m[0] - curr_pos[0]
            dy = m[1] - curr_pos[1]
            if dist > abs(dx) + abs(dy):
                closest_m = m
                dist = abs(dx) + abs(dy)
        if closest_m:
            parameters[0] = dist

        search = self.search_for_hole(wrld, curr_pos[0], start_y)

        if search:
            # Abs for the x and not the y because we want to value being below the hole more than being above it
            parameters[6] = abs(search[0] - curr_pos[0])
            parameters[7] = search[1] - curr_pos[1]
        return parameters
       
    def search_for_hole(self, wrld, start_x, start_y):
        """
        finds the dx and dy to the nearest hole below, or false if no hole
        self = self
        wrld = world
        start_x, start_y = starting positions for search
        """
        dy = 0
        walls_found = False
        for y in range(start_y - 1, wrld.height()):
            for x in range(0, wrld.width()):
                if wrld.wall_at(x, y):
                    walls_found = True
                    dy = y - start_y
                    break
            if walls_found:
                break
        if not walls_found:
            # HANDLE MOVING TO EXIT
            return (wrld.width() - 1, wrld.height() - 1)
            
        for x in range(wrld.width()):
            if not wrld.wall_at(x, dy+start_y):
                return (x, dy+start_y)
            
        return False


class Drill1(QLearner):

    def reward(self, wrld, curr_pos):
        score = wrld.time - 5000
        if wrld.exit_at(curr_pos[0], curr_pos[1]):
            score += 5000
        elif wrld.monsters_at(curr_pos[0], curr_pos[1]):
            score -= 5000
        return score


class Drill2(QLearner):
    hole = None
    bomb = ()

    def __init__(self, weights, features, bomb, learning_rate=0.01, hole=None):
        super().__init__(weights, features, learning_rate)
        self.hole = hole
        self.bomb= bomb

    def reward(self, wrld, curr_pos):
        score = wrld.time - 5000
        if wrld.monsters_at(curr_pos[0], curr_pos[1]) or wrld.explosion_at(curr_pos[0], curr_pos[1]):
            score -= 5000

        elif not(wrld.explosion_at(self.bomb[0], self.bomb[1])) and not(wrld.bomb_at(self.bomb[0], self.bomb[1])):
            score += 5000
            quit_event = pygame.event.Event(pygame.QUIT)
            pygame.event.post(quit_event)
        return score

    def get_parameters(self, wrld, curr_pos):
            """
            self = self
            wrld = world object
            curr_pos = where we are looking at
                
            return: [abs(dx to closest monster), abs(dy to closest monster), time till explosion or 0, abs(dx to closest wall), abs(dy to closest wall), bomb planted?, abs(dx to hole or exit), dy to hole or exit]
            """
            parameters = [None] * 8
            monsters = []
            parameters[5] = -1
            # Search for monsters at a reasonable distance from us only
            for x in range(wrld.width()):
                for y in range(max(curr_pos[1] - 3, 0), min(curr_pos[1] + 4, wrld.height()-1)):
                    mons = wrld.monsters_at(x, y)
                    if mons:
                        monsters.append((x+mons[0].dx, y+mons[0].dy))

            # Only consider an unexploded bomb if we're close to it if it explodes and the explosion happens soon
            bomb = wrld.bomb_at(self.bomb[0], self.bomb[1])
            if curr_pos[0] == self.bomb[0] and bomb and bomb.timer < 3:
                parameters[2] = 1
            if curr_pos[1] == self.bomb[1] and bomb and bomb.timer < 3:
                parameters[3] = 1

            if (wrld.explosion_at(curr_pos[0], curr_pos[1])):
                parameters[5] = 1
                        
            dist = 9999999999999999
            closest_m = None
            for m in monsters:
                dx = m[0] - curr_pos[0]
                dy = m[1] - curr_pos[1]
                if dist >= math.sqrt(dx*dx+dy*dy):
                    closest_m = m
                    dist = math.sqrt(dx*dx+dy*dy)
            if closest_m:
                parameters[0] = dist

            if self.hole:
                # Abs for the x and not the y because we want to value being below the hole more than being above it
                parameters[6] = abs(self.hole[0] - curr_pos[0])
                parameters[7] = curr_pos[1] - self.hole[1]
            return parameters

class Drill3(QLearner):

    def reward(self, wrld, curr_pos):
        score = wrld.time - 5000
        if wrld.monsters_at(curr_pos[0], curr_pos[1]) or wrld.explosion_at(curr_pos[0], curr_pos[1]):
            score -= 5000

        elif curr_pos[1] > 2:
            monsters = []
            score += 5000 
            # Have the winning reward also depend on how close to a monster we ended up
            for x in range(wrld.width()):
                for y in range(max(curr_pos[1] - 3, 0), wrld.height()):
                    mons = wrld.monsters_at(x, y)
                    if mons:
                        monsters.append((x+mons[0].dx, y+mons[0].dy))
            for m in monsters:
                score -= 500*1/(1 + abs(m[0] - curr_pos[0]))
                score -= 500*1/(1 + abs(m[1] - curr_pos[1]))
            quit_event = pygame.event.Event(pygame.QUIT)
            pygame.event.post(quit_event)
        return score

