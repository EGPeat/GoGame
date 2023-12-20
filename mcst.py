import random
import math
from typing import Tuple, List, Set, Union, Optional, Type, Literal
from scoringboard import BoardNode, BoardString
import config as cf
from player import Player


class MCSTNode:
    def __init__(self, turn_person: Tuple[Player, Player],
                 board_list=None, killed_last: Union[Set[None], Set[BoardNode]] = set(),
                 placement_location=((-1, -1), -1, -1), parent: Union[None, Type['MCSTNode']] = None) -> None:
        from scoringboard import BoardNode
        self.placement_choice = placement_location[0]
        self.choice_info = placement_location
        self.board_list = board_list
        self.parent: Union[None, Type['MCSTNode']] = parent
        self.children: List[MCSTNode] = []
        self.move_choices = dict()
        self.visits: int = 0
        self.wins: int = 0
        self.killed_last_turn = killed_last  # Potential issue here wrt contamination
        self.child_killed_last = set()  # Potential issue here wrt contamination
        self.visit_kill: Set[BoardNode] = set()
        self.whose_turn = turn_person[0]
        self.not_whose_turn = turn_person[1]
        if self.whose_turn.unicode == cf.unicode_black:
            self.player_black = self.whose_turn
            self.player_white = self.not_whose_turn
        else:
            self.player_black = self.not_whose_turn
            self.player_white = self.whose_turn
        self.cache_hash = self.generate_cache()

    def switch_player(self) -> None:
        if self.whose_turn == self.player_black:
            self.whose_turn = self.player_white
            self.not_whose_turn = self.player_black
        else:
            self.whose_turn = self.player_black
            self.not_whose_turn = self.player_white

    def generate_cache(self):
        cache_hash = ""
        if self.whose_turn.color == cf.unicode_black:
            cache_hash += "1"
        elif self.whose_turn.color == cf.unicode_white:
            cache_hash += "2"
        cache_hash.join(self.board_list)
        tuple_list = list()
        for item in self.killed_last_turn:  # Unsure if it should be item.row or item.col first
            tpl = (item.row, item.col)
            tuple_list.append(tpl)
        sorted_tuple_list = sorted(tuple_list, key=lambda x: (x[0], x[1]))
        for item in sorted_tuple_list:
            cache_hash += str(item[0])
            cache_hash += str(item[1])
        return cache_hash


class CollectionOfMCST:  # Unsure how to typehint init line
    def __init__(self, board: List[List[BoardNode]], black_outer: List[BoardString], black_inner: List[BoardString],
                 white_outer: List[BoardString], white_inner: List[BoardString],
                 iterations: int, max_sim_depth: int, players: Tuple[Player, Player]) -> None:
        self.black_MCSTS_tuple_list = list()
        self.black_MCSTS: List[MCST] = list()
        self.white_MCSTS_tuple_list = list()
        self.white_MCSTS: List[MCST] = list()

        for idx in range(len(black_outer)):
            temp: MCST = MCST(board, black_outer[idx], black_inner[idx], iterations, max_sim_depth, players)
            self.black_MCSTS.append(temp)
            self.black_MCSTS_tuple_list.append([black_outer[idx], black_inner[idx], temp])

        for idx in range(len(white_outer)):
            temp = MCST(board, white_outer[idx], white_inner[idx], iterations, max_sim_depth, players)
            self.white_MCSTS.append(temp)
            self.white_MCSTS_tuple_list.append([white_outer[idx], white_inner[idx], temp])

        for idx in range(len(self.black_MCSTS)):
            print("black_MCSTS time")
            print(self.black_MCSTS_tuple_list[idx][1])
            output = self.black_MCSTS[idx].run_mcst()
            self.black_MCSTS_tuple_list[idx].append(output)
            print("NOT black_MCSTS time")

        for idx in range(len(self.white_MCSTS)):
            print("white_MCSTS time")
            print(self.white_MCSTS_tuple_list[idx][1])
            output = self.white_MCSTS[idx].run_mcst()
            self.white_MCSTS_tuple_list[idx].append(output)
            print("NOT white_MCSTS time")


class MCST:
    def __init__(self, board: List[List[BoardNode]], outer_pieces: BoardString,  # Maybe turn person is an issue?
                 inner_pieces: BoardString, iterations: int, max_sim_depth: int, turn_person: Tuple[Player, Player]) -> None:
        self.board = board
        self.inner = inner_pieces
        self.outer = outer_pieces
        self.cache = {}
        self.cache_hash = None
        temp_set = set()
        for pairing in inner_pieces.list_values:
            temp_set.add(self.board[pairing[1]][pairing[0]])
        self.inner = BoardString(inner_pieces.color, temp_set)
        temp_set = set()
        for pairing in outer_pieces.list_values:
            temp_set.add(self.board[pairing[1]][pairing[0]])
        self.outer = BoardString(outer_pieces.color, temp_set)
        board_list_for_root = self.make_board_string()

        self.root: MCSTNode = MCSTNode(turn_person, board_list_for_root, placement_location=("Root", -1, -1))
        self.iteration_number: int = iterations
        self.remove_these = None
        self.max_simulation_depth = max_sim_depth

    def print_board(self):
        for xidx in range(len(self.board)):
            tempstr = ''
            for yidx in range(len(self.board)):
                if self.board[yidx][xidx].stone_here_color == cf.unicode_none:
                    tempstr += "\u26D4"
                elif self.board[yidx][xidx].stone_here_color == cf.unicode_black:
                    tempstr += '\u26AB'
                else:
                    tempstr += '\u26AA'
            print(f'{tempstr}')
        print('\n\n')

    def make_board_string(self):
        board_string_list = list()
        for xidx in range(len(self.board)):
            tempstr = ''
            for yidx in range(len(self.board)):
                if self.board[yidx][xidx].stone_here_color == cf.unicode_none:
                    tempstr += "0"
                elif self.board[yidx][xidx].stone_here_color == cf.unicode_black:
                    tempstr += '1'
                else:
                    tempstr += '2'
            board_string_list.append(tempstr)
        return board_string_list

    def load_board_string(self, node: MCSTNode):
        self.reload_board_string(node.board_list)
        self.cache_hash = node.cache_hash

    def reload_board_string(self, board_list):
        for xidx in range(len(board_list)):
            for yidx in range(len(board_list)):
                if board_list[xidx][yidx] == "0":
                    self.board[yidx][xidx].stone_here_color = cf.unicode_none
                elif board_list[xidx][yidx] == "1":
                    self.board[yidx][xidx].stone_here_color = cf.unicode_black
                elif board_list[xidx][yidx] == "2":
                    self.board[yidx][xidx].stone_here_color = cf.unicode_white

    def run_mcst(self):
        for idx in range(self.iteration_number):
            selected_node = self.select(self.root, idx)
            self.expand(selected_node, idx)
            result = self.simulate(selected_node)
            self.backpropagate(selected_node, result)

        if self.root.wins >= self.iteration_number//2:
            print(f"the total amount was {self.iteration_number} with wins of {self.root.wins}")
            return True  # This means the internal pieces should be counted as dead
        else:
            print(f"the total amount was {self.iteration_number} with wins of {self.root.wins}")
            return False

    def backpropagate(self, node, result):
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent

    def select(self, node: MCSTNode, idx):
        # Select a child node based on the UCT (Upper Confidence Bound for Trees) formula
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
        legal_moves = self.generate_moves(root_child)
        for move in legal_moves:
            self.choose_move(move, root_child, idx)
        return root_child

    def best_child_finder(self, node: MCSTNode):
        # current_best_val = float('-inf')
        current_best_child = None

        # for child in node.children:
        #    child_val = self.get_UCB_score(child)
        #    if child_val > current_best_val:
        #        current_best_val = child_val
        #        current_best_child = child
        # THIS CHOOSES A RANDOM CHILD.############################
        current_best_child = random.choice(node.children)
        return current_best_child

    def get_UCB_score(self, child: MCSTNode):
        explor_weight = 1.4
        # if child.visits == 0:
        #    return float('inf')
        t_node = child
        if t_node.parent:
            t_node = t_node.parent
        # return ((child.wins/child.visits) + exploration_weight * (math.sqrt(math.log(top_node.visits)/child.visits)))
        return (child.wins / max(1, child.visits)) + explor_weight * (math.sqrt(math.log(t_node.visits) / max(1, child.visits)))

    def test_piece_placement(self, piece: BoardNode, node: MCSTNode) -> Tuple[bool, BoardNode]:
        if (piece.stone_here_color != cf.unicode_none):
            return (False, piece)
        elif (self.ko_rule_break(piece, node) is True):
            return (False, piece)
        elif (self.kill_stones(piece, node, testing=True) is True):
            return (True, piece)
        elif (self.self_death_rule(piece, node, node.whose_turn) == 0):
            return (False, piece)
        else:
            return (True, piece)

    def ko_rule_break(self, piece: BoardNode, node: MCSTNode, simulate=False) -> bool:
        if self.self_death_rule(piece, node, node.whose_turn) > 0:
            return False
        if piece in node.killed_last_turn and not simulate:
            return True
        if piece in node.child_killed_last and simulate:
            return True
        return False

    def self_death_rule(self, piece: BoardNode, node: MCSTNode, which_player: Player,
                        visited: Optional[Set[BoardNode]] = None) -> int:
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
        node.child_killed_last.clear()
        for position in node.visit_kill:
            node.child_killed_last.add(position)
            node.whose_turn.captured += 1  # is it necessary in this case?
            position.stone_here_color = cf.unicode_none

    def kill_stones(self, piece: BoardNode, node: MCSTNode, testing: bool) -> bool:
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

    def expand(self, node: MCSTNode, idx):
        self.load_board_string(node)
        legal_moves = self.generate_moves(node)
        selected_move = random.choice(legal_moves)
        self.choose_move(selected_move, node, idx)

    def generate_moves(self, node: MCSTNode):
        if self.cache_hash in self.cache:
            legal_moves = list(self.cache[self.cache_hash])
            legal_moves += ["Pass"]
            return legal_moves
        legal_moves: List[Union[BoardNode, Literal["Pass"]]] = ["Pass"]  # potential issue
        legal_moves_set: Union[Set[None], Set[BoardNode]] = set()
        for board_node in self.inner.member_set:
            output = self.test_piece_placement(board_node, node)
            if output[0]:
                legal_moves.append(output[1])
                legal_moves_set.add(output[1])
        cache_value = frozenset(legal_moves_set)
        self.cache[self.cache_hash] = cache_value

        return legal_moves

    def choose_move(self, selected_move: Union[BoardNode, Literal["Pass"]], node: MCSTNode, idx):
        original_board = self.make_board_string()
        if selected_move == "Pass":
            if "Pass" not in node.move_choices.keys():
                node.switch_player()
                child_node = MCSTNode((node.whose_turn, node.not_whose_turn),
                                      original_board, node.child_killed_last,
                                      ("Pass", idx, node.not_whose_turn.color), parent=node)
                node.children.append(child_node)
                node.move_choices["Pass"] = child_node
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
        return

    def expand_play_move(self, move, node: MCSTNode):
        new_board_piece: BoardNode = self.board[move[0]][move[1]]
        node.child_killed_last.clear()
        self.kill_stones(new_board_piece, node, testing=False)
        new_board_piece.stone_here_color = node.whose_turn.unicode
        node.switch_player()

    def simulate_play_move(self, piece: Union[BoardNode, Literal['Pass']], node: MCSTNode):
        node.child_killed_last.clear()
        if piece != "Pass":
            self.kill_stones(piece, node, testing=False)
            piece.stone_here_color = node.whose_turn.unicode
        node.switch_player()
        node.generate_cache()
        self.cache_hash = node.cache_hash

    def is_game_over(self, node: MCSTNode):
        p1_legal_moves = self.generate_moves(node)
        node.switch_player()
        p2_legal_moves = self.generate_moves(node)
        node.switch_player

        if len(p1_legal_moves) == 1 and len(p2_legal_moves) == 1:
            # No legal moves for both players (aside from passing), so the game is over
            return True

        # Game is not over
        return False

    def backup_info(self, node: MCSTNode):
        backup_board = self.make_board_string()
        backup_whose = node.whose_turn.color
        if node.killed_last_turn:  # Unsure if necessary now, test
            backup_killed_last = BoardString("Temp holding", node.killed_last_turn)
        else:
            backup_killed_last = set()
        return (backup_board, backup_whose, backup_killed_last)

    def load_backup(self, backup, node: MCSTNode) -> None:
        self.reload_board_string(backup[0])
        #Potential issue, check if this inherently relies/calls on load_board_string b4

        if backup[1] == cf.unicode_black:
            node.whose_turn = node.player_black
            node.not_whose_turn = node.player_white
        else:
            node.whose_turn = node.player_white
            node.not_whose_turn = node.player_black

        node.killed_last_turn = set()
        if backup[2]:
            for pairing in backup[2].list_values:
                node.killed_last_turn.add(self.board[pairing[1]][pairing[0]])

    def simulate(self, node: MCSTNode):
        # TODO: decide if it should stop two passes in a row, and how
        backup = self.backup_info(node)
        simulation_depth = 0
        while not self.is_game_over(node) and simulation_depth < self.max_simulation_depth:
            # This doesn't fully manage figuring out what is or isn't alive, as a player can place inside
            # on the last move even if it would be dead
            # But this would say that the whole thing should be counted alive in that case, which is wrong. Ask for advice.
            legal_moves = self.generate_moves(node)
            if legal_moves:
                selected_move = random.choice(legal_moves)
                self.simulate_play_move(selected_move, node)
                simulation_depth += 1
            else:
                self.load_backup(backup, node)
                break

        unique_colors = {spot.stone_here_color for spot in self.inner.member_set}
        outer_item = next(iter(self.outer.member_set))
        if len(unique_colors) <= 2 and outer_item.stone_here_color in unique_colors:
            self.load_backup(backup, node)
            return 1
        else:
            self.load_backup(backup, node)
            return 0
