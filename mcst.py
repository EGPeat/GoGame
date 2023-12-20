import random
import copy
import math
from typing import Tuple, List, Set, Union, Optional, Type, Literal
from scoringboard import BoardNode, BoardString
import config as cf
from player import Player
# The deep copying might be a problem, so i should optimize it later on.


class MCSTNode:
    def __init__(self, board: List[List[BoardNode]], board_list=None, turn_person: Tuple[Player, Player],
                 inner: BoardString, outer: BoardString, killed_last: Union[Set[None], Set[BoardNode]] = set(),
                 placement_location=((-1, -1), -1, -1), parent: Union[None, Type['MCSTNode']] = None) -> None:
        from scoringboard import BoardNode
        self.placement_choice = placement_location[0]
        self.choice_info = placement_location
        self.board: List[List[BoardNode]] = board   # change this to be a different representation
        if board_list:
            self.load_board_string(board_list)
        self.parent: Union[None, Type['MCSTNode']] = parent
        self.children: List[MCSTNode] = []
        self.move_choices = dict()
        self.visits: int = 0
        self.wins: int = 0
        self.inner = inner # load it from a string/list of idx, 
        self.outer = outer
        self.killed_last_turn = killed_last
        self.visit_kill: Set[BoardNode] = set()
        self.whose_turn = turn_person[0]
        self.not_whose_turn = turn_person[1]
        if self.whose_turn.unicode == cf.unicode_black:
            self.player_black = self.whose_turn
            self.player_white = self.not_whose_turn
        else:
            self.player_black = self.not_whose_turn
            self.player_white = self.whose_turn

    def switch_player(self) -> None:
        if self.whose_turn == self.player_black:
            self.whose_turn = self.player_white
            self.not_whose_turn = self.player_black
        else:
            self.whose_turn = self.player_black
            self.not_whose_turn = self.player_white

    def print_board(self):
        for xidx in range(len(self.board)):
            tempstr = ''
            for yidx in range(len(self.board)):
                if self.board[yidx][xidx].stone_here_color == cf.unicode_none:
                    tempstr += "0"
                elif self.board[yidx][xidx].stone_here_color == cf.unicode_black:
                    tempstr += '1'
                else:
                    tempstr += '2'
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

    def load_board_string(self, board_list):
        for xidx in len(board_list):
            for yidx in len(board_list):
                if board_list[yidx][xidx] == "0":
                    self.board[yidx][xidx].stone_here_color = cf.unicode_none
                elif board_list[yidx][xidx] == "1":
                    self.board[yidx][xidx].stone_here_color = cf.unicode_black
                elif board_list[yidx][xidx] == "2":
                    self.board[yidx][xidx].stone_here_color = cf.unicode_white



class CollectionOfMCST:  # Unsure how to typehint init line
    def __init__(self, board: List[List[BoardNode]], black_outer: List[BoardString], black_inner: List[BoardString],
                 white_outer: List[BoardString], white_inner: List[BoardString],
                 iterations: int, max_sim_depth: int, players: Tuple[Player, Player]) -> None:
        self.black_MCSTS_tuple_list = list()
        self.black_MCSTS: List[MCST] = list()
        self.white_MCSTS_tuple_list = list() #: Union[List[None], List[List[BoardString, BoardString, MCST]]]
        self.white_MCSTS: List[MCST] = list()

        for idx in range(len(black_outer)):  # must be a more pythonic way
            temp: MCST = MCST(board, black_outer[idx], black_inner[idx], iterations, max_sim_depth, players)
            self.black_MCSTS.append(temp)
            self.black_MCSTS_tuple_list.append([black_outer[idx], black_inner[idx], temp])

        for idx in range(len(white_outer)):  # must be a more pythonic way
            temp = MCST(board, white_outer[idx], white_inner[idx], iterations, max_sim_depth, players)
            self.white_MCSTS.append(temp)
            self.white_MCSTS_tuple_list.append([white_outer[idx], white_inner[idx], temp])



        #for idx in range(len(self.black_MCSTS)):
        #    output = self.black_MCSTS[idx].run_mcst()
        #    self.black_MCSTS_tuple_list[idx].append(output)

        for idx in range(len(self.white_MCSTS)):
            output = self.white_MCSTS[idx].run_mcst()
            self.white_MCSTS_tuple_list[idx].append(output)


class MCST:
    def __init__(self, board: List[List[BoardNode]], outer_pieces: BoardString,  # Maybe turn person is an issue?
                 inner_pieces: BoardString, iterations: int, max_sim_depth: int, turn_person: Tuple[Player, Player]) -> None:
        
        self.root: MCSTNode = MCSTNode(board, turn_person, inner_pieces, outer_pieces, placement_location=("Root", -1, -1))
        self.iteration_number: int = iterations
        self.inner_backup: BoardString = inner_pieces
        self.remove_these = None
        self.max_simulation_depth = max_sim_depth

    def run_mcst(self):
        for idx in range(self.iteration_number):
            selected_node = self.select(self.root)
            self.expand(selected_node, idx)
            result = self.simulate(selected_node)
            self.backpropagate(selected_node, result)

        # Choose the best move based on the tree search results
        quit()
        best_move = max(self.root.children, key=lambda child: child.visits)  # !

        best_move = max(self.root.children, key=lambda child: child.visits)
        # change this to be something to do with what to kill
        return best_move

    def backpropagate(self, node, result):
        # Backpropagate the simulation result up the tree
        while node is not None:
            node.visits += 1
            node.wins += result
            node = node.parent

    def select(self, node: MCSTNode): # only selects the child of the root, lol
        # Select a child node based on the UCT (Upper Confidence Bound for Trees) formula
        if not node.children:
            #generate all children#!
            return node

        root_child = self.best_child_finder(node)

        while root_child.children:
            root_child = self.best_child_finder(root_child)
        
        #generate all children
        return root_child


        """exploration_weight = 1.4
        return max(node.children, key=lambda child: (child.wins / max(1, child.visits)) +
                   exploration_weight * (math.sqrt(math.log(node.visits) / max(1, child.visits))))"""
    

    def best_child_finder(self, node: MCSTNode):
        current_best_val = float('-inf')
        current_best_child = None

        for child in node.children:
            child_val = self.get_UCB_score(child)
            if child_val > current_best_val:
                current_best_val = child_val
                current_best_child = child

        return current_best_child

    def get_UCB_score(self, child: MCSTNode):
        exploration_weight = 1.4
        if child.visits == 0:
            return float('inf')
        top_node = child
        if top_node.parent:
            top_node = top_node.parent
        return ((child.wins/child.visits) + exploration_weight * (math.sqrt(math.log(top_node.visits)/child.visits)))

    def test_piece_placement(self, piece: BoardNode, node: MCSTNode) -> bool:
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

    def ko_rule_break(self, piece: BoardNode, node: MCSTNode) -> bool:
        if self.self_death_rule(piece, node, node.whose_turn) > 0:
            return False
        if piece in node.killed_last_turn:
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
        node.killed_last_turn.clear()
        for position in node.visit_kill:
            node.killed_last_turn.add(position)
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
        if truth_value is False:
            piece.stone_here_color = cf.unicode_none
        return truth_value

    def generate_moves(self, node: MCSTNode, debug=False):
        legal_moves: List[Union[BoardNode, Literal["Pass"]]] = ["Pass"]  # potential issue
        if debug:
            print(node.choice_info)
            print(f"hi the len is {len(node.inner.member_set)}")
        for board_node in node.inner.member_set:
            if debug:
                print(board_node.stone_here_color, board_node.col, board_node.row)
            output = self.test_piece_placement(board_node, node)
            if output[0]:
                legal_moves.append(output[1])

        return legal_moves

    def choose_move(self, selected_move: Union[BoardNode, Literal["Pass"]], node: MCSTNode, idx):
        original_board = node.make_board_string()
        if selected_move == "Pass":  # potential trouble, ill see how it pans out though
            #print("Pass")
            if "Pass" not in node.move_choices.keys():
                node.switch_player()
                child_node = MCSTNode(node.board, original_board, (node.whose_turn, node.not_whose_turn),
                                      node.inner, node.outer, node.killed_last_turn,
                                      ("Pass", idx, node.not_whose_turn.color), parent=node)
                node.children.append(child_node)
                node.move_choices["Pass"] = child_node
            return

        location_tuple = (selected_move.row, selected_move.col)

        if f"{location_tuple}" not in node.move_choices:
            self.expand_play_move(location_tuple, node)
            #print(location_tuple)
            print("in choose_move")
            #compare node.inner to what should be expected after the move placement?
            """for xidx in range(len(new_board)):
                tempstr = ''
                for yidx in range(len(new_board)):
                    if new_board[yidx][xidx].stone_here_color == cf.unicode_none:
                        tempstr += "0"
                    elif new_board[yidx][xidx].stone_here_color == cf.unicode_black:
                        tempstr += '1'
                    else:
                        tempstr += '2'
                print(f'{tempstr}')
            print('\n\n')"""



            board_list = node.make_board_string()
            #for board_node in node.inner.member_set:
            #    print(board_node.stone_here_color, board_node.col, board_node.row)
            child_node = MCSTNode(node.board, board_list, (node.whose_turn, node.not_whose_turn),
                                   node.inner, node.outer, node.killed_last_turn, 
                                    ((location_tuple[1], location_tuple[0]), idx, node.not_whose_turn.color), parent=node)
            
            node.load_board_string(original_board)
            """for xidx in range(len(child_node.board)):
                tempstr = ''
                for yidx in range(len(child_node.board)):
                    if child_node.board[yidx][xidx].stone_here_color == cf.unicode_none:
                        tempstr += "0"
                    elif child_node.board[yidx][xidx].stone_here_color == cf.unicode_black:
                        tempstr += '1'
                    else:
                        tempstr += '2'
                print(f'{tempstr}')
            print('\n\n')"""

            #for board_node in child_node.inner.member_set:
            #    print(board_node.stone_here_color, board_node.col, board_node.row)

            node.children.append(child_node)
            node.move_choices[f"{location_tuple}"] = child_node

        return


    def expand_play_move(self, move, node: MCSTNode):
        new_board_piece: BoardNode = node.board[move[0]][move[1]]
        node.killed_last_turn.clear()
        self.kill_stones(new_board_piece, node, testing=False)
        new_board_piece.stone_here_color = node.whose_turn.unicode
        node.switch_player()

    def simulate_play_move(self, piece: Union[BoardNode, Literal['Pass']], node: MCSTNode):
        if piece != "Pass":
            #board_piece: BoardNode = node.board[move[0]][move[1]]
            node.killed_last_turn.clear()
            self.kill_stones(piece, node, testing=False)
            piece.stone_here_color = node.whose_turn.unicode
            node.switch_player()

    def expand(self, node: MCSTNode, idx):
        legal_moves = self.generate_moves(node, True)
        print(len(legal_moves))
        for item in legal_moves:
            print(item)
        selected_move = random.choice(legal_moves)
        print(node.whose_turn.color)
        print(selected_move)
        print("\n\n\n")
        self.choose_move(selected_move, node, idx)


    def is_game_over(self, node: MCSTNode):
        # Check if there are legal moves for both players aside from passing
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
        current_inner = copy.deepcopy(node.inner)
        current_board = copy.deepcopy(node.board)
        backup_whose = copy.deepcopy(node.whose_turn)
        backup_not_whose = copy.deepcopy(node.not_whose_turn)
        backup_killed_last = copy.deepcopy(node.killed_last_turn)
        return (current_inner, current_board, backup_whose, backup_not_whose, backup_killed_last)

    def load_backup(self,
                    backup, #Tuple[BoardString, List[List[BoardNode], Player, Player, Union[Set[None], Set[BoardNode]]]]
                    node: MCSTNode) -> None:
        node.inner = backup[0]
        node.board = backup[1]
        node.whose_turn = backup[2]
        node.not_whose_turn = backup[3]
        node.killed_last_turn = backup[4]

    def simulate(self, node: MCSTNode):
        # There has to be a check here regarding passing, as otherwise this will just infinitely pass...
        backup = self.backup_info(node)
        print("started simulating")
        simulation_depth = 0
        #node.print_board()
        while not self.is_game_over(node) and simulation_depth < self.max_simulation_depth:
            legal_moves = self.generate_moves(node)
            if legal_moves:  # ! I'm not sure about this......
                selected_move = random.choice(legal_moves)
                #print(selected_move)
                self.simulate_play_move(selected_move, node)
                simulation_depth += 1
            else:
                #print("else")
                #node.print_board()
                self.load_backup(backup, node)
                break  # No legal moves, end the simulation

        unique_colors = {spot.stone_here_color for spot in node.inner.member_set}
        outer_item = next(iter(node.outer.member_set))
        #for board_node in node.inner.member_set:
        #    print(board_node.stone_here_color, board_node.col, board_node.row)
        if len(unique_colors) <= 2 and outer_item.stone_here_color in unique_colors:
            #print("hi")
            #node.print_board()
            self.load_backup(backup, node)
            print("1")
            #node.print_board()
            print()
            print()
            #for board_node in node.inner.member_set:
            #    print(board_node.stone_here_color, board_node.col, board_node.row)
            print('\n\n\n')
            return 1
        else:
            #print("hi2")
            #node.print_board()
            self.load_backup(backup, node)
            print("0")
            #node.print_board()
            print()
            print()
            #for board_node in node.inner.member_set:
            #    print(board_node.stone_here_color, board_node.col, board_node.row)
            print('\n\n\n')
            return 0
