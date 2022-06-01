from chess import Gomoku
import random
import math
from collections import defaultdict
from typing import List, Callable, Tuple, Any
import copy

class QLearningAlgorithm():
    def __init__(self, actions: Callable, discount: float, featureExtractor: Callable, explorationProb=0.2):
        self.actions = actions
        self.discount = discount
        self.featureExtractor = featureExtractor
        self.explorationProb = explorationProb
        self.weights = defaultdict(float)
        self.numIters = 0

    # Return the Q function associated with the weights and features
    def getQ(self, state: Tuple, action: Any) -> float:
        score = 0
        for f, v in self.featureExtractor(state, action):
            score += self.weights[f] * v
        return score

    # This algorithm will produce an action given a state.
    # Here we use the epsilon-greedy algorithm: with probability
    # |explorationProb|, take a random action.
    def getAction(self, state: Tuple) -> Any:
        self.numIters += 1
        actions = self.actions(state)
        if not actions or not state:
            return None
        if random.random() < self.explorationProb:
            return random.choice(self.actions(state))
        else:
            return max((self.getQ(state, action), action) for action in self.actions(state))[1]

    # Call this function to get the step size to update the weights.
    def getStepSize(self) -> float:
        return 1.0 / math.sqrt(self.numIters)

    # We will call this function with (s, a, r, s'), which you should use to update |weights|.
    # Note that if s is a terminal state, then s' will be None.  Remember to check for this.
    # You should update the weights using self.getStepSize(); use
    # self.getQ() to compute the current estimate of the parameters.
    def incorporateFeedback(self, state: Tuple, action: Any, reward: int, newState: Tuple) -> None:
        VOpt = 0 if newState is None else max([self.getQ(newState, act) for act in self.actions(newState)])
        QOpt = self.getQ(state, action)
        for f, v in self.featureExtractor(state, action):
            self.weights[f] = self.weights[f] - self.getStepSize() * (QOpt - (reward + self.discount * VOpt)) * v

class GomokuMDP(Gomoku):
    def startState(self):
        self.winner = None
        n = self.board_size
        return [[0]*n for _ in range(n)]

    def actions(self, state):
        if not state: return []
        n = self.board_size
        all_actions = [(i, j) for i in range(n) for j in range(n) if state[i][j] == 0]
        return all_actions

    def succAndProbReward(self, state, action):
        if not action or not state:
            return []
        m, n = action
        if state[m][n] != 0:
            h_label, v_label = chr(ord('A') + m), str(n+1)
            raise ValueError(f"position {h_label}x{v_label} is occupied")
        player = self.next_player
        state[m][n] = player

        succ, prob, reward = state, 1, 0
        won = self.is_win(state, player)
        if won:
            succ = None
            self.winner = player
            reward = 5000
            return [(succ, prob, reward)]

        if self.is_end(state):
            return []
        actions = self.actions(state)
        if not actions:
            succ = None
            reward = 0
            return [(succ, prob, reward)]

        player = -player
        action = random.choice(actions)
        m, n = action
        state[m][n] = player
        won = self.is_win(state, player)
        if won:
            succ = None
            self.winner = player
            reward = 0
            return [(succ, prob, reward)]
        if self.is_end(state):
            return []
        return [(succ, prob, reward)]

    def discount(self):
        return 0.9

    def is_win(self, state, player):
        N = self.board_size
        stone = [(m, n) for m in range(N) for n in range(N) if state[m][n] == player ]
        if len(stone) < 5:
            return False
        stone_sort = sorted(stone)
        for x, y in stone_sort:
            row, col, diag, adiag = [], [], [], []
            for i in range(1, 5):
                row.append((x, y+i))
                col.append((x+i, y))
                diag.append((x+i, y+i))
                adiag.append((x+i, y-i))
            stone_set = set(stone_sort)
            win = (stone_set.issuperset(set(row))
                   or stone_set.issuperset(set(col))
                   or stone_set.issuperset(set(diag))
                   or stone_set.issuperset(set(adiag)))
            if win: return True
        return False

    def is_end(self, state):
        actions = self.actions(state)
        return len(actions) == 0 or self.winner is not None

############################################################

# Perform |numTrials| of the following:
# On each trial, take the MDP |mdp| and an RLAlgorithm |rl| and simulates the
# RL algorithm according to the dynamics of the MDP.
# Each trial will run for at most |maxIterations|.
# Return the list of rewards that we get for each trial.
def simulate(mdp, rl, numTrials=10, maxIterations=1000, verbose=False,
             sort=False):
    # Return i in [0, ..., len(probs)-1] with probability probs[i].
    def sample(probs):
        target = random.random()
        accum = 0
        for i, prob in enumerate(probs):
            accum += prob
            if accum >= target: return i
        raise Exception("Invalid probs: %s" % probs)

    totalRewards = []  # The rewards we get on each trial
    for trial in range(numTrials):
        state = mdp.startState()
        sequence = [state]
        totalDiscount = 1
        totalReward = 0
        for _ in range(maxIterations):
            action = rl.getAction(state)
            transitions = mdp.succAndProbReward(state, action)
            # ah, I think this sort is throwing things off
            if sort: transitions = sorted(transitions)
            if len(transitions) == 0:
                rl.incorporateFeedback(state, action, 0, None)
                break

            # Choose a random transition
            i = sample([prob for newState, prob, reward in transitions])
            newState, prob, reward = transitions[i]
            sequence.append(action)
            sequence.append(reward)
            sequence.append(newState)

            rl.incorporateFeedback(state, action, reward, newState)
            totalReward += totalDiscount * reward
            totalDiscount *= mdp.discount()
            state = newState
        if verbose:
            print(("Trial %d (totalReward = %s): %s" % (trial, totalReward, sequence)))
        totalRewards.append(totalReward)
    return totalRewards

def manhattanDistance( xy1, xy2 ):
  "Returns the Manhattan distance between points xy1 and xy2"
  return abs( xy1[0] - xy2[0] ) + abs( xy1[1] - xy2[1] )


gomoku_game = GomokuMDP(8)

def simpleFeatureExtractor(state, action) -> List[Tuple[Tuple, int]]:
    manhattanDist = 0
    if not action or not state: return [(('manhattanDist', manhattanDist, action), 0)]
    N = len(state)
    white_stone = [(m, n) for m in range(N) for n in range(N) if state[m][n] == 1 ]
    black_stone = [(m, n) for m in range(N) for n in range(N) if state[m][n] == -1 ]
    player = 1
    if len(white_stone) > len(black_stone):
        player = -1
    x, y = action

    stone = [manhattanDistance((m, n), (x, y)) for m in range(N) for n in range(N) if state[m][n] == player ]
    if stone:
        manhattanDist = sum(stone)/len(stone)
    return [(('manhattanDist', manhattanDist, action), -manhattanDist)]

def interactive(rl):
    game = Gomoku(n=8, gui=True)
    game.draw_board()
    while game.winner is None:
        action = game.human_step()
        if action is None:
            break
        game.step(action)
        action = rl.getAction(game.chess_board)
        game.step(action)

q_rl = QLearningAlgorithm(gomoku_game.actions, gomoku_game.discount(), simpleFeatureExtractor)
q_rewards = simulate(gomoku_game, q_rl, numTrials=200)
interactive(q_rl)
