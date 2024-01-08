import random
import math
from typing import Tuple, List, Set, Union, Optional, Type, Literal, Dict, FrozenSet
from scoringboard import BoardNode, BoardString
import config as cf
from player import Player


class MCSTNode:
    def __init__(self, turn_person: Tuple[Player, Player],
                 board_list=None, killed_last: Union[Set[None], Set[BoardNode]] = set(),
                 placement_location: Tuple[Union[str, Tuple[int, int]], int, Tuple[int, int, int]] = ((-1, -1), -1, -1),
                 parent: Union[None, Type['MCSTNode']] = None) -> None:
        from scoringboard import BoardNode
        self.placement_choice = placement_location[0]
        self.choice_info = placement_location
        self.board_list: List[str] = board_list
        self.parent: Union[None, Type['MCSTNode']] = parent
        self.children: List[MCSTNode] = []
        self.move_choices: Dict[str, BoardNode] = dict()
        self.visits: int = 0
        self.wins: int = 0
        self.killed_last_turn: Union[Set[None], Set[BoardNode]] = killed_last
        self.child_killed_last: Union[Set[BoardNode], Set[None]] = set()
        self.visit_kill: Set[BoardNode] = set()
        self.whose_turn: Player = turn_person[0]
        self.not_whose_turn: Player = turn_person[1]
        self.mcstnode_init()
        self.cache_hash: str = self.generate_cache()

    def mcstnode_init(self) -> None:
        '''Initialize the MCST nodes player values'''
        if self.whose_turn.unicode == cf.unicode_black:
            self.player_black = self.whose_turn
            self.player_white = self.not_whose_turn
        else:
            self.player_black = self.not_whose_turn
            self.player_white = self.whose_turn

    def switch_player(self) -> None:
        '''Switches which players turn it is.'''
        if self.whose_turn == self.player_black:
            self.whose_turn = self.player_white
            self.not_whose_turn = self.player_black
        else:
            self.whose_turn = self.player_black
            self.not_whose_turn = self.player_white

    def generate_cache(self) -> str:
        '''
        Generate a string representation of the current game board to use for hashing purposes.

        Returns a string representing the board state, where each character represents the color of a stone.
        '1' for black, '2' for white, and '0' for an empty intersection.
        The first character represents the player's turn (1 for black, 2 for white).
        '''
        cache_hash: str = ""
        if self.whose_turn.color == "Black":
            cache_hash += "1"
        elif self.whose_turn.color == "White":
            cache_hash += "2"
        cache_hash += ''.join(self.board_list)
        tuple_list: List[Tuple[int, int]] = list()
        for item in self.killed_last_turn:
            tpl = (item.row, item.col)
            tuple_list.append(tpl)
        sorted_tuple_list = sorted(tuple_list, key=lambda x: (x[0], x[1]))
        for item in sorted_tuple_list:
            cache_hash += str(item[0])
            cache_hash += str(item[1])
        return cache_hash


class CollectionOfMCST:
    def __init__(self, board: List[List[BoardNode]], black_outer: List[BoardString], black_inner: List[BoardString],
                 white_outer: List[BoardString], white_inner: List[BoardString],
                 iterations: int, max_sim_depth: int, players: Tuple[Player, Player]) -> None:
        self.black_MCSTS_tuple_list: List[Tuple[BoardString, BoardString, MCST]] = list()
        self.black_MCSTS: List[MCST] = list()
        self.white_MCSTS_tuple_list: List[Tuple[BoardString, BoardString, MCST]] = list()
        self.white_MCSTS: List[MCST] = list()
        self.black_MCSTS_final: List[Tuple[BoardString, BoardString, MCST, bool]] = list()
        self.white_MCSTS_final: List[Tuple[BoardString, BoardString, MCST, bool]] = list()

        for idx in range(len(black_outer)):
            temp: MCST = MCST(board, black_outer[idx], black_inner[idx], iterations, max_sim_depth, players)
            self.black_MCSTS.append(temp)
            self.black_MCSTS_tuple_list.append([black_outer[idx], black_inner[idx], temp])

        for idx in range(len(white_outer)):
            temp: MCST = MCST(board, white_outer[idx], white_inner[idx], iterations, max_sim_depth, players)
            self.white_MCSTS.append(temp)
            self.white_MCSTS_tuple_list.append([white_outer[idx], white_inner[idx], temp])
        for idx in range(len(self.black_MCSTS)):
            item = self.black_MCSTS_tuple_list[idx]
            # print(item[1])
            output: bool = self.black_MCSTS[idx].run_mcst()
            self.black_MCSTS_final.append((item[0], item[1], item[2], output))
            # print(self.black_MCSTS_final[idx])
            # print('\n\n')
        for idx in range(len(self.white_MCSTS)):
            item = self.white_MCSTS_tuple_list[idx]
            # print(item[1])
            output: bool = self.white_MCSTS[idx].run_mcst()  # If output is true, it means you kill the internal pieces
            self.white_MCSTS_final.append((item[0], item[1], item[2], output))
            # print(self.white_MCSTS_final[idx])
            # print('\n\n')


class MCST:
    def __init__(self, board: List[List[BoardNode]], outer_pieces: BoardString,  # Maybe turn person is an issue?
                 inner_pieces: BoardString, iterations: int, max_sim_depth: int, turn_person: Tuple[Player, Player]) -> None:
        self.board = board
        self.inner = inner_pieces
        self.outer = outer_pieces
        self.cache: Dict[str, FrozenSet[BoardNode]] = {}
        self.win_cache: Dict[str, Tuple[int, int]] = {}
        self.cache_hash: str = None
        self.secondary_init(inner_pieces, outer_pieces, turn_person)
        self.iteration_number: int = iterations
        self.max_simulation_depth = max_sim_depth

    # Potential improvement/cleaning up
    def secondary_init(self, inner_pieces: BoardString, outer_pieces: BoardString, turn_person: Tuple[Player, Player]) -> None:
        '''Helper function for init.'''
        # This is necessary because of earlier deepcopy issues causing it to not refer to the current board
        temp_set: Set[BoardNode] = set()
        for pairing in inner_pieces.list_values:
            temp_set.add(self.board[pairing[1]][pairing[0]])
        self.inner = BoardString(inner_pieces.color, temp_set)
        # This is necessary because of earlier deepcopy issues causing it to not refer to the current board
        temp_set: Set[BoardNode] = set()
        for pairing in outer_pieces.list_values:
            temp_set.add(self.board[pairing[1]][pairing[0]])
        self.outer = BoardString(outer_pieces.color, temp_set)
        board_list_for_root = self.make_board_string()
        self.root: MCSTNode = MCSTNode(turn_person, board_list_for_root, placement_location=("Root", -1, -1))

    def print_board(self) -> None:
        '''Prints the board to the terminal.'''
        for xidx in range(len(self.board)):
            tempstr: str = ''
            for yidx in range(len(self.board)):
                if self.board[yidx][xidx].stone_here_color == cf.unicode_none:
                    tempstr += "\u26D4"
                elif self.board[yidx][xidx].stone_here_color == cf.unicode_black:
                    tempstr += '\u26AB'
                else:
                    tempstr += '\u26AA'
            print(f'{tempstr}')
        print('\n\n')

    def make_board_string(self) -> List[str]:   # Target of optimization
        '''
        Generate a string representation of the current game board.

        Returns a string representing the board state, where each character represents the color of a stone.
        '1' for black, '2' for white, and '0' for an empty intersection.
        The first character represents the player's turn (1 for black, 2 for white).
        '''
        board_string_list: List[str] = list()
        for xidx in range(len(self.board)):
            tempstr: str = ''
            for yidx in range(len(self.board)):
                if self.board[yidx][xidx].stone_here_color == cf.unicode_none:
                    tempstr += "0"
                elif self.board[yidx][xidx].stone_here_color == cf.unicode_black:
                    tempstr += '1'
                else:
                    tempstr += '2'
            board_string_list.append(tempstr)
        return board_string_list

    def load_board_string(self, node: MCSTNode) -> None:
        '''Changes the self.board to represent the hash provided by node.board_list. Also generates a hash'''
        self.reload_board_string(node.board_list)
        node.cache_hash = node.generate_cache()
        self.cache_hash = node.cache_hash

    def reload_board_string(self, board_list: List[str]):
        '''Changes the self.board to represent the hash provided by node.board_list.'''
        for xidx in range(len(board_list)):
            for yidx in range(len(board_list)):
                if board_list[xidx][yidx] == "0":
                    self.board[yidx][xidx].stone_here_color = cf.unicode_none
                elif board_list[xidx][yidx] == "1":
                    self.board[yidx][xidx].stone_here_color = cf.unicode_black
                elif board_list[xidx][yidx] == "2":
                    self.board[yidx][xidx].stone_here_color = cf.unicode_white

    def run_mcst(self) -> bool:
        """
        Run the Monte Carlo Search Tree (MCST) algorithm.

        Returns:
            bool: True if the internal pieces should be counted as dead, False otherwise.
        """
        for idx in range(self.iteration_number):
            selected_node = self.select(self.root, idx)
            self.expand(selected_node, idx)
            result: int = self.simulate(selected_node)
            self.backpropagate(selected_node, result)
        if self.root.wins >= self.iteration_number//2:
            print(f"the total amount was {self.iteration_number} with wins of {self.root.wins}")
            return True  # This means the internal pieces should be counted as dead
        else:
            print(f"the total amount was {self.iteration_number} with wins of {self.root.wins}")
            return False

    def backpropagate(self, node: MCSTNode, result: int) -> None:
        '''Backpropagates the result of a simulation through the tree.'''
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent

    def select(self, node: MCSTNode, idx: int) -> MCSTNode:
        '''Selects a node for expansion, as well as generates child nodes.'''
        if self.is_winning_state(node):
            return node
        if not node.children:
            self.load_board_string(node)
            legal_moves = self.generate_moves(node)
            for move in legal_moves:
                self.choose_move(move, node, idx)
            return node

        root_child = self.best_child_finder(node)
        while root_child.children:
            root_child = self.best_child_finder(root_child)
        self.load_board_string(root_child)
        if self.is_winning_state(root_child):
            return root_child
        legal_moves = self.generate_moves(root_child)
        for move in legal_moves:
            self.choose_move(move, root_child, idx)
        return root_child

    def is_winning_state(self, node: MCSTNode) -> bool:
        '''Checks if the current node represents a winning state.'''
        if node.cache_hash[1:] in self.win_cache:
            cache_value = self.win_cache[node.cache_hash[1:]]
            if cache_value[0] == 1:
                return True
            else:
                return False

    def best_child_finder(self, node: MCSTNode) -> MCSTNode:
        '''Finds the best child of the given node.'''
        # current_best_val = float('-inf')
        current_best_child: MCSTNode = None

        # for child in node.children:
        #    child_val = self.get_UCB_score(child)
        #    if child_val > current_best_val:
        #        current_best_val = child_val
        #        current_best_child = child
        # THIS CHOOSES A RANDOM CHILD.############################
        current_best_child = random.choice(node.children)
        return current_best_child

    def get_UCB_score(self, child: MCSTNode) -> float:
        '''Calculate the Upper Confidence Bound (UCB) score for a given child node.'''
        explor_weight = 1.4
        # if child.visits == 0:
        #    return float('inf')
        t_node = child
        if t_node.parent:
            t_node = t_node.parent
        # return ((child.wins/child.visits) + exploration_weight * (math.sqrt(math.log(top_node.visits)/child.visits)))
        return (child.wins / max(1, child.visits)) + explor_weight * (math.sqrt(math.log(t_node.visits) / max(1, child.visits)))

    def test_piece_placement(self, piece: BoardNode, node: MCSTNode, simulate=False, final_test=False) -> Tuple[bool, BoardNode]:
        '''Tests if placing a piece in that location would break the rules of go.'''
        if (piece.stone_here_color != cf.unicode_none):
            return (False, piece)
        elif (self.ko_rule_break(piece, node, simulate, final_test) is True):
            return (False, piece)
        elif (self.kill_stones(piece, node, testing=True) is True):
            return (True, piece)
        elif (self.self_death_rule(piece, node, node.whose_turn) == 0):
            return (False, piece)
        elif self.fills_eye(piece, node) is True:
            return (False, piece)
        else:
            return (True, piece)

    def fills_eye(self, piece: BoardNode, node: MCSTNode) -> bool:
        '''Check if placing a stone in the given position would fill an eye.'''
        for neighbor in piece.connections:
            if neighbor.stone_here_color != node.whose_turn.unicode:
                return False
        piece_diagonals = self.diagonals_setup(piece)
        for item in piece_diagonals:
            if item.stone_here_color != node.whose_turn.unicode:
                return False
        return True

    def ko_rule_break(self, piece: BoardNode, node: MCSTNode, simulate=False, final_test=False) -> bool:
        '''Checks if placing a piece breaks the ko rule.'''
        if final_test:
            return False
        if self.self_death_rule(piece, node, node.whose_turn) > 0:
            return False
        if piece in node.killed_last_turn and not simulate:
            return True
        if piece in node.child_killed_last and simulate:
            return True
        return False

    def self_death_rule(self, piece: BoardNode, node: MCSTNode, which_player: Player,
                        visited: Optional[Set[BoardNode]] = None) -> int:  # Target of optimization
        '''Uses recursive BFS to find liberties and connected pieces of the same type, returns the number of liberties'''
        if visited is None:
            visited: Set[BoardNode] = set()
        visited.add(piece)
        neighboring_piece: Set[BoardNode] = piece.connections
        liberties: int = 0
        for neighbor in neighboring_piece:
            if neighbor.stone_here_color == cf.unicode_none and neighbor not in visited:
                liberties += 1
            elif neighbor.stone_here_color != which_player.unicode:
                pass
            elif neighbor not in visited:
                liberties += self.self_death_rule(neighbor, node, which_player, visited)
        node.visit_kill = visited
        return liberties

    def remove_stones(self, node: MCSTNode) -> None:
        '''Removes stones marked for removal and updates the player's captured count.'''
        node.child_killed_last.clear()
        for position in node.visit_kill:
            node.child_killed_last.add(position)
            position.stone_here_color = cf.unicode_none

    def kill_stones(self, piece: BoardNode, node: MCSTNode, testing: bool) -> bool:
        '''
        Determines if placing a piece kills opponent's stones and removes them if needed.
        Returns True if placing the piece kills stones, False otherwise.
        '''
        piece.stone_here_color: Tuple[int, int, int] = node.whose_turn.unicode
        neighboring_pieces: Set[BoardNode] = piece.connections
        truth_value: bool = False
        for neighbor in neighboring_pieces:
            if neighbor.stone_here_color == node.not_whose_turn.unicode:
                if (self.self_death_rule(neighbor, node, node.not_whose_turn) == 0):
                    if not testing:
                        self.remove_stones(node)
                    truth_value = True
        if truth_value is False or testing is True:
            piece.stone_here_color = cf.unicode_none
        return truth_value

    def flood_fill_two_colors(self, piece: BoardNode, second_color: Tuple[int, int, int],
                              connected_pieces: Union[None, Tuple[Set[BoardNode], Set[BoardNode]]] = None) -> Union[
                                  None, Tuple[Set[BoardNode], Set[BoardNode]]]:  # Target of optimization
        '''Perform flood fill to identify connected pieces for two colors.'''
        if connected_pieces is None:
            connected_pieces = (set(), set())
        connected_pieces[0].add(piece)
        neighboring_pieces = piece.connections
        for neighbor in neighboring_pieces:
            if neighbor.stone_here_color == cf.unicode_none and neighbor not in connected_pieces[0]:
                self.flood_fill_two_colors(neighbor, second_color, connected_pieces)
            elif neighbor.stone_here_color == second_color and neighbor not in connected_pieces[0]:
                self.flood_fill_two_colors(neighbor, second_color, connected_pieces)
            else:
                connected_pieces[1].add(neighbor)
                pass
        return connected_pieces

    def expand(self, node: MCSTNode, idx) -> None:
        '''Expand the MCST by choosing a move and creating a child node.'''
        self.load_board_string(node)
        legal_moves = self.generate_moves(node)
        selected_move = random.choice(legal_moves)
        if self.is_winning_state(node):
            return
        self.choose_move(selected_move, node, idx)

    def generate_moves(self, node: MCSTNode, simulate=False, final_test=False) -> List[Union[BoardNode, Literal["Pass"]]]:
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
        for board_node in self.inner.member_set:
            output = self.test_piece_placement(board_node, node, simulate, final_test)
            if output[0]:
                legal_moves.append(output[1])
                legal_moves_set.add(output[1])
        cache_value = frozenset(legal_moves_set)
        self.cache[self.cache_hash] = cache_value

        return legal_moves

    def choose_move(self, selected_move: Union[BoardNode, Literal["Pass"]], node: MCSTNode, idx) -> None:
        '''Choose a move and expand the MCST with the selected move.'''
        original_board = self.make_board_string()
        if selected_move == "Pass":
            if "Pass" not in node.move_choices.keys():
                node.switch_player()
                child_node = MCSTNode((node.whose_turn, node.not_whose_turn),
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
            child_node = MCSTNode((node.whose_turn, node.not_whose_turn),
                                  board_list, node.child_killed_last,  # Why does location tuple do [1] and then [0]?
                                  ((location_tuple[1], location_tuple[0]), idx, node.not_whose_turn.color), parent=node)
            self.reload_board_string(original_board)
            node.children.append(child_node)
            node.move_choices[f"{location_tuple}"] = child_node
            node.switch_player()
        return

    def expand_play_move(self, move, node: MCSTNode) -> None:
        '''Expands the MCST by playing the given move on the board.'''
        new_board_piece: BoardNode = self.board[move[0]][move[1]]
        node.child_killed_last.clear()
        self.kill_stones(new_board_piece, node, testing=False)
        new_board_piece.stone_here_color = node.whose_turn.unicode
        node.switch_player()

    def simulate_play_move(self, piece: Union[BoardNode, Literal['Pass']], node: MCSTNode) -> None:
        '''Simulates playing a move on the board and updates the MCST node accordingly.'''
        node.child_killed_last.clear()
        if piece != "Pass":
            self.kill_stones(piece, node, testing=False)
            piece.stone_here_color = node.whose_turn.unicode
        self.switch_player_setup(node)

    def switch_player_setup(self, node: MCSTNode):
        '''Switches the player turn in the MCST and updates the board state accordingly.'''
        node.switch_player()
        node.board_list = self.make_board_string()
        node.cache_hash = node.generate_cache()
        self.cache_hash = node.cache_hash

    def is_game_over(self, node: MCSTNode) -> bool:
        '''Checks if the game is over by examining various game-ending conditions.'''
        if self.cache_hash[1:] in self.win_cache:
            cache_value = self.win_cache[self.cache_hash[1:]]
            if cache_value[0] == 1:
                return True
            else:
                return False

        life_check = self.check_inner_life()
        only_outside_color = self.check_inner_kill()
        if life_check or only_outside_color:
            if life_check:
                self.win_cache[self.cache_hash[1:]] = (1, 0)
            else:
                self.win_cache[self.cache_hash[1:]] = (1, 1)
            return True

        self.switch_player_setup(node)
        p1_legal_moves = self.generate_moves(node, True, True)
        self.switch_player_setup(node)
        p2_legal_moves = self.generate_moves(node, True, True)
        if len(p1_legal_moves) == 1 and len(p2_legal_moves) == 1:
            # No legal moves for both players (aside from passing), so the game is over
            return True
        return False

    def check_inner_kill(self) -> bool:
        '''Checks if all stones in the inner region have the same color.'''
        color = next(iter(self.outer.member_set)).stone_here_color
        for item in self.inner.member_set:
            if item.stone_here_color != color and item.stone_here_color != cf.unicode_none:
                return False
        return True

    def check_inner_life(self) -> bool:
        '''Checks if there is more than one living eye in the inner region.'''
        color = next(iter(self.outer.member_set)).stone_here_color
        eye_list = self.making_eye_list(color)
        living_eyes = 0
        if len(eye_list) == 1:
            return False
        for eye_area in eye_list:
            living_eyes += self.check_eye_life(eye_area, color)
        if living_eyes > 1:
            return True
        else:
            return False

    def making_eye_list(self, color) -> List[Set[BoardNode]]:
        '''Generates a list of eye areas in the inner region for the specified color.'''
        full_eye_set: Set[BoardNode] = set()
        eye_list: List[Set[BoardNode]] = list()
        for item in self.inner.member_set:
            if item.stone_here_color == cf.unicode_none and item not in full_eye_set:
                item_set = self.flood_fill_two_colors(item, color)
                full_eye_set.update(item_set[0])
                eye_list.append(item_set[0])
        return eye_list

    def check_eye_life(self, eye_area: Set[BoardNode], color) -> Literal[1, 0]:
        '''Checks if an eye area is alive for the specified color.'''
        color = self.color_switch(color)
        open_diagonals: int = 0
        for spot in eye_area:
            spot_diagonals = self.diagonals_setup(spot)
            for item in spot_diagonals:
                if open_diagonals > 1:
                    return 0
                if item not in eye_area and item.stone_here_color != color:
                    open_diagonals += 1
        if open_diagonals == 0:
            return 1
        else:
            return 0

    def diagonals_setup(self, piece: BoardNode) -> Set[BoardNode]:
        '''Sets up and returns a set of diagonal neighbors for a given board piece.'''
        board_size = len(self.board)
        diagonal_change = [[1, 1], [-1, -1], [1, -1], [-1, 1]]
        diagonals = set()
        for item in diagonal_change:
            new_row, new_col = piece.row + item[0], piece.col + item[1]
            if new_row >= 0 and new_row < board_size and new_col >= 0 and new_col < board_size:
                diagonals.add(self.board[new_row][new_col])
        return diagonals

    def color_switch(self, original_color) -> Tuple[int, int, int]:
        '''Switches the color from black to white and vice versa.'''
        if original_color == cf.unicode_black:
            return cf.unicode_white
        elif original_color == cf.unicode_white:
            return cf.unicode_black

    def backup_info(self, node: MCSTNode) -> Tuple[List[str], str, str]:
        """
        Backs up essential information from the current MCST node.

        Args:
            node (MCSTNode): The current node in the MCST.

        Returns:
            Tuple[List[str], str, str]: Backup information - board state, current player's color, and cache hash.
        """
        backup_board = self.make_board_string()
        backup_whose = node.whose_turn.color
        backup_cache = node.cache_hash
        return (backup_board, backup_whose, backup_cache)

    def load_backup(self, backup: Tuple[List[str], str, str], node: MCSTNode) -> None:
        '''Loads backup information into the current state of the MCST node.'''
        self.reload_board_string(backup[0])
        node.cache_hash = backup[2]
        if backup[1] == cf.unicode_black:
            node.whose_turn = node.player_black
            node.not_whose_turn = node.player_white
        else:
            node.whose_turn = node.player_white
            node.not_whose_turn = node.player_black
        node.child_killed_last.clear()

    def simulate(self, node: MCSTNode) -> Literal[1, 0]:
        """
        Simulates a game to determine the outcome for the current MCST node.

        Args:
            node: The current node in the MCST.

        Returns:
            Literal[1, 0]: 1 if the current player wins, 0 otherwise.
        """
        if self.cache_hash[1:] in self.win_cache:
            cache_value = self.win_cache[self.cache_hash[1:]]
            if cache_value[0] == 1:
                return cache_value[1]

        backup = self.backup_info(node)
        simulation_depth: int = 0
        while not self.is_game_over(node) and simulation_depth < self.max_simulation_depth:
            legal_moves = self.generate_moves(node, True)
            if legal_moves:
                self.win_cache[self.cache_hash[1:]] = (0, 0)
                selected_move = random.choice(legal_moves)
                self.simulate_play_move(selected_move, node)
                simulation_depth += 1
            else:
                self.load_backup(backup, node)
                break
        if self.cache_hash[1:] in self.win_cache:
            cache_value = self.win_cache[self.cache_hash[1:]]
            if cache_value[0] == 1:
                self.load_backup(backup, node)
                return cache_value[1]
        unique_colors = {spot.stone_here_color for spot in self.inner.member_set}
        outer_item = next(iter(self.outer.member_set))
        if len(unique_colors) <= 2 and outer_item.stone_here_color in unique_colors:
            self.win_cache[self.cache_hash[1:]] = (1, 1)
            self.load_backup(backup, node)
            return 1
        else:
            self.win_cache[self.cache_hash[1:]] = (1, 0)
            self.load_backup(backup, node)
            return 0


"""
For training AI, have each turn a board_hash generated, as well as a text representation of the move played.
Add this to a list or other data structure and then feed to AI.
How to have the AI know when to consider the game done/close to done???
"""
