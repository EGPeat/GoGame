from time import sleep
import pygame
import uifunctions as ui
from player import Player
from goclasses import GoBoard, BoardNode, BoardString
import config as cf
from typing import Tuple, List, Set, Union, Literal, Type
from goclasses import diagonals_setup


def making_score_board_object(board: GoBoard):
    '''Creates a ScoringBoard object to handle scoring and dead stones.'''
    import platform  # Required as for some reason the code/window behaves differently between linux and windows
    board.scoring_dead: ScoringBoard = ScoringBoard(board)
    if platform.system() == "Linux":
        board.window.close()
        ui.setup_board_window_pygame(board.scoring_dead)  # Makes a window, but nothing you click will do anything
        ui.refresh_board_pygame(board.scoring_dead)
        winner = board.scoring_dead.dealing_with_dead_stones()
        return winner
    elif platform.system() == "Windows":
        ui.close_window(board)
        ui.setup_board_window_pygame(board.scoring_dead)
        ui.refresh_board_pygame(board.scoring_dead)
        winner = board.scoring_dead.dealing_with_dead_stones()
        return winner


class ScoringBoard(GoBoard):
    def __init__(self, parent_obj: Type[GoBoard]) -> None:
        # Not a optimal way of doing this but whatever...
        self.parent = parent_obj
        self.defaults: bool = self.parent.defaults
        self.board_size: int = self.parent.board_size
        self.board: List[List[BoardNode]] = self.parent.board

        self.init_helper_player_deep()

        # Turn and log attributes
        self.times_passed: int = self.parent.times_passed
        self.turn_num: int = self.parent.turn_num
        PPL_Type = List[Union[str, Tuple[str, int, int]]]
        self.position_played_log: PPL_Type = self.parent.position_played_log
        self.visit_kill: Set[BoardNode] = self.parent.visit_kill
        self.killed_last_turn: Set[BoardNode] = self.parent.killed_last_turn
        KL_Type = List[List[Union[Tuple[Tuple[int, int, int], int, int], List[None]]]]
        self.killed_log: KL_Type = self.parent.killed_log

        # Mode and handicap attributes
        self.mode: str = self.parent.mode
        self.mode_change: bool = self.parent.mode_change
        self.handicap: Tuple[bool, str, int] = self.parent.handicap

        self.pygame_board_vals: Tuple[int, float, float] = self.parent.pygame_board_vals
        self.empty_strings: List[BoardString] = list()
        self.black_strings: List[BoardString] = list()
        self.white_strings: List[BoardString] = list()

    def init_helper_player_deep(self) -> None:
        '''Makes a copy of the variables to do with Players'''
        self.player_black: Player = self.parent.player_black
        self.player_white: Player = self.parent.player_white
        self.whose_turn: Player = self.parent.whose_turn
        self.not_whose_turn: Player = self.parent.not_whose_turn

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

    def make_mixed_and_outer(self, mixed_str_color: Union[List[None], List[BoardString]],
                             outer_str_color: Union[List[None], List[BoardString]],
                             player: Player, player_strings: List[BoardString], unicode: Tuple[int, int, int]) -> None:
        '''This function makes a list of mixed and outer strings to then be used by the MCST.'''
        while self.empty_strings:
            obj: BoardString = self.empty_strings.pop()
            obj_obj: BoardNode = obj.member_set.pop()
            success, original_string = self.find_neighbor_get_string(obj_obj, unicode)
            if success:
                tmp = self.finding_correct_mixed_string(obj_obj, player.unicode, original_string, player_strings)
                if tmp[0]:
                    mixed_str, outer_str = tmp[1], tmp[2]
                    mixed_str_color.append(mixed_str)
                    outer_str_color.append(outer_str)

    def draw_dead_stones(self, m_str: BoardString, o_str: BoardString) -> None:
        '''Draws dead stones on the Pygame board and updates the display.'''
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
        ui.refresh_board_pygame(self)

    def dealing_with_dead_stones(self) -> bool:  # Could easily split up this function into multiple functions
        '''
        Manages the process of dealing with dead stones, including finding and removing them.
        Initializes and uses the MCST collection for scoring.
        Returns the winner after counting territory.
        '''
        import copy
        self.pieces_into_sets()
        self.making_go_board_strings(self.empty_space_set, cf.unicode_none, False)
        self.making_go_board_strings(self.black_set, cf.unicode_black, False)
        self.making_go_board_strings(self.white_set, cf.unicode_white, False)
        self.empty_strings_backup: List[BoardString] = copy.deepcopy(self.empty_strings)  # Change
        self.black_strings_backup: List[BoardString] = copy.deepcopy(self.black_strings)  # Change
        self.white_strings_backup: List[BoardString] = copy.deepcopy(self.white_strings)  # Change
        self.mixed_string_for_black: Union[List[None], List[BoardString]] = list()
        self.mixed_string_for_white: Union[List[None], List[BoardString]] = list()
        self.outer_string_black: Union[List[None], List[BoardString]] = list()
        self.outer_string_white: Union[List[None], List[BoardString]] = list()

        self.make_mixed_and_outer(self.mixed_string_for_black, self.outer_string_black,
                                  self.player_black, self.black_strings, cf.unicode_black)
        self.empty_strings = self.empty_strings_backup
        self.black_strings = self.black_strings_backup
        self.white_strings = self.white_strings_backup

        self.make_mixed_and_outer(self.mixed_string_for_white, self.outer_string_white,
                                  self.player_white, self.white_strings, cf.unicode_white)
        self.remove_safe_strings()
        from mcst import CollectionOfMCST
        self.MCST_collection = CollectionOfMCST(self.board, self.outer_string_black, self.mixed_string_for_black,
                                                self.outer_string_white, self.mixed_string_for_white,
                                                5000, 30, (self.whose_turn, self.not_whose_turn))

        for item in self.MCST_collection.black_MCSTS_final:
            if item[3] is True:
                for node in item[1].member_set:
                    spot = self.board[node.row][node.col]
                    spot.stone_here_color = cf.unicode_none
        for item in self.MCST_collection.white_MCSTS_final:
            if item[3] is True:
                for node in item[1].member_set:
                    spot = self.board[node.row][node.col]
                    spot.stone_here_color = cf.unicode_none
        winner = self.counting_territory()
        return winner

    def remove_safe_strings(self):
        '''
        Removes safe strings (mixed and outer strings) from both black and white players.
        Safe strings are a pair of inner and outer strings, where the inner/mixed string does not contain any pieces.
        '''
        for idx in reversed(range(len(self.outer_string_black))):
            removeable = True
            for item in self.mixed_string_for_black[idx].member_set:
                if item.stone_here_color == cf.unicode_white:
                    removeable = False
            if removeable:
                self.mixed_string_for_black.pop(idx)
                self.outer_string_black.pop(idx)

        for idx in reversed(range(len(self.outer_string_white))):
            removeable = True
            for item in self.mixed_string_for_white[idx].member_set:
                if item.stone_here_color == cf.unicode_black:
                    removeable = False
            if removeable:
                self.mixed_string_for_white.pop(idx)
                self.outer_string_white.pop(idx)

    def find_neighbor_get_string(self, piece: BoardNode, color: Tuple[int, int, int],
                                 visited: Union[None, Set[BoardNode]] = None) -> Union[
                                     Tuple[Literal[True], BoardString], Tuple[Literal[False], Literal[-1]]]:
        '''Finds and returns the board string of the neighboring piece with the specified color.'''
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
                recursive_result = self.find_neighbor_get_string(neighbor, color, visited)  # visited used to be visited.copy()
                # But that caused awful performance. but might have been necessary
                if recursive_result[0]:
                    break
        return recursive_result

    def find_neighbor_get_string_helper(self, piece: BoardNode, neighbor: BoardNode,
                                        second_color: Tuple[int, int, int], string_choice: List[BoardString]) -> Union[
            Tuple[Literal[True], BoardString], Tuple[Literal[False], Literal[-1]]]:
        '''
        Helper function for find_neighbor_get_string.
        Determines if the neighbor's string should be included in the result.
        '''
        if piece.stone_here_color == second_color and second_color == cf.unicode_white:
            second_color = cf.unicode_none
        piece_flood = self.flood_fill_two_colors(piece, second_color)
        # Why is it two color floodfill? Might cause the issue found in the 9x9 board.
        piece_string = BoardString("Empty", piece_flood[0])
        for item in string_choice:
            if (
                (neighbor.col, neighbor.row) in item.list_idx #!
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

    def counting_territory(self) -> Union[None, bool]:  # something somewhere makes row and col switch...
        '''Counts the territory for both players and determines the winner.'''
        self.pieces_into_sets()
        self.making_go_board_strings(self.empty_space_set, cf.unicode_none, True)
        pb = self.player_black
        pw = self.player_white
        pb.black_set_len = len(self.black_set)
        pw.white_set_len = len(self.white_set)
        player_black_score = pb.komi + pb.territory + len(self.black_set)
        player_white_score = pw.komi + pw.territory + len(self.white_set)
        print(f"black has {pb.komi} and {pb.territory} and {len(self.black_set)}")
        difference = player_black_score - player_white_score
        print(f"white has {pw.komi} and {pw.territory} and {len(self.white_set)}, making the difference {difference}")
        if difference > 0:
            return 1  # Might be a more descriptive way to have it say who won, which could be better for training an AI...
        else:
            return -1

    def mixed_string_set_removal(self, connections_set: Set[BoardNode], color: Tuple[int, int, int]) -> None:
        """
        Removes pieces from the specified set of connections and updates the corresponding board strings.

        Args:
            connections_set: The set of connected board pieces to be removed.
            color: The color of the stones to update.

        """
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
        """
        Removes a board string from the specified list of enemy strings if its color matches the comparison color.

        Args:
            p_string: The board string to be checked and removed.
            p_color: The color of the stones in the given board string.
            comp_color: The comparison color for removal.
            enemy_strings: The list of enemy board strings.
        """
        if p_color == comp_color:
            for obj in enemy_strings:
                if obj.list_idx == p_string.list_idx:
                    enemy_strings.remove(obj)

    def finding_correct_mixed_string(self, piece: BoardNode, color: Tuple[int, int, int],
                                     original_string: BoardString, list_strings: List[BoardString]) -> \
            Union[Tuple[Literal[False], Literal[-1]], Tuple[Literal[True], BoardString, BoardString]]:
        """
        Finds the correct mixed strings for a given board piece and color, ensuring proper connectivity.

        Args:
            piece: The board piece for which mixed strings are to be found.
            color: The color of the stones for which mixed strings are considered.
            original_string: The original string to which the board piece belongs.
            list_strings: List of existing board strings.

        Returns:
            Union[Tuple[Literal[False], Literal[-1]], Tuple[Literal[True], BoardString, BoardString]]:
                - (False, -1) if the mixed strings are not correct or connected.
                - (True, con_str_full, discon_str) if the mixed strings are correct and connected.
        """
        con_str, discon_str = self.making_mixed_strings(piece, color, original_string, list_strings)
        # If you change the or in the following two checks, it will generate larger areas to test
        if con_str.xmin < discon_str.xmin or con_str.xmax > discon_str.xmax:
            return (False, -1)
        elif con_str.ymin < discon_str.ymin or con_str.ymax > discon_str.ymax:
            return (False, -1)
        else:
            import copy
            base_piece = con_str.member_set.pop()
            con_str_temp = self.flood_fill_with_outer(base_piece, discon_str)
            con_str_full = BoardString("Internal Area", con_str_temp[0])
            self.mixed_string_set_removal(copy.deepcopy(con_str_temp[0]), color)
            return (True, con_str_full, discon_str)

    def making_mixed_strings(self, piece: BoardNode, color: Tuple[int, int, int],
                             original_string: BoardString, list_strings: List[BoardString]) -> \
            Tuple[BoardString, BoardString]:
        """
        Generate mixed strings by connecting empty spaces and opponent stones.

        Parameters:
            piece The starting piece for generating mixed strings.
            original_string: The original string to which the piece belongs.
            list_strings: List of existing strings on the board.

        Returns a tuple containing connected nodes, connected string, and disconnected outer string.
        """
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
        return con_str, discon_str

    def generating_mixed_strings(self, piece: BoardNode, color: Tuple[int, int, int], og_str: BoardString,
                                 str_list: List[BoardString], conn_piece: Union[None, Set[BoardNode]] = None,
                                 outer_pieces: Union[None, Set[BoardNode]] = None,
                                 temp_outer: Union[None, Set[BoardNode]] = None) -> Tuple[
            Set[BoardNode], Set[BoardNode], Set[BoardNode]]:
        """
        Recursive function to generate mixed strings.

        Parameters:
            piece: The current piece being processed.
            og_str: The original string to which the piece belongs.
            str_list: List of existing strings on the board.
            conn_piece: Set of connected pieces (optional).
            outer_pieces: Set of outer pieces (optional).
            temp_outer: Temporary set for outer pieces (optional).

        Returns a tuple containing connected nodes, outer pieces, and temporary outer pieces.
        """
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
        '''Extremely complicated logic for calculating if a piece should be in the mixed string'''
        diagonals = diagonals_setup(self, piece)
        for diagonal in diagonals:
            if diagonal.stone_here_color == color and diagonal not in conn_piece:
                for friend in diagonal.connections:
                    if friend in conn_piece:
                        for item in str_list.copy():
                            if (neighbor.row, neighbor.col) in item.list_idx:
                                return (True, item.member_set)
        return (False, set())

    def making_go_board_strings(self, piece_set: Set[BoardNode],
                                piece_type: Tuple[int, int, int], final: bool) -> None:
        '''Generate Go board strings based on a set of pieces.'''
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

    def making_go_board_strings_helper(self, piece: BoardNode,
                                       connected_pieces: Union[None, Set[BoardNode]] = None) -> Set[BoardNode]:
        """Helper function to recursively identify connected pieces in a Go board string."""
        if connected_pieces is None:
            connected_pieces = set()
        connected_pieces.add(piece)
        for neighbor in piece.connections:
            if neighbor.stone_here_color == piece.stone_here_color and neighbor not in connected_pieces:
                self.making_go_board_strings_helper(neighbor, connected_pieces)

        diagonals = diagonals_setup(self, piece)

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
        '''Assign territory based on neighboring pieces. Uses chinese rules.'''
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
        '''Perform flood fill to identify connected pieces.'''
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
        '''Perform flood fill to identify connected pieces for two colors.'''
        if connected_pieces is None:
            connected_pieces = (set(), set())
        connected_pieces[0].add(piece)
        neighboring_pieces = piece.connections
        for neighbor in neighboring_pieces:  # piece.stone_here_color might be for below
            if neighbor.stone_here_color == cf.unicode_none and neighbor not in connected_pieces[0]:
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
        '''Perform flood fill to identify connected pieces considering outer pieces.
        Set 1 is the set of objects of the same color, Set 2 is the outside objects
        '''
        if connected_pieces is None:
            connected_pieces = (set(), set())
        connected_pieces[0].add(piece)
        neighboring_pieces = piece.connections
        for neighbor in neighboring_pieces:
            if (neighbor.row, neighbor.col) not in outer_pieces.list_idx and neighbor not in connected_pieces[0]:#!
                self.flood_fill_with_outer(neighbor, outer_pieces, connected_pieces)
            else:
                connected_pieces[1].add(neighbor)
                pass
        return connected_pieces
