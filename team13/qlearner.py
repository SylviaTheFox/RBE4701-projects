import math


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
            # Iterate through all features to compute
            score = self.evaluate_score(parameters)
            if score > best_score:
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
        print(self.weights)
        
        
        """
        self = self
        wrld = world object
        curr_pos = where we are looking at
        
        return: [abs(dx to closest monster), abs(dy to closest monster), time till explosion or 0, abs(dx to closest wall), abs(dy to closest wall), bomb planted?, abs(dx to hole or exit), dy to hole or exit]
        """
    def get_prameters(self, wrld, curr_pos):
        parameters = [0] * 8
        monsters = []
        my_pos = (0,0)
        for x in range(wrld.width() - 1):
            for y in range(wrld.height() - 1):
                if wrld.monsters_at(x,y):
                    monsters.append((x, y))
                if wrld.character_at((x,y)):
                    my_pos = (x,y)
                    
        if (wrld.explosion_at(curr_pos[0], curr_pos[1])):
            parameters[2] = wrld.explosion_at(curr_pos[0], curr_pos[1]).timer.timer + 1
            parameters[5] = 1
                    
        dist = 9999999999999999
        closest_m = (0,0)
        for m in monsters:
            dx = m[0] - my_pos[0]
            dy = m[1] - my_pos[1]
            if dist > math.sqrt(dx*dx+dy*dy):
                closest_m = m
                dist = math.sqrt(dx*dx+dy*dy)
        parameters[0] = abs(closest_m[0] - my_pos[0])
        parameters[1] = abs(closest_m[1] - my_pos[1])
        
        counter = 1
        while parameters[3] == 0:
            if curr_pos[0] + counter >= wrld.width or curr_pos[0] - counter < 0 or wrld.wall_at(curr_pos[0] + counter, curr_pos[1]) or wrld.wall_at(curr_pos[0] - counter, curr_pos[1]):
                parameters[3] = counter
        counter = 1
        while parameters[4] == 0:
            if curr_pos[1] + counter >= wrld.height or curr_pos[1] - counter < 0 or wrld.wall_at(curr_pos[0], curr_pos[1] + counter) or wrld.wall_at(curr_pos[0], curr_pos[1] - counter):
                parameters[4] = counter
            
        # parameters[6] = 0
        # while parameters[6] + my_pos[0] < wrld.height and not wrld.wall_at(my_pos[0 + parameters[6]], my_pos[1]):
        #     parameters[6] += 1

        search = self.search_for_hole(wrld, curr_pos[0], my_pos[1])
        if search:
            parameters[6] = search[0]
            parameters[7] = search[1] + my_pos[1] - curr_pos[1]
        
        return parameters
    
        """
        finds the dx and dy to the nearest hole below, or false if no hole
        self = self
        wrld = world
        start_x, start_y = starting positions for search
        """
    def search_for_hole(self, wrld, start_x, start_y):
        dy = 0
        walls_found = False
        for y in range(start_y + 1, wrld.height()):
            for x in range(0, wrld.width()):
                if wrld.wall_at(x, y):
                    walls_found = True
                    dy = y - start_y
                    break
            if walls_found:
                break
        if not walls_found:
            # HANDLE MOVING TO EXIT
            dx = wrld.width() - start_x - 1
            dy = wrld.height() - start_y - 1
            return (dx, dy)
        for dx in range(wrld.width()):
            if start_x - dx >= 0 and not wrld.wall_at(dx+start_x, start_y + dy):
                return (dx, dy)
            if start_x + dx < wrld.width() and not wrld.wall_at(start_x - dx, start_y + dy):
                return (dx, dy)
            
        return False


class Drill1(QLearner):

    def reward(self, wrld, curr_pos):
        pass

    def get_parameters(self, wrld, curr_pos):
        pass

class Drill2(QLearner):

    def reward(self, wrld, curr_pos):
        pass

    def get_parameters(self, wrld, curr_pos):
        pass

class Drill3(QLearner):

    def reward(self, wrld, curr_pos):
        pass

    def get_parameters(self, wrld, curr_pos):
        pass
