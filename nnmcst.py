from goclasses import BoardNode, BoardString
from typing import Tuple, List, Set, Union, Type, Dict, FrozenSet, Literal
from player import Player
from mcst import MCSTNode, MCST
import config as cf
import math
from neuralnet import neural_net_calcuation
import copy
from numpy import argmax
# Need to set the probability for each child node on creation based on the neural net choice
# need a deepcopy thing for the nn so that i dont overwrite my actual game


class NNMCSTNode(MCSTNode):
    def __init__(self, turn_person: Tuple[Player, Player], training_info: List[str], prob,
                 board_list=None, killed_last: Union[Set[None], Set[BoardNode]] = set(),
                 placement_location: Tuple[Union[str, Tuple[int, int]], int, Tuple[int, int, int]] = ((-1, -1), -1, -1),
                 parent: Union[None, Type['NNMCSTNode']] = None) -> None:
        self.placement_choice = placement_location[0]
        self.choice_info = placement_location
        self.board_list: List[str] = board_list
        self.parent: Union[None, Type['NNMCSTNode']] = parent
        self.children: List[NNMCSTNode] = []
        self.move_choices: Dict[str, BoardNode] = dict()
        self.wins: int = 0  # Deprecate

        self.prior_probability: float = prob
        self.number_times_choosen: int = 0
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
                 iterations: int, turn_person: Tuple[Player, Player]) -> None:
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

    def secondary_init(self) -> None:
        '''Helper function for init.'''
        temp_set: Set[BoardNode] = set()
        for idx_1 in range(9):
            for idx_2 in range(9):
                temp_set.add(self.board[idx_1][idx_2])
        self.board_BoardString = BoardString(cf.unicode_none, temp_set)

    def best_child_finder(self, node: NNMCSTNode) -> NNMCSTNode:
        '''Finds the best child of the given node.'''
        current_best_val = float('-inf')
        current_best_child: NNMCSTNode = None

        for child in node.children:
            child_val = self.get_UCB_score(child)
            if child_val > current_best_val:
                current_best_val = child_val
                current_best_child = child
        return current_best_child

    def get_UCB_score(self, child: NNMCSTNode) -> float:
        '''Calculate the Upper Confidence Bound (UCB) score for a given child node.'''
        explor_weight = 1.4
        t_node = child
        if t_node.parent:
            t_node = t_node.parent
        penalty_term_inner_upper = 0
        for sibling in t_node.children:  # I am not sure if this should include the child being tested or not...
            penalty_term_inner_upper += sibling.number_times_choosen

        penalty_term_inner_upper = math.sqrt(penalty_term_inner_upper)
        penalty_term_inner = penalty_term_inner_upper/(1+child.number_times_choosen)
        penalty_term = explor_weight * child.prior_probability * penalty_term_inner
        ucb_value = child.mean_value_v + penalty_term
        return ucb_value

    def backpropagate(self, node: NNMCSTNode, value_output: int) -> None:
        '''Backpropagates the result of a simulation through the tree.'''
        while node is not None:
            node.number_times_choosen += 1
            node.total_v_children += value_output
            node.mean_value_v = node.total_v_children / node.number_times_choosen
            node = node.parent

    def run_mcst(self) -> Tuple[int, int]:
        """
        Run the Monte Carlo Search Tree (MCST) algorithm.

        Returns:
            bool: True if the internal pieces should be counted as dead, False otherwise.
        """
        for idx in range(self.iteration_number):
            selected_node = self.select(self.root, idx)
            value_output = self.expand(selected_node, idx)
            self.backpropagate(selected_node, value_output)
        best_child_value = float('-inf')
        best_child: NNMCSTNode = None
        for spawn in self.root.children:
            spawn_value = self.get_UCB_score(spawn)
            if spawn_value >= best_child_value:
                best_child = spawn
                best_child_value = spawn_value
        location = (best_child.choice_info[0][1], best_child.choice_info[0][0])  # potential issue again....
        if location[0] != "a":
            location = best_child.choice_info[0][1] * 9 + best_child.choice_info[0][0]
        else:
            location = 81  # Hardcoded values
        output_chances = self.get_choice_info()
        return location, output_chances

    def get_choice_info(self) -> List[float]:
        chance_list: List[float] = [None] * 82
        values_list: List[float] = [None] * 82
        for spawn in self.root.children:
            if spawn.choice_info[0][1] != 'a':
                location = spawn.choice_info[0][1] * 9 + spawn.choice_info[0][0]
            else:
                location = 81  # Hardcoded value
            chance_list[location] = spawn.number_times_choosen / (self.iteration_number)
            values_list[location] = self.get_UCB_score(spawn)
        #for idx in range(len(chance_list)):
        #    print(f"{chance_list[idx]}, {values_list[idx]}")

        return chance_list

    def select(self, node: NNMCSTNode, idx: int) -> NNMCSTNode:
        '''Selects a node for expansion, as well as generates child nodes.'''
        if self.is_winning_state(node):
            return node
        if not node.children:
            self.load_board_string(node)
            legal_moves = self.generate_moves(node)
            _, policy_output = self.child_nn_info(node)
            for move in legal_moves:
                probability = self.get_probabilities_for_child(policy_output, move)
                self.make_child_node(move, node, idx, probability)
            return self.select(node, idx)

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
            self.make_child_node(move, root_child, idx, probability)
        return root_child

    def is_winning_state(self, node: NNMCSTNode) -> bool:
        '''Checks if the current node represents a winning state.'''
        if node.cache_hash[1:] in self.win_cache:
            cache_value = self.win_cache[node.cache_hash[1:]]
            if cache_value[0] == 1:
                return True
            else:
                return False

    def expand(self, node: NNMCSTNode, idx) -> None:
        '''Expand the MCST by choosing a move and creating a child node.'''
        self.load_board_string(node)
        if self.is_winning_state(node):
            return
        value_output, policy_output = self.child_nn_info(node)
        legal_move = False
        selected_move = None
        policy_copy = copy.copy(policy_output)  # overkill? look into np arrays for mutability
        while not legal_move:
            move = argmax(policy_copy)
            if move != 81:
                # policy_copy[0][move] = 0  # Could break af
                policy_copy[0][move] = -2  # Could break af
                board_node = self.board[move // 9][move % 9]
                legal_move = self.test_piece_placement(board_node, node)
                selected_move = board_node
            else:
                print("2")
                selected_move = "Pass"
                legal_move = True
        probability = self.get_probabilities_for_child(policy_output, selected_move)
        self.make_child_node(selected_move, node, idx, probability)
        return value_output

    def generate_moves(self, node: NNMCSTNode, simulate=False, final_test=False) -> List[Union[BoardNode, Literal["Pass"]]]:
        '''
        Generates a list of legal moves for the given node based on the current board state.
        Caches the result for future use.
        '''
        if self.cache_hash in self.cache:
            legal_moves = list(self.cache[self.cache_hash])
            legal_moves += ["Pass"]
            return legal_moves
        legal_moves: List[Union[BoardNode, Literal["Pass"]]] = ["Pass"]
        legal_moves_set: Union[Set[None], Set[BoardNode]] = set()
        for board_node in self.board_BoardString.member_set:
            output = self.test_piece_placement(board_node, node, simulate, final_test)
            if output[0]:
                legal_moves.append(output[1])
                legal_moves_set.add(output[1])
        cache_value = frozenset(legal_moves_set)
        self.cache[self.cache_hash] = cache_value

        return legal_moves

    def make_child_node(self, selected_move: Union[BoardNode, Literal["Pass"]], node: NNMCSTNode, idx, prob) -> None:
        '''Choose a move and expand the MCST with the selected move.'''
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
                                    ((location_tuple[1], location_tuple[0]), idx, node.not_whose_turn.color), parent=node)
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
        nn_input = []
        if node.whose_turn.unicode == cf.unicode_black:
            nn_input = node.ai_training_info_node[-8:]
            nn_input.reverse()
            nn_input.append(self.ai_black_board)
        else:
            nn_input = node.ai_training_info_node[-8:]
            nn_input.reverse()
            nn_input.append(self.ai_white_board)

        value_output, policy_output = neural_net_calcuation(nn_input, 9)  # 9 is hardcoded value, not so good
        return (value_output, policy_output)

    def get_probabilities_for_child(self, policy_output, choosen_bnode: BoardNode):
        # heavily unsure if it should be row first or col first
        if choosen_bnode == "Pass":
            return policy_output[0][81]
        row, col = choosen_bnode.row, choosen_bnode.col
        policy_idx = row * 9 + col
        return policy_output[0][policy_idx]
