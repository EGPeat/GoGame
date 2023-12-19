from time import sleep
import pygame
import copy
from player import Player
from goclasses import GoBoard, BoardNode, BoardString
import config as cf
from typing import Tuple, List, Set, Union, Literal, Type
import sys
sys.setrecursionlimit(10000)


class ScoringBoard(GoBoard):
    def __init__(self, parent_obj: Type[GoBoard]) -> None:
        # Not a optimal way of doing this but whatever...
        self.parent = parent_obj
        self.board_size: int = copy.deepcopy(self.parent.board_size)
        self.defaults: bool = copy.deepcopy(self.parent.defaults)
        self.board: List[List[BoardNode]] = copy.deepcopy(self.parent.board)
        self.player_black: Player = copy.deepcopy(self.parent.player_black)
        self.player_white: Player = copy.deepcopy(self.parent.player_white)
        self.whose_turn: Player = copy.deepcopy(self.parent.whose_turn)
        self.not_whose_turn: Player = copy.deepcopy(self.parent.not_whose_turn)
        self.times_passed: int = copy.deepcopy(self.parent.times_passed)
        self.turn_num: int = copy.deepcopy(self.parent.turn_num)
        PPL_Type = List[Union[str, Tuple[str, int, int]]]
        self.position_played_log: PPL_Type = copy.deepcopy(self.parent.position_played_log)
        self.visit_kill: Set[BoardNode] = copy.deepcopy(self.parent.visit_kill)
        self.killed_last_turn: Set[BoardNode] = copy.deepcopy(self.parent.killed_last_turn)
        KL_Type = List[List[Union[Tuple[Tuple[int, int, int], int, int], List[None]]]]
        self.killed_log: KL_Type = copy.deepcopy(self.parent.killed_log)
        self.mode: str = copy.deepcopy(self.parent.mode)
        self.mode_change: bool = copy.deepcopy(self.parent.mode_change)
        self.handicap: Tuple[bool, str, int] = copy.deepcopy(self.parent.handicap)
        self.pygame_board_vals: Tuple[int, float, float] = copy.deepcopy(self.parent.pygame_board_vals)
        self.empty_strings: List[BoardString] = list()
        self.black_strings: List[BoardString] = list()
        self.white_strings: List[BoardString] = list()

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

    def find_dead_stones(self, mixed_str_color: Union[List[None], List[BoardString]],
                         outer_str_color: Union[List[None], List[BoardString]],
                         player: Player, player_strings: List[BoardString], unicode: Tuple[int, int, int]) -> None:
        while self.empty_strings:
            obj: BoardString = self.empty_strings.pop()
            obj_obj: BoardNode = obj.member_set.pop()
            success, original_string = self.find_neighbor_get_string(obj_obj, unicode)
            if success:
                tmp = self.finding_correct_mixed_string(obj_obj, player.unicode, original_string, player_strings)
                if tmp[0]:
                    mixed_str, outer_str = tmp[1], tmp[2]  # You need to modify the above function to get the mixed_str
                    # to return the correct area inside of the outer_str. Just modify a floodfill.
                    mixed_str_color.append(mixed_str)
                    outer_str_color.append(outer_str)
                    # m_str: BoardString = mixed_str
                    # o_str: BoardString = outer_str
                    # self.draw_dead_stones(m_str, o_str)

    def draw_dead_stones(self, m_str: BoardString, o_str: BoardString) -> None:
        for item in m_str.member_set:
            pygame.draw.circle(self.screen, cf.unicode_green, (item.screen_row, item.screen_col),
                               self.pygame_board_vals[2])
        pygame.display.update()
        for item in o_str.member_set:
            pygame.draw.circle(self.screen, cf.unicode_red, (item.screen_row, item.screen_col),
                               self.pygame_board_vals[2])
        pygame.display.update()
        sleep(1.5)
        # sleep(0.2)
        self.refresh_board_pygame()

    def dealing_with_dead_stones(self) -> None:
        self.pieces_into_sets()
        self.making_go_board_strings(self.empty_space_set, cf.unicode_none, False)
        self.making_go_board_strings(self.black_set, cf.unicode_black, False)
        self.making_go_board_strings(self.white_set, cf.unicode_white, False)
        self.empty_strings_backup: List[BoardString] = copy.deepcopy(self.empty_strings)
        self.black_strings_backup: List[BoardString] = copy.deepcopy(self.black_strings)
        self.white_strings_backup: List[BoardString] = copy.deepcopy(self.white_strings)
        self.mixed_string_for_black: Union[List[None], List[BoardString]] = list()
        self.mixed_string_for_white: Union[List[None], List[BoardString]] = list()
        self.outer_string_black: Union[List[None], List[BoardString]] = list()
        self.outer_string_white: Union[List[None], List[BoardString]] = list()
        self.find_dead_stones(self.mixed_string_for_black, self.outer_string_black,
                              self.player_black, self.black_strings, cf.unicode_black)
        self.empty_strings = self.empty_strings_backup
        self.black_strings = self.black_strings_backup
        self.white_strings = self.white_strings_backup

        self.find_dead_stones(self.mixed_string_for_white, self.outer_string_white,
                              self.player_white, self.white_strings, cf.unicode_white)

        from mcst import CollectionOfMCST

        self.remove_safe_strings()

        self.MCST_collection = CollectionOfMCST(copy.deepcopy(self.board), self.outer_string_black, self.mixed_string_for_black,
                                                self.outer_string_white, self.mixed_string_for_white,
                                                1000, 20, (self.whose_turn, self.not_whose_turn))
        # 100k

        for idx in range(len(self.mixed_string_for_black)):
            self.draw_dead_stones(self.mixed_string_for_black[idx], self.outer_string_black[idx])
        for idx in range(len(self.mixed_string_for_white)):
            self.draw_dead_stones(self.mixed_string_for_white[idx], self.outer_string_white[idx])

        print("done")

        print("double done")

    def remove_safe_strings(self):
        for idx in reversed(range(len(self.outer_string_black))):
            removeable = True
            for item in self.mixed_string_for_black[idx].member_set:
                if item.stone_here_color != cf.unicode_none:
                    removeable = False
            if removeable:
                self.mixed_string_for_black.pop(idx)
                self.outer_string_black.pop(idx)

        for idx in reversed(range(len(self.outer_string_white))):
            removeable = True
            for item in self.mixed_string_for_white[idx].member_set:
                if item.stone_here_color != cf.unicode_none:
                    removeable = False
            if removeable:
                self.mixed_string_for_white.pop(idx)
                self.outer_string_white.pop(idx)

    def find_neighbor_get_string(self, piece: BoardNode, color: Tuple[int, int, int],
                                 visited: Union[None, Set[BoardNode]] = None) -> Union[
                                     Tuple[Literal[True], BoardString], Tuple[Literal[False], Literal[-1]]]:
        if visited is None:
            visited = set()
        visited.add(piece)
        neighboring_piece: Set[BoardNode] = piece.connections
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

    def find_neighbor_get_string_helper(self, piece: BoardNode, neighbor: BoardNode,
                                        second_color: Tuple[int, int, int], string_choice: List[BoardString]) -> Union[
            Tuple[Literal[True], BoardString], Tuple[Literal[False], Literal[-1]]]:
        if piece.stone_here_color == second_color and second_color == cf.unicode_white:
            second_color = cf.unicode_none
        piece_flood = self.flood_fill_two_colors(piece, second_color)
        # Why is it two color floodfill? Might cause the issue found in the 9x9 board.
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
                )  # Unsure if it should be >= or just >. same for <= and <
            ):
                return True, item
        return (False, -1)

    def counting_territory(self) -> None:  # something somewhere makes row and col switch...
        self.pieces_into_sets()
        self.making_go_board_strings(self.empty_space_set, cf.unicode_none, True)

    def mixed_string_set_removal(self, connections_set: Set[BoardNode], color: Tuple[int, int, int]) -> None:
        while connections_set:
            piece = connections_set.pop()
            piece_color = piece.stone_here_color
            piece_string = self.flood_fill(piece)
            piece_string_obj = BoardString(color, piece_string[0])
            self.mixed_string_set_removal_loop_remove(piece_string_obj, piece_color, cf.unicode_none, self.empty_strings)
            self.mixed_string_set_removal_loop_remove(piece_string_obj, piece_color, cf.unicode_white, self.white_strings)
            self.mixed_string_set_removal_loop_remove(piece_string_obj, piece_color, cf.unicode_black, self.black_strings)

    def mixed_string_set_removal_loop_remove(self, p_string: BoardString, p_color: Tuple[int, int, int],
                                             comp_color: Tuple[int, int, int], enemy_strings: List[BoardString]) -> None:
        if p_color == comp_color:
            for obj in enemy_strings:
                if obj.list_idx == p_string.list_idx:
                    enemy_strings.remove(obj)

    def finding_correct_mixed_string(self, piece: BoardNode, color: Tuple[int, int, int],
                                     original_string: BoardString, list_strings: List[BoardString]) -> \
            Union[Tuple[Literal[False], Literal[-1]], Tuple[Literal[True], BoardString, BoardString]]:

        connections, con_str, discon_str = self.making_mixed_strings(piece, color, original_string, list_strings)
        # If you change the or in the following two checks, it will generate larger areas to test
        if con_str.xmin < discon_str.xmin or con_str.xmax > discon_str.xmax:
            return (False, -1)
        elif con_str.ymin < discon_str.ymin or con_str.ymax > discon_str.ymax:
            return (False, -1)
        else:
            base_piece = con_str.member_set.pop()
            con_str_temp = self.flood_fill_with_outer(base_piece, discon_str)
            con_str_full = BoardString("Internal Area", con_str_temp[0])
            self.mixed_string_set_removal(copy.deepcopy(con_str_temp[0]), color)
            # return (True, con_str, discon_str)
            return (True, con_str_full, discon_str)

    def making_mixed_strings(self, piece: BoardNode, color: Tuple[int, int, int],
                             original_string: BoardString, list_strings: List[BoardString]) -> \
            Tuple[Set[BoardNode], BoardString, BoardString]:
        connections, disconnected_temp, outer_temp = self.generating_mixed_strings(piece, color, original_string, list_strings)
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
        return connections, con_str, discon_str

    def generating_mixed_strings(self, piece: BoardNode, color: Tuple[int, int, int], og_str: BoardString,
                                 str_list: List[BoardString], conn_piece: Union[None, Set[BoardNode]] = None,
                                 outer_pieces: Union[None, Set[BoardNode]] = None,
                                 temp_outer: Union[None, Set[BoardNode]] = None) -> Tuple[
            Set[BoardNode], Set[BoardNode], Set[BoardNode]]:

        if conn_piece is None:
            conn_piece: Union[Set[None], Set[BoardNode]] = set()
        if outer_pieces is None:
            outer_pieces = og_str.member_set
        if temp_outer is None:
            temp_outer: Union[Set[None], Set[BoardNode]] = set()
        conn_piece.add(piece)
        neighboring_pieces = piece.connections
        for neighbor in neighboring_pieces:
            if neighbor.stone_here_color != color and neighbor not in conn_piece:
                self.generating_mixed_strings(neighbor, color, og_str, str_list, conn_piece, outer_pieces, temp_outer)
            elif neighbor.stone_here_color == color and neighbor not in outer_pieces and neighbor not in temp_outer:
                truth, item_member_set = self.mixed_string_logic(piece, color, conn_piece, str_list, neighbor)
                if truth:
                    temp_outer.update(item_member_set)
        return conn_piece, outer_pieces, temp_outer

    def mixed_string_logic(self, piece: BoardNode, color: Tuple[int, int, int], conn_piece: Set[BoardNode],
                           str_list: List[BoardString], neighbor: BoardNode) -> \
            Union[Tuple[Literal[False], Set[None]], Tuple[Literal[True], Set[BoardNode]]]:

        diagonals = self.diagonals_setup(piece)
        for diagonal in diagonals:
            if diagonal.stone_here_color == color and diagonal not in conn_piece:
                for friend in diagonal.connections:
                    if friend in conn_piece:
                        for item in str_list.copy():
                            if (neighbor.col, neighbor.row) in item.list_idx:
                                return (True, item.member_set)
        return (False, set())

    def making_go_board_strings(self, piece_set: Set[BoardNode],
                                piece_type: Tuple[int, int, int], final: bool) -> None:

        list_of_piece_sets: Union[List[None], List[Set[BoardNode]]] = list()
        while piece_set:
            piece = piece_set.pop()
            string = self.making_go_board_strings_helper(piece)
            list_of_piece_sets.append(string)
            piece_set -= string
        for item in list_of_piece_sets:
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
                self.assigns_territory(sets)

    def diagonals_setup(self, piece: BoardNode) -> Set[BoardNode]:
        diagonal_change = [[1, 1], [-1, -1], [1, -1], [-1, 1]]
        diagonals = set()
        for item in diagonal_change:
            new_row, new_col = piece.row + item[0], piece.col + item[1]
            if new_row >= 0 and new_row < self.board_size and new_col >= 0 and new_col < self.board_size:
                diagonals.add(self.board[new_row][new_col])
        return diagonals

    def making_go_board_strings_helper(self, piece: BoardNode,
                                       connected_pieces: Union[None, Set[BoardNode]] = None) -> Set[BoardNode]:
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

    def assigns_territory(self, sets: Tuple[Set[BoardNode], Set[BoardNode]]) -> None:
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
                player = self.player_white
            elif white_pieces == 0:
                player = self.player_black
            player.territory += len(pieces_string)
        else:
            self.player_black.territory += len(pieces_string) * 0.5
            self.player_white.territory += len(pieces_string) * 0.5
        return

    @staticmethod
    def flood_fill(piece: BoardNode,
                   connected_pieces: Union[None, Tuple[Set[BoardNode], Set[BoardNode]]] = None) -> Union[
            None, Tuple[Set[BoardNode], Set[BoardNode]]]:

        if connected_pieces is None:
            connected_pieces = (set(), set())  # (Same color nodes, seen already nodes)
        connected_pieces[0].add(piece)
        neighboring_pieces = piece.connections
        for neighbor in neighboring_pieces:
            if neighbor.stone_here_color == piece.stone_here_color and neighbor not in connected_pieces[0]:
                ScoringBoard.flood_fill(neighbor, connected_pieces)  # Might be issue
            elif neighbor not in connected_pieces[1]:
                connected_pieces[1].add(neighbor)
        return connected_pieces

    def flood_fill_two_colors(self, piece: BoardNode, second_color: Tuple[int, int, int],
                              connected_pieces: Union[None, Tuple[Set[BoardNode], Set[BoardNode]]] = None) -> Union[
                                  None, Tuple[Set[BoardNode], Set[BoardNode]]]:

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

    def flood_fill_with_outer(self, piece: BoardNode, outer_pieces: BoardString,
                              connected_pieces: Union[None, Tuple[Set[BoardNode], Set[BoardNode]]] = None) -> Union[
                                  None, Tuple[Set[BoardNode], Set[BoardNode]]]:
        if connected_pieces is None:
            connected_pieces = (set(), set())
        connected_pieces[0].add(piece)
        neighboring_pieces = piece.connections
        for neighbor in neighboring_pieces:
            if (neighbor.col, neighbor.row) not in outer_pieces.list_idx and neighbor not in connected_pieces[0]:
                self.flood_fill_with_outer(neighbor, outer_pieces, connected_pieces)
            else:
                connected_pieces[1].add(neighbor)
                pass
        return connected_pieces
