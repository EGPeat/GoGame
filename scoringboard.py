from time import sleep
import pygame
import copy
from player import Player
from goclasses import GoBoard, BoardNode, BoardString
import config as cf
from typing import Tuple, Optional, List, Set, Union, Literal


class ScoringBoard(GoBoard):
    def __init__(self, parent_obj):
        # Not a optimal way of doing this but whatever...
        self.parent = parent_obj  #Typehint
        self.board_size: int = copy.deepcopy(self.parent.board_size)
        self.defaults: bool = copy.deepcopy(self.parent.defaults)
        self.board: List[List[BoardNode]] = copy.deepcopy(self.parent.board)
        self.player_black: Player = copy.deepcopy(self.parent.player_black)
        self.player_white: Player = copy.deepcopy(self.parent.player_white)
        self.whose_turn: Player = copy.deepcopy(self.parent.whose_turn)
        self.not_whose_turn: Player = copy.deepcopy(self.parent.not_whose_turn)
        self.times_passed: int = copy.deepcopy(self.parent.times_passed)
        self.turn_num: int = copy.deepcopy(self.parent.turn_num)
        self.position_played_log = copy.deepcopy(self.parent.position_played_log)  #Typehint
        self.visit_kill = copy.deepcopy(self.parent.visit_kill)  #Typehint
        self.killed_last_turn = copy.deepcopy(self.parent.killed_last_turn)  #Typehint
        self.killed_log = copy.deepcopy(self.parent.killed_log)  #Typehint
        self.mode: str = copy.deepcopy(self.parent.mode)
        self.mode_change: bool = copy.deepcopy(self.parent.mode_change)
        self.handicap: Tuple[bool, str, int] = copy.deepcopy(self.parent.handicap)
        self.pygame_board_vals: Tuple[int, float, float] = copy.deepcopy(self.parent.pygame_board_vals)
        self.empty_strings = list()  #Typehint
        self.black_strings = list()  #Typehint
        self.white_strings = list()  #Typehint

    def pieces_into_sets(self) -> None:
        self.empty_space_set: Set[BoardNode] = set()
        self.black_set: Set[BoardNode] = set()
        self.white_set: Set[BoardNode] = set()
        for xidx in range(self.board_size):  # This puts all node spots into 3 sets
            for yidx in range(self.board_size):
                temp_node: BoardNode = self.board[xidx][yidx]
                if temp_node.stone_here_color == cf.unicode_white:
                    self.white_set.add(temp_node)
                elif temp_node.stone_here_color == cf.unicode_black:
                    self.black_set.add(temp_node)
                else:
                    self.empty_space_set.add(temp_node)

    def find_dead_stones(self, mixed_str_color, outer_str_color, player, player_strings, unicode) -> None:  #Typehint
        while self.empty_strings:
            obj: BoardString = self.empty_strings.pop()
            obj_obj: BoardNode = obj.member_set.pop()
            success, original_string = self.find_neighbor_get_string(obj_obj, unicode)
            if not success:
                raise RecursionError
            tmp = self.making_mixed_string(obj_obj, player.unicode, original_string, player_strings)
            if tmp[0]:
                mixed_str, outer_str = tmp[1], tmp[2]
                mixed_str_color.append(mixed_str)
                outer_str_color.append(outer_str)
                m_str = mixed_str
                o_str = outer_str
                self.draw_dead_stones(m_str, o_str)

    def draw_dead_stones(self, m_str, o_str):  #Typehint
        for item in m_str.member_set:
            pygame.draw.circle(self.screen, cf.unicode_green, (item.screen_row, item.screen_col),
                               self.pygame_board_vals[2])
        pygame.display.update()
        for item in o_str.member_set:
            pygame.draw.circle(self.screen, cf.unicode_red, (item.screen_row, item.screen_col),
                               self.pygame_board_vals[2])
        pygame.display.update()
        sleep(1.5)
        self.refresh_board_pygame()

    def dealing_with_dead_stones(self):  #Typehint
        self.pieces_into_sets()
        self.making_go_board_strings(self.empty_space_set, cf.unicode_none, False)
        self.making_go_board_strings(self.black_set, cf.unicode_black, False)
        self.making_go_board_strings(self.white_set, cf.unicode_white, False)
        self.empty_strings_backup = copy.deepcopy(self.empty_strings)
        self.black_strings_backup = copy.deepcopy(self.black_strings)
        self.white_strings_backup = copy.deepcopy(self.white_strings)
        self.mixed_string_for_black = list()
        self.mixed_string_for_white = list()
        self.outer_string_black = list()
        self.outer_string_white = list()
        self.find_dead_stones(self.mixed_string_for_black, self.outer_string_black,
                              self.player_black, self.black_strings, cf.unicode_black)
        self.empty_strings = self.empty_strings_backup
        self.black_strings = self.black_strings_backup
        self.white_strings = self.white_strings_backup
        self.find_dead_stones(self.mixed_string_for_white, self.outer_string_white,
                              self.player_white, self.white_strings, cf.unicode_white)

    # I should refactor this, but i'm afraid of how it might break.
    def find_neighbor_get_string(self, piece, color, visited=None):  #Typehint
        if visited is None:
            visited = set()
        visited.add(piece)
        neighboring_piece = piece.connections
        recursive_result = (False, -1)

        for neighbor in neighboring_piece:
            neighbor_color = neighbor.stone_here_color
            if neighbor not in visited and neighbor_color == color and color == cf.unicode_black:
                recursive_result = self.find_neighbor_get_string_helper(piece, neighbor, cf.unicode_white, self.black_strings)
                if recursive_result[0]:
                    break

            elif neighbor not in visited and neighbor_color == color and color == cf.unicode_white:
                recursive_result = self.find_neighbor_get_string_helper(piece, neighbor, cf.unicode_black, self.white_strings)
                if recursive_result[0]:
                    break
            elif neighbor not in visited:
                recursive_result = self.find_neighbor_get_string(neighbor, color, visited.copy())
                if recursive_result[0]:
                    break
        return recursive_result

    def find_neighbor_get_string_helper(self, piece, neighbor, second_color, string_choice):  #Typehint
        if piece.stone_here_color == second_color and second_color == cf.unicode_white:
            second_color = cf.unicode_none
        piece_flood = self.flood_fill_two_colors(piece, second_color)
        piece_string = BoardString("Empty", piece_flood[0])
        for item in string_choice:
            if (
                (neighbor.col, neighbor.row) in item.list_idx
                and len(item.list_idx) > 1
                and (
                    item.xmax > piece_string.xmax
                    or item.xmin < piece_string.xmin
                    or item.ymax > piece_string.ymax
                    or item.ymin < piece_string.ymin
                )
            ):
                return True, item
        return (False, -1)

    def counting_territory(self) -> None:  #something somewhere makes row and col switch...
        self.pieces_into_sets()
        self.making_go_board_strings(self.empty_space_set, cf.unicode_none, True)

    def mixed_string_set_removal(self, connections_set, color):  #Typehint
        while connections_set:
            piece = connections_set.pop()
            piece_color = piece.stone_here_color
            piece_string = self.flood_fill(piece)
            piece_string_obj = BoardString(color, piece_string[0])
            self.mixed_string_set_removal_loop_remove(piece_string_obj, piece_color, cf.unicode_none, self.empty_strings)
            self.mixed_string_set_removal_loop_remove(piece_string_obj, piece_color, cf.unicode_white, self.white_strings)
            self.mixed_string_set_removal_loop_remove(piece_string_obj, piece_color, cf.unicode_black, self.black_strings)
            # No wrong color in set checker...

    def mixed_string_set_removal_loop_remove(self, p_string, p_color, comp_color, enemy_strings) -> None:  #Typehint
        if p_color == comp_color:
            for obj in enemy_strings:
                if obj.list_idx == p_string.list_idx:
                    enemy_strings.remove(obj)

    # I should refactor this, but i'm afraid of how it might break.
    def making_mixed_string(self, piece, color, original_string, strings_set) -> \
            tuple[Literal[False], Literal[-1]] | tuple[Literal[True], BoardString, BoardString]:  #Typehint
        connections, disconnected_temp, outer_temp = self.making_mixed_string_helper(piece, color, original_string, strings_set)
        if len(outer_temp) > 1:
            ot_str = BoardString("Testing", outer_temp)
        temp_str = BoardString("Empty and Enemy", connections)
        if len(outer_temp) > 1:
            if temp_str.xmin > ot_str.xmin or temp_str.xmax < ot_str.xmax or \
               temp_str.ymin > ot_str.ymin or temp_str.ymax < ot_str.ymax:
                disconnected_temp.update(outer_temp)
            else:
                connections.update(outer_temp)
        con_str = BoardString("Empty and Enemy", connections)
        discon_str = BoardString("Disconnected Outer String", disconnected_temp)
        if con_str.xmin < discon_str.xmin or con_str.xmax > discon_str.xmax:
            return (False, -1)
        elif con_str.ymin < discon_str.ymin or con_str.ymax > discon_str.ymax:
            return (False, -1)
        else:
            self.mixed_string_set_removal(copy.deepcopy(connections), color)
            return (True, con_str, discon_str)

    # I should refactor this, but i'm afraid of how it might break.
    def making_mixed_string_helper(self, piece, color, og_str, str_set,
                                   conn_piece=None, outer_pieces=None, temp_outer=None): #Typehint
        if conn_piece is None:
            conn_piece = set()
        if outer_pieces is None:
            outer_pieces = og_str.member_set
        if temp_outer is None:
            temp_outer = set()
        conn_piece.add(piece)
        neighboring_pieces = piece.connections
        for neighbor in neighboring_pieces:
            if neighbor.stone_here_color != color and neighbor not in conn_piece:
                self.making_mixed_string_helper(neighbor, color, og_str, str_set, conn_piece, outer_pieces, temp_outer)
            elif neighbor.stone_here_color == color:
                if neighbor not in outer_pieces and neighbor not in temp_outer:
                    diagonals = self.diagonals_setup(piece)
                    for diagonal in diagonals:
                        if diagonal.stone_here_color == color and diagonal not in conn_piece:
                            for friend in diagonal.connections:
                                if friend in conn_piece:
                                    for item in str_set.copy():
                                        if (neighbor.col, neighbor.row) in item.list_idx:
                                            temp_outer.update(item.member_set)
        return conn_piece, outer_pieces, temp_outer

    def making_go_board_strings(self, piece_set, piece_type, final):  #Typehint
        list_of_piece_strings = list()
        while piece_set:
            piece = piece_set.pop()
            string = self.making_go_board_strings_helper(piece)
            list_of_piece_strings.append(string)
            piece_set -= string
        for item in list_of_piece_strings:
            string_obj = BoardString(piece_type, item)
            if piece_type == cf.unicode_none:
                self.empty_strings.append(string_obj)
            elif piece_type == cf.unicode_black:
                self.black_strings.append(string_obj)
            elif piece_type == cf.unicode_white:
                self.white_strings.append(string_obj)
            if final:
                item2 = item.pop()
                item.add(item2)
                sets = self.flood_fill(item2)
                self.assignment_logic(sets, piece_type)

    def diagonals_setup(self, piece):  #Typehint
        diagonal_change = [[1, 1], [-1, -1], [1, -1], [-1, 1]]
        diagonals = set()
        for item in diagonal_change:
            new_row, new_col = piece.row + item[0], piece.col + item[1]
            if new_row >= 0 and new_row < self.board_size and new_col >= 0 and new_col < self.board_size:
                diagonals.add(self.board[new_row][new_col])
        return diagonals

    def making_go_board_strings_helper(self, piece, connected_pieces=None):  #Typehint
        if connected_pieces is None:
            connected_pieces = set()
        connected_pieces.add(piece)
        for neighbor in piece.connections:
            if neighbor.stone_here_color == piece.stone_here_color and neighbor not in connected_pieces:
                self.making_go_board_strings_helper(neighbor, connected_pieces)

        diagonals = self.diagonals_setup(piece)

        for diagonal in diagonals:
            if diagonal.stone_here_color == piece.stone_here_color and diagonal not in connected_pieces:
                xdiff = diagonal.row - piece.row
                ydiff = diagonal.col - piece.col
                xopen = self.board[piece.row + xdiff][piece.col].stone_here_color == cf.unicode_none
                yopen = self.board[piece.row][piece.col + ydiff].stone_here_color == cf.unicode_none
                if xopen or yopen:
                    self.making_go_board_strings_helper(diagonal, connected_pieces)
        return connected_pieces

    def assignment_logic(self, sets, empty):  #Typehint
        neighboring = sets[1] - sets[0]
        pieces_string = sets[0]
        black_pieces, white_pieces = 0, 0
        for item in neighboring:
            if item.stone_here_color == cf.unicode_black:
                black_pieces += 1
            else:
                white_pieces += 1
        if black_pieces == 0 or white_pieces == 0:
            if black_pieces == 0:
                player, unicode_choice = self.player_white, cf.unicode_triangle_white
            elif white_pieces == 0:
                player, unicode_choice = self.player_black, cf.unicode_triangle_black
            player.territory += len(pieces_string)
            if empty == "Empty":
                for item in pieces_string:
                    pygame.draw.circle(self.screen, unicode_choice, (item.screen_row, item.screen_col), self.pygame_board_vals[2])
                    self.board[item.row][item.col].stone_here_color = unicode_choice
                pygame.display.update()
        else:
            self.player_black.territory += len(pieces_string) * 0.5
            self.player_white.territory += len(pieces_string) * 0.5
        return

    def flood_fill(self, piece, connected_pieces=None):  #Typehint
        if connected_pieces is None:
            connected_pieces = (set(), set())  # (Same color nodes, seen already nodes)
        connected_pieces[0].add(piece)
        neighboring_pieces = piece.connections
        for neighbor in neighboring_pieces:
            if neighbor.stone_here_color == piece.stone_here_color and neighbor not in connected_pieces[0]:
                self.flood_fill(neighbor, connected_pieces)
            elif neighbor not in connected_pieces[1]:
                connected_pieces[1].add(neighbor)
        return connected_pieces

    def flood_fill_two_colors(self, piece, second_color, connected_pieces=None):  #Typehint
        if connected_pieces is None:
            connected_pieces = (set(), set())
        connected_pieces[0].add(piece)
        neighboring_pieces = piece.connections
        for neighbor in neighboring_pieces:
            if neighbor.stone_here_color == piece.stone_here_color and neighbor not in connected_pieces[0]:
                self.flood_fill_two_colors(neighbor, second_color, connected_pieces)
            elif neighbor.stone_here_color == second_color and neighbor not in connected_pieces[0]:
                self.flood_fill_two_colors(neighbor, second_color, connected_pieces)
            else:
                connected_pieces[1].add(neighbor)
                pass
        return connected_pieces
