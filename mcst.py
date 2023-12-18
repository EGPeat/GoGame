import random
import copy
import math
from typing import List
#Typehint

class MCSTNode:
    def __init__(self, board, parent=None):
        self.board = copy.deepcopy(board)
        self.parent = parent
        self.children = []
        self.visits = 0
        self.wins = 0

class CollectionOfMCST:
    def __init__(self, board, black_outer, black_inner, white_outer, white_inner, iterations, max_sim_depth) -> None:
        self.board = board  # necessary?
        self.black_MCSTS_tuple_list = list()
        self.black_MCSTS: List[MCST] = list()
        self.white_MCSTS_tuple_list = list()
        self.white_MCSTS: List[MCST] = list()

        for idx in range(len(black_outer)):  # must be a more pythonic way
            temp = MCST(board, black_outer[idx], black_inner[idx], iterations, max_sim_depth)
            self.black_MCSTS.append(temp)
            self.black_MCSTS_tuple_list.append([black_outer[idx], black_inner[idx], temp])

        for idx in range(len(white_outer)):  # must be a more pythonic way
            temp = MCST(board, white_outer[idx], white_inner[idx], iterations, max_sim_depth)
            self.white_MCSTS.append(temp)
            self.white_MCSTS_tuple_list.append([white_outer[idx], white_inner[idx], temp])


        for idx in range(len(self.black_MCSTS)):
            output= self.black_MCSTS[idx].run_mcst()
            self.black_MCSTS_tuple_list[idx].append(output)

        for idx in range(len(self.white_MCSTS)):
            output= self.white_MCSTS[idx].run_mcst()
            self.white_MCSTS_tuple_list[idx].append(output)


class MCST:
    def __init__(self, board, outer_pieces, inner_pieces, iterations, max_sim_depth) ->  None:
        self.root: MCSTNode = MCSTNode(board)
        self.iteration_number = iterations
        self.outer = outer_pieces
        self.inner = inner_pieces
        self.remove_these = None
        self.max_simulation_depth = max_sim_depth




    def run_mcst(self):
        for _ in range(self.iteration_number):
            selected_node = self.select(self.root)
            self.expand(selected_node)
            result = self.simulate(selected_node)
            self.backpropagate(selected_node, result)

        # Choose the best move based on the tree search results
        best_move = max(self.root.children, key=lambda child: child.visits)  
        # change this to be something to do with what to kill
        return best_move




    def select(self, node):
        # Select a child node based on the UCT (Upper Confidence Bound for Trees) formula
        exploration_weight = 1.4
        return max(node.children, key=lambda child: (child.wins / child.visits) +
                                                    exploration_weight * (math.sqrt(math.log(node.visits) / child.visits)))

    def expand(self, node):
        # Expand the node by adding a child representing a legal move
        legal_moves = [(i, j) for i in range(node.board.size) for j in range(node.board.size)
                    if node.board.is_valid_move(i, j)]
        ################################################### work on above and below
        if not legal_moves:
            return  # No legal moves, do not expand further

        selected_move = random.choice(legal_moves)
        new_board = copy.deepcopy(node.board)
        new_board.place_stone(selected_move[0], selected_move[1], 1)  # Assume player 1 always makes the next move
        child_node = MCSTNode(new_board, parent=node)
        node.children.append(child_node)

    def simulate(self, node):
        # Simulate a random game from the current node
        current_board = copy.deepcopy(node.board)
        simulation_depth = 0
        # Simulate until the game is over or a certain depth is reached
        while not is_game_over(current_board) and simulation_depth < self.max_simulation_depth:
            legal_moves = [(i, j) for i in range(current_board.size) for j in range(current_board.size)
                        if current_board.is_valid_move(i, j)]
            if legal_moves:
                random_move = random.choice(legal_moves)
                current_board.place_stone(random_move[0], random_move[1], 2)  # Assume opponent (player 2) makes a move
            else:
                break  # No legal moves, end the simulation

        # Evaluate the final state of the game using the rules for stone group life or death
        # Update node statistics based on the evaluation
        # ...

    def backpropagate(node, result):
        # Backpropagate the simulation result up the tree
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent
