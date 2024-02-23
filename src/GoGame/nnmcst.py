from GoGame.goclasses import BoardNode, BoardString
from typing import Tuple, List, Set, Union, Type, Dict, FrozenSet, Literal
from GoGame.player import Player
from GoGame.mcst import MCSTNode, MCST
import GoGame.config as cf
import math
from GoGame.neuralnet import neural_net_calcuation, generate_17_length
import copy
from numpy import argmax


class NNMCSTNode(MCSTNode):
    def __init__(self, turn_person: Tuple[Player, Player], training_info: List[str], prob,
                 board_list=None, killed_last: Union[Set[None], Set[BoardNode]] = set(),
                 placement_location: Tuple[Union[str, Tuple[int, int]], int, Tuple[int, int, int]] = ((-1, -1), -1, -1),
                 parent: Union[None, Type['NNMCSTNode']] = None) -> None:
        """
        Initializes an MCSTNode instance representing a Monte Carlo Search Tree node.

        Parameters:
            turn_person (Tuple[Player, Player]): Tuple of two Player instances representing whose_turn and not_whose_turn
            training_info (List[str]): list of strings representing boardstates in previous turns.
            prob: probability of being chosen by the parent NNMCSTNode.
            board_list (List[str]): List of strings representing the current state of the board.
            killed_last Set[BoardNode] or Empty Set: Set of BoardNode instances representing pieces killed in the last turn.
            placement_location: Tuple containing information about the placement location (move, row, col, and stone color).
            parent (MCSTNode): Reference to the parent MCSTNode instance, if one exists.

        Attributes:
            placement_choice: The chosen placement location (move) for this node.
            choice_info: Information about the placement location.
            board_list (List[str]): List of strings representing the current state of the board.
            parent (MCSTNode): Reference to the parent MCSTNode instance.
            children (List[MCSTNode]): List of child MCSTNode instances.
            move_choices (Dict[str, BoardNode]): Dictionary mapping moves to BoardNode instances.
            prior_probability (float): Probability of this node being chosen by its parent node.
            number_times_chosen (int): Number of times this node or it's children were chosen.
            total_v_children (float): Total value output of this node and all of it's children.
            mean_value_v: total_v_children divided by the number of times this node and it's children were chosen.
            ai_training_info_node (List[str]): training_info parameter.
            killed_last_turn (Union[Set[None], Set[BoardNode]]): Set of BoardNode instances killed in the last turn.
            child_killed_last (Union[Set[BoardNode], Set[None]]): Set of BoardNode instances killed by child nodes.
            visit_kill (Set[BoardNode]): Set of BoardNode instances representing visited and killed stones.
            whose_turn (Player): Player instance representing the current player's turn.
            not_whose_turn (Player): Player instance representing the not current player's turn.
            cache_hash (str): Hash value representing the state of the MCSTNode for caching purposes.

        Note:
            The default values for parameters are provided for optional attributes.
        """
        self.placement_choice = placement_location[0]
        self.choice_info = placement_location
        self.board_list: List[str] = board_list
        self.parent: Union[None, Type['NNMCSTNode']] = parent
        self.children: List[NNMCSTNode] = []
        self.move_choices: Dict[str, BoardNode] = dict()

        self.prior_probability: float = prob
        self.number_times_chosen: int = 0
        self.total_v_children: float = 0
        self.mean_value_v: float = 0
        self.ai_training_info_node = training_info

        self.killed_last_turn: Union[Set[None], Set[BoardNode]] = killed_last
        self.child_killed_last: Union[Set[BoardNode], Set[None]] = set()
        self.visit_kill: Set[BoardNode] = set()
        self.whose_turn: Player = turn_person[0]
        self.not_whose_turn: Player = turn_person[1]
        self.mcstnode_init()
        self.cache_hash: str = self.generate_cache()


class NNMCST(MCST):
    def __init__(self, board: List[List[BoardNode]], training_info: List[str], white_board: str, black_board: str,
                 iterations: int, turn_person: Tuple[Player, Player], nn, turnnum: int) -> None:
        """
        Initializes an MCST instance representing a Monte Carlo Search Tree for game tree traversal and decision-making.

        Parameters:
            board (List[List[BoardNode]]): 2D list representing the current state of the board with BoardNode instances.
            training_info (List[str]): list of strings representing boardstates in previous turns.
            white_board (str): A string representing the entire board being of the value held by the white player
            black_board (str): A string representing the entire board being of the value held by the black player
            iterations (int): Number of iterations for Monte Carlo Tree Search.
            turn_person (Tuple[Player, Player]): Tuple of two Player instances representing the current and not current player.
            nn: neural net to be used to improve the MCST.
            turnnum (int): the turn number

        Attributes:
            board: 2D list representing the current state of the board with BoardNode instances.
            board_BoardString: BoardString representing the entire board.
            training_info (List[str]): list of strings representing boardstates in previous turns.
            white_board (str): A string representing the entire board being of the value held by the white player
            black_board (str): A string representing the entire board being of the value held by the black player
            cache: Dictionary caching frozen sets of BoardNode instances for each unique board state.
            win_cache: Dictionary caching win statistics for each unique board state.
            cache_hash: Hash value representing the state of the MCST for caching purposes.
            iteration_number: Number of iterations for Monte Carlo Tree Search.
            max_simulation_depth: Maximum simulation depth for Monte Carlo Tree Search.
            root: Root node of the Monte Carlo Search Tree.
            nn: neural net to be used
            nn_bad: copy of neural net, or a more outdated version.
            temp: temperature to be used by some functions. Either 1 or 0.1
        """

        self.board = board
        self.board_BoardString = None
        self.ai_training_info = copy.deepcopy(training_info)
        self.ai_white_board = white_board
        self.ai_black_board = black_board

        self.cache: Dict[str, FrozenSet[BoardNode]] = {}
        self.win_cache: Dict[str, Tuple[int, int]] = {}
        self.cache_hash: str = None
        self.secondary_init()
        self.iteration_number: int = iterations
        board_list_for_root = self.make_board_string()
        self.root: NNMCSTNode = NNMCSTNode(turn_person, self.ai_training_info, 1, board_list_for_root,
                                           placement_location=("Root", -1, -1))
        self.neural_net_inst = nn
        self.turn_num = turnnum
        if turnnum <= 30:
            self.temp = 1
        else:
            self.temp = 0.1

    def secondary_init(self) -> None:
        '''Helper function for init.'''
        temp_set: Set[BoardNode] = set()
        for idx_1 in range(9):
            for idx_2 in range(9):
                temp_set.add(self.board[idx_1][idx_2])
        self.board_BoardString = BoardString(cf.rgb_grey, temp_set)

    def best_child_finder(self, node: NNMCSTNode) -> NNMCSTNode:
        '''Finds the best child of the given node, and then returns it.'''
        current_best_val = float('-inf')
        current_best_child: NNMCSTNode = None

        for child in node.children:
            child_val = self.get_UCB_score(child)
            if child_val > current_best_val:
                current_best_val = child_val
                current_best_child = child
        return current_best_child

    def get_UCB_score(self, child: NNMCSTNode) -> float:
        '''Calculate the Upper Confidence Bound (UCB) score for a given child node, and returns it as a float.'''
        explor_weight = 1.4
        t_node = child
        if t_node.parent:
            t_node = t_node.parent
        penalty_term_inner_upper = 0
        for sibling in t_node.children:
            penalty_term_inner_upper += sibling.number_times_chosen

        penalty_term_inner_upper = math.sqrt(penalty_term_inner_upper)
        penalty_term_inner = penalty_term_inner_upper / (1 + child.number_times_chosen)
        penalty_term = explor_weight * child.prior_probability * penalty_term_inner
        ucb_value = child.mean_value_v + penalty_term
        return ucb_value

    def get_deep_score(self, child: NNMCSTNode) -> float:
        '''Calculate the score used by Deep Mind to choose the final output for a given child node, and returns it as a float.'''
        t_node = child
        if t_node.parent:
            t_node = t_node.parent
        lower_value = 0
        for sibling in t_node.children:
            lower_value += math.pow(sibling.number_times_chosen, (1 / self.temp))

        upper_value = math.pow(child.number_times_chosen, (1 / self.temp))
        return (upper_value / lower_value)

    def backpropagate(self, node: NNMCSTNode, value_output: int) -> None:
        '''Backpropagates the result of a simulation through the tree.'''
        while node is not None:
            node.number_times_chosen += 1
            node.total_v_children += value_output
            node.mean_value_v = node.total_v_children / node.number_times_chosen
            node = node.parent

    def run_mcst(self) -> Tuple[int, List[float]]:
        """
        Run the Monte Carlo Search Tree (MCST) algorithm.
        Returns:
            bool: True if the internal pieces should be counted as dead, False otherwise.
        """
        nn_input_backup = self.nn_input_generation(self.root, training=True)
        for idx in range(self.iteration_number):
            selected_node = self.select(self.root, idx)
            value_output = self.expand(selected_node, idx)
            self.backpropagate(selected_node, value_output)
        output_chances = self.get_choice_info()
        choice_weights = self.get_deep_info()
        the_range = []
        for idx in range(82):
            the_range.append(idx)
        from random import choices
        if self.turn_num < 60:
            the_range = the_range[:-1]
            choice_weights = choice_weights[:-1]
        location = choices(the_range, weights=choice_weights, k=1)
        return location[0], output_chances, nn_input_backup

    def get_choice_info(self) -> List[float]:
        '''Returns a list representing the number of times each location was choosen by the MCST.'''
        chance_list: List[float] = [0] * 82
        for spawn in self.root.children:
            if spawn.choice_info[0][1] != 'a':
                location = spawn.choice_info[0][0] * 9 + spawn.choice_info[0][1]
            else:
                location = 81
            chance_list[location] = spawn.number_times_chosen / (self.iteration_number)
        return chance_list

    def get_deep_info(self) -> List[float]:
        '''Returns a list representing the deepmind value for each location on the board.'''
        chance_list: List[float] = [0] * 82
        for spawn in self.root.children:
            spawn_value = self.get_deep_score(spawn)
            if spawn.choice_info[0][1] != 'a':
                location = spawn.choice_info[0][0] * 9 + spawn.choice_info[0][1]
            else:
                location = 81
            chance_list[location] = spawn_value
        return chance_list

    def select(self, node: NNMCSTNode, idx: int) -> NNMCSTNode:
        '''Selects a node for expansion, as well as generates child nodes, when necessary.'''
        if self.is_winning_state(node):
            return node
        if not node.children:
            self.load_board_string(node)
            legal_moves = self.generate_moves(node)
            _, policy_output = self.child_nn_info(node)
            for move in legal_moves:
                probability = self.get_probabilities_for_child(policy_output, move)
                self.generate_child(move, node, idx, probability)
            return self.select(node, idx)

        return self.select_non_init(node, idx)

    def select_non_init(self, node: NNMCSTNode, idx: int) -> NNMCSTNode:
        '''
        Helper function for the select function, implementing behavior for when the current node is not a winning state,
        or when the root has children.
        '''
        root_child = self.best_child_finder(node)
        while root_child.children:
            root_child = self.best_child_finder(root_child)
        self.load_board_string(root_child)
        if self.is_winning_state(root_child):
            return root_child
        legal_moves = self.generate_moves(root_child)
        _, policy_output = self.child_nn_info(root_child)
        for move in legal_moves:
            probability = self.get_probabilities_for_child(policy_output, move)
            self.generate_child(move, root_child, idx, probability)
        return root_child

    def is_winning_state(self, node: NNMCSTNode) -> bool:
        '''Checks if the current node represents a winning state.'''
        if node.cache_hash[1:] in self.win_cache:
            cache_value = self.win_cache[node.cache_hash[1:]]
            if cache_value[0] == 1:
                return True
            else:
                return False
        else:
            return False

    def expand(self, node: NNMCSTNode, idx) -> None:
        '''Expands the MCST by choosing a move and creating a child node.'''
        self.load_board_string(node)
        if self.is_winning_state(node):
            return
        value_output, policy_output = self.child_nn_info(node)
        legal_move = False
        selected_move = None
        policy_copy = copy.copy(policy_output)
        while not legal_move:
            move = argmax(policy_copy)
            if move != 81:
                policy_copy[0][move] = -2
                board_node = self.board[move // 9][move % 9]
                legal_move = self.test_piece_placement(board_node, node)
                selected_move = board_node
            else:
                selected_move = "Pass"
                legal_move = True
        probability = self.get_probabilities_for_child(policy_output, selected_move)
        self.generate_child(selected_move, node, idx, probability)
        return value_output

    def generate_moves(self, node: NNMCSTNode, simulate=False, final_test=False) -> List[Union[BoardNode, Literal["Pass"]]]:
        '''
        Generates a list of legal moves for the given node based on the current board state.
        Caches the result for future use.
        Returns the possible moves as a List of moves, with moves represented as BoardNodes or as "Pass".
        '''
        if self.cache_hash in self.cache:
            moves = list(self.cache[self.cache_hash])
            moves += ["Pass"]
            return moves
        legal_moves: List[Union[BoardNode, Literal["Pass"]]] = ["Pass"]
        legal_moves_set: Union[Set[None], Set[BoardNode]] = set()
        for board_node in self.board_BoardString.member_set:
            output = self.test_piece_placement(board_node, node, simulate, final_test)
            if output:
                legal_moves.append(board_node)
                legal_moves_set.add(board_node)
        cache_value = frozenset(legal_moves_set)
        self.cache[self.cache_hash] = cache_value

        return legal_moves

    def generate_child(self, selected_move: Union[BoardNode, Literal["Pass"]], node: NNMCSTNode, idx, prob) -> None:
        '''Choose a move and expand the MCST with the selected move.
        When a new node is added, the turn ordering is switched due to a play being already made.'''
        original_board = self.make_board_string()
        if selected_move == "Pass":
            if "Pass" not in node.move_choices.keys():
                node.switch_player()
                temp = self.make_board_string()
                temp_train_info = node.ai_training_info_node
                temp_train_info.append(temp)
                child_node = NNMCSTNode((node.whose_turn, node.not_whose_turn), temp_train_info, prob,
                                        original_board, node.child_killed_last,
                                        ("Pass", idx, node.not_whose_turn.color), parent=node)
                node.children.append(child_node)
                node.move_choices["Pass"] = child_node
                node.switch_player()
            return

        location_tuple = (selected_move.row, selected_move.col)

        if f"{location_tuple}" not in node.move_choices:
            self.expand_play_move(location_tuple, node)
            board_list = self.make_board_string()
            temp_train_info = node.ai_training_info_node
            temp_train_info.append(board_list)
            child_node = NNMCSTNode((node.whose_turn, node.not_whose_turn), temp_train_info, prob,
                                    board_list, node.child_killed_last,
                                    ((location_tuple[0], location_tuple[1]), idx, node.not_whose_turn.color), parent=node)
            self.reload_board_string(original_board)
            node.children.append(child_node)
            node.move_choices[f"{location_tuple}"] = child_node
            node.switch_player()
        return

    def expand_play_move(self, move, node: NNMCSTNode) -> None:
        '''Expands the MCST by playing the given move on the board.'''
        new_board_piece: BoardNode = self.board[move[0]][move[1]]
        node.child_killed_last.clear()
        self.kill_stones(new_board_piece, node, testing=False)
        new_board_piece.stone_here_color = node.whose_turn.unicode
        node.switch_player()

    def child_nn_info(self, node: NNMCSTNode):
        '''Generates the value and policy for a MCSTNode.
        Returns a tuple of a float and an array of length 82'''
        nn_input = self.nn_input_generation(node)
        val_output, policy_output = neural_net_calcuation(nn_input, 9, self.neural_net_inst)
        return (val_output, policy_output)

    def nn_input_generation(self, node: NNMCSTNode, training: bool = False) -> List[str]:
        '''Generates a list of strings of length 16 or 17 representing the last 8 turns.'''
        nn_input = []
        if node.whose_turn.unicode == cf.rgb_black:
            nn_input = node.ai_training_info_node[-8:]
            nn_input.reverse()
            nn_input.append(self.ai_black_board)
        else:
            nn_input = node.ai_training_info_node[-8:]
            nn_input.reverse()
            nn_input.append(self.ai_white_board)
        if training:
            temp = generate_17_length(nn_input, 9)
            nn_input = temp.tolist()
        return nn_input

    def get_probabilities_for_child(self, policy_output, chosen_bnode: BoardNode) -> float:
        '''Gets the probabilities of choosing a node from the policy_output variable (array of length 82).'''
        if chosen_bnode == "Pass":
            return policy_output[0][81]
        row, col = chosen_bnode.row, chosen_bnode.col
        policy_idx = row * 9 + col
        return policy_output[0][policy_idx]
