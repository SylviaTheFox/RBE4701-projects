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