import uifunctions as ui
import PySimpleGUI as sg
import math
import pygame
import sys
from player import Player
from handicap import Handicap
import config as cf
from typing import Tuple, Optional, List, Set, Union
sys.setrecursionlimit(10000)


class BoardNode():
    def __init__(self, row_value: Optional[int] = None, col_value: Optional[int] = None):
        self.row: int = row_value
        self.col: int = col_value
        self.screen_row: float = None
        self.screen_col: float = None
        self.stone_here_color: Tuple[int, int, int] = cf.unicode_none
        self.connections: Set[BoardNode] = set()

    def __str__(self) -> str:
        return (f"This is a BoardNode with coordinates of ({self.row},{self.col}) and a stone of {self.stone_here_color}")


class BoardString():
    def __init__(self, color: str, member_set: Set[BoardNode]) -> None:
        '''
        Initialize a BoardString object.

        Parameters:
            color (str): Color associated with the BoardString.
            member_set (Set[BoardNode]): Set of BoardNode objects representing the board state.

        Attributes:
            color (str): Color associated with the BoardString.
            member_set (Set[BoardNode]): Set of BoardNode objects representing the board state.
            list_idx: List of sorted indices (col, row) of member_set.
            list_values: List of sorted values (col, row, stone_color) of member_set.
            xmax, xmin, ymax, ymin: maximum and minimum values for the rows and columns.
        '''
        self.color: str = color
        self.member_set: Set[BoardNode] = member_set
        self.list_idx: List[Tuple[int, int]] = self.make_list_idx(member_set)
        self.list_values: List[Tuple[int, int, Tuple[int, int, int]]] = self.make_list_values(member_set)

    def __str__(self) -> str:
        return (f"this is a board string of color {self.color} and with len of {len(self.list_idx)} and values {self.list_idx}\
             and a xmax and xmin of {self.xmax, self.xmin}, and a ymax and ymin of {self.ymax, self.ymin}")

    def make_list_idx(self, set_objects: Set[BoardNode]) -> List[Tuple[int, int]]:
        '''
        Generate a sorted list of indices (col, row) from the set of BoardNode objects.
        Also defines some class variables and assigns values to them.

        Parameters:
            set_objects (Set[BoardNode]): Set of BoardNode objects.

        Returns:
            List[Tuple[int, int]]: Sorted list of indices (col, row).
        '''
        from operator import itemgetter
        sorting_list: List[Tuple[int, int]] = []
        for item in set_objects:
            sorting_list.append((item.row, item.col))
        sorting_list.sort(key=lambda item: (item[0], item[1]))
        self.xmax: int = sorting_list[-1][0]
        self.xmin: int = sorting_list[0][0]
        self.ymax: int = max(sorting_list, key=itemgetter(1))[1]
        self.ymin: int = min(sorting_list, key=itemgetter(1))[1]
        return sorting_list

    def make_list_values(self, set_objects: Set[BoardNode]) -> List[Tuple[int, int, Tuple[int, int, int]]]:
        '''
        Generate a sorted list of values (col, row, stone_color) from the set of BoardNode objects.
        '''
        sorting_list: List[Tuple[int, int]] = []
        for item in set_objects:
            sorting_list.append((item.row, item.col, (item.stone_here_color)))
        sorting_list.sort(key=lambda item: (item[0], item[1]))
        return sorting_list


class GoBoard():
    def __init__(self, board_size=19, defaults=True):
        self.defaults: bool = defaults
        self.board_size: int = board_size
        self.board: List[List[BoardNode]] = self.setup_board()
        self.init_helper_player()

        # Turn and log attributes
        self.times_passed, self.turn_num = 0, 0
        self.position_played_log: List[Union[str, Tuple[str, int, int]]] = []
        self.visit_kill: Set[BoardNode] = set()
        self.killed_last_turn: Set[BoardNode] = set()
        self.killed_log: List[List[Union[Tuple[Tuple[int, int, int], int, int], List[None]]]] = list()

        # Mode and handicap attributes
        self.mode, self.mode_change = "Playing", True
        self.handicap: Tuple[bool, str, int] = Handicap.default_handicap()

        # pygame and pySimpleGui attributes
        self.window: sg.Window = None
        self.screen: pygame.Surface = None
        self.backup_board: pygame.Surface = None
        self.pygame_board_vals: Tuple[int, float, float] = None  # (workable_area, distance, circle_radius)

    def init_helper_player(self) -> None:
        '''Initializes class variables to do with the players'''
        self.player_black: Player = Player.setup_player(self.defaults, "Player One", "Black", cf.unicode_black)
        self.player_white: Player = Player.setup_player(self.defaults, "Player Two", "White", cf.unicode_white)
        self.whose_turn: Player = self.player_black
        self.not_whose_turn: Player = self.player_white

    def make_board_string(self) -> str:
        '''
        Generate a string representation of the current game board.

        Returns a string representing the board state, where each character represents the color of a stone.
        '1' for black, '2' for white, and '0' for an empty intersection.
        The first character represents the player's turn (1 for black, 2 for white).
        '''
        board_string = '1' if self.whose_turn == self.player_black else '2'
        for xidx in range(len(self.board)):
            for yidx in range(len(self.board)):
                if self.board[xidx][yidx].stone_here_color == cf.unicode_none:
                    board_string += "0"
                elif self.board[xidx][yidx].stone_here_color == cf.unicode_black:
                    board_string += '1'
                else:
                    board_string += '2'
        return board_string

    def setup_board(self) -> List[List[BoardNode]]:  # Refactor/change up the hardcoded numbers
        '''
        Sets up and returns the initialized board.
        Returns a 2D list representing the game board with initialized BoardNode objects.
        '''
        board: List[List[BoardNode]] = [[BoardNode(row, col) for col in range(self.board_size)] for row in range(self.board_size)]
        for node in board:
            for item in node:
                workable_area: float = 620.0 / (self.board_size - 1)
                item.screen_row = 40 + workable_area * item.col
                item.screen_col = 40 + workable_area * item.row
                friends: List[Tuple[int, int]] = self.check_neighbors(item)
                for place in friends:
                    item.connections.add(board[place[0]][place[1]])
        return board

    def check_neighbors(self, piece) -> List[Tuple[int, int]]:
        '''Takes in a boardNode, returns a list of tuples of coordinates'''
        neighbors = [(piece.row - 1, piece.col), (piece.row + 1, piece.col),
                     (piece.row, piece.col - 1), (piece.row, piece.col + 1)]
        valid_neighbors: List[Tuple[int, int]] = []
        for coordinate in neighbors:
            if 0 <= coordinate[0] < self.board_size and 0 <= coordinate[1] < self.board_size:
                valid_neighbors.append(coordinate)
        return valid_neighbors

    def read_window(self):
        event, values = self.window.read()
        return event, values

    def switch_player(self) -> None:
        '''Switches the current player by updating whose_turn and not_whose_turn'''
        if self.whose_turn == self.player_black:
            self.whose_turn = self.player_white
            self.not_whose_turn = self.player_black
        else:
            self.whose_turn = self.player_black
            self.not_whose_turn = self.player_white

    def play_game(self, from_file: Optional[bool] = False, fixes_handicap: Optional[bool] = False) -> None:
        '''
        This function figures out the gamemode of the board (playing, finished, scoring) and then calls the appropriate function.
        from_file: a bool representing if the board should be loaded from file
        fixes_handicap: a bool representing if a player has a handicap or not
        '''
        if self.mode == "Playing":
            winner = self.play_game_playing_mode(from_file, fixes_handicap)
            return winner
        elif self.mode == "Finished":
            self.play_game_view_endgame()
        elif from_file is True and not self.mode_change:
            ui.refresh_board_pygame(self)
            self.scoring_block()

        else:
            ui.refresh_board_pygame(self)
            self.mode_change = True
            self.times_passed = 0
            self.scoring_block()

    def play_game_playing_mode(self, from_file, fixes_handicap) -> None:
        '''
        This function handles the game logic during the "Playing" mode.
        It sets up the board and does handicaps if necessary based on from_file and fixes_handicap variable.
        It also executes turns for both players until the game enters the "Scoring" mode.
        from_file: a bool representing if the board should be loaded from file
        fixes_handicap: a bool representing if a player has a handicap or not
        '''
        if not from_file:
            self.board = self.setup_board()
        else:
            ui.refresh_board_pygame(self)
        if fixes_handicap:
            hc: Handicap = Handicap(self)
            self.handicap = hc.custom_handicap(False)
        self.turn_loop()
        self.mode = "Scoring"
        self.times_passed = 0
        self.resuming_scoring_buffer("Scoring")
        return self.playing_mode_end_of_game()

    def playing_mode_end_of_game(self):
        ui.end_game_popup()
        return self.scoring_block()

    def turn_loop(self):
        while (self.times_passed <= 1):
            self.play_turn()

    def play_game_view_endgame(self) -> None:  # Might be wrong, requires testing.
        '''Allows the user to view a completed game'''
        ui.refresh_board_pygame(self)
        event, _ = self.read_window()
        if event == "Exit Game":
            from main import play_game_main
            ui.close_window(self)
            play_game_main()
            quit()
        elif event == sg.WIN_CLOSED:
            quit()

    def scoring_block(self) -> bool:
        '''
        Manages the scoring phase of the game.
        This function iterates through the scoring phase, allowing players to remove dead stones.
        When the scoring is finished, it calls 'making_score_board_object()' to determine the winner.
        '''
        while self.mode != "Finished":
            if self.mode_change:
                ui.switch_button_mode(self)
            while self.mode == "Scoring":
                from remove_dead import remove_dead
                remove_dead(self)
                if self.times_passed == 2:
                    self.mode = "Finished"
            if self.mode_change:
                if not self.mode == "Scoring":
                    self.window["Res"].update("Quit Program")
            while (self.times_passed <= 1):
                self.play_turn()
            if self.times_passed == 2 and self.mode == "Playing":
                self.mode = "Scoring"
                self.resuming_scoring_buffer("Scoring")
                self.times_passed = 0
        from scoringboard import making_score_board_object
        winner = making_score_board_object(self)
        self.end_of_game()
        return winner

    def resuming_scoring_buffer(self, text) -> None:
        '''Updates the some class variables when resuming a game (i.e. going from Scoring to Playing)'''
        self.turn_num += 1
        self.position_played_log.append(text)
        self.killed_log.append([])

    def end_of_game(self) -> None:
        '''Handles the end of the game, i.e. displaying the winner, saving the game state, and returning to the main menu.'''
        ui.end_game_popup_two(self)
        ui.default_popup_no_button("Please save to a file, thank you.", 3)
        from saving_loading import save_pickle
        save_pickle(self)

    def find_piece_click(self, input_location: Tuple[float, float]) -> Tuple[bool, Union[List[int], BoardNode]]:
        '''Finds the BoardNode corresponding to a clicked location on the game board.'''
        for item_row in self.board:
            for item in item_row:
                item_location = [item.screen_row, item.screen_col]
                if math.dist(input_location, item_location) <= self.pygame_board_vals[2]:
                    return True, item
        return False, [-1, -1]

    def play_turn(self) -> None:  # Refactor
        '''This function plays a turn by capturing info from a mouse click or a bot move and then plays the turn.'''
        ui.update_scoring(self)
        truth_value: bool = False
        while not truth_value:
            event, values = self.read_window()
            if event != "-GRAPH-":
                from turn_options import normal_turn_options
                normal_turn_options(self, event, text="Passed")
                if event == "Pass Turn" or event == "Res" or event == "Undo Turn":
                    return
            else:
                row, col = values['-GRAPH-']
                found_piece, piece = self.find_piece_click([row, col])
                if found_piece:
                    truth_value = self.play_piece(piece.row, piece.col)

                    if truth_value:
                        self.times_passed = 0
        self.make_turn_info()
        return

    def make_turn_info(self):
        temp_list: List[Tuple[Tuple[int, int, int], int, int]] = list()
        for item in self.killed_last_turn:
            temp_list.append((self.not_whose_turn.unicode, item.row, item.col))
        self.killed_log.append(temp_list)
        self.switch_player()

    def play_piece(self, row: int, col: int) -> bool:
        '''Attempts to play a piece on the board and handles rule violations.'''
        piece: BoardNode = self.board[row][col]
        if (piece.stone_here_color != cf.unicode_none):
            ui.def_popup("You tried to place where there is already a piece. Please try your turn again.", 2)
            return False
        elif (self.turn_num > 2 and self.ko_rule_break(piece) is True):
            ui.def_popup("Place the piece there would break the ko rule. Please try your turn again.", 2)
            return False
        elif (self.kill_stones(piece) is True):
            piece_placement(self, piece, row, col)
            ui.refresh_board_pygame(self)
            return True
        elif (self_death_rule(self, piece, self.whose_turn) == 0):
            ui.def_popup("Place the piece there would break the self death rule. Please try your turn again.", 2)
            return False
        else:
            piece_placement(self, piece, row, col)
            ui.refresh_board_pygame(self)
            self.killed_last_turn.clear()
            return True

    def ko_rule_break(self, piece: BoardNode) -> bool:  # no superko, but if it becomes a problem...
        '''Checks if placing a piece breaks the ko rule.'''
        if self_death_rule(self, piece, self.whose_turn) > 0:
            return False
        if piece in self.killed_last_turn:
            return True
        return False

    def kill_stones(self, piece: BoardNode) -> bool:  # needs to return true if it does kill stones
        '''
        Determines if placing a piece kills opponent's stones and removes them if needed.
        Returns True if placing the piece kills stones, False otherwise.
        '''
        piece.stone_here_color = self.whose_turn.unicode
        neighboring_pieces: Set[BoardNode] = piece.connections
        truth_value: bool = False
        for neighbor in neighboring_pieces:
            if neighbor.stone_here_color == self.not_whose_turn.unicode:
                if (self_death_rule(self, neighbor, self.not_whose_turn) == 0):
                    remove_stones(self)
                    truth_value = True
        if truth_value is False:
            piece.stone_here_color = cf.unicode_none
        return truth_value


@staticmethod
def self_death_rule(self, piece: BoardNode, which_player: Player, visited: Optional[Set[BoardNode]] = None) -> int:
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
            liberties += self_death_rule(self, neighbor, which_player, visited)
    self.visit_kill = visited
    return liberties


@staticmethod
def remove_stones(self) -> None:
    '''Removes stones marked for removal.'''
    self.killed_last_turn.clear()
    for position in self.visit_kill:
        self.killed_last_turn.add(position)
        position.stone_here_color = cf.unicode_none


@staticmethod
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


@staticmethod
def fills_eye(self, piece: BoardNode, whose_turn_uni, not_whose_uni) -> bool:
    '''Check if placing a stone in the given position would fill an eye.'''
    # False means it will not fill an eye, so it can place there
    for neighbor in piece.connections:
        if neighbor.stone_here_color != whose_turn_uni:
            return False
    piece_diagonals = diagonals_setup(self, piece)
    counter = 0
    dual_eye_check = False
    bad_diagonals = False

    for item in piece_diagonals:
        if item.stone_here_color == cf.unicode_none:
            # This next thing checks to see if that diagonal is also a eye (dual eye setup) plus more
            surrounded_properly = True
            for neighbor in item.connections:
                if neighbor.stone_here_color != whose_turn_uni:
                    # This doesn't fully work safely (sometimes fills eyes),
                    # but i think a NN will eventually figure out what is a dumb move
                    surrounded_properly = False
            if not surrounded_properly:
                counter += 1
            if surrounded_properly:
                item_diagonals = diagonals_setup(self, item)
                temp_counter = 0
                # This next thing checks to see if that diagonal is also a eye (dual eye setup)
                for second_item in item_diagonals:
                    if second_item.stone_here_color != whose_turn_uni:
                        temp_counter += 1
                if temp_counter < 2:
                    dual_eye_check = True
                else:
                    counter += 1
                    # This might be bad/not correct... But maybe a NN will be able to figure out not acting dumb
            # I might need to eventually add in a check regarding honeycomb shapes, if it doesn't work properly...
        elif item.stone_here_color == not_whose_uni:
            counter += 1

    if counter > 1:
        bad_diagonals = True

    if bad_diagonals:  # Therefore it's ok to fill
        return False
    elif dual_eye_check:  # Therefore don't fill
        return True
    else:  # Not ok to fill
        return True


@staticmethod
def play_piece_bot(self, row: int, col: int) -> bool:
    '''
    This function represents the bot's move during a turn.
    It checks if the move is valid, updates the game state, and handles capturing stones.
    row, col: ints representing the row and column of where the bot is playing.
    '''
    piece: BoardNode = self.board[row][col]
    if (piece.stone_here_color != cf.unicode_none):
        return False
    elif (self.turn_num > 2 and self.ko_rule_break(piece) is True):
        return False
    elif (self.kill_stones(piece) is True):
        piece_placement(self, piece, row, col)
        return True
    elif (self_death_rule(self, piece, self.whose_turn) == 0):
        return False
    elif fills_eye(self, piece, self.whose_turn.unicode, self.not_whose_turn.unicode):
        return False
    else:
        piece_placement(self, piece, row, col)
        self.killed_last_turn.clear()
        return True


@staticmethod
def play_turn_bot_helper(self, truth_value, val):
    if val == (self.board_size * self.board_size):
        self.times_passed += 1
        self.turn_num += 1
        self.position_played_log.append(("Pass", -3, -3))
        self.killed_log.append([])
        self.switch_player()
        return "Break"
    else:
        row = val // self.board_size
        col = val % self.board_size
        piece = self.board[row][col]
        found_piece = True
    if found_piece:
        truth_value = play_piece_bot(self, piece.row, piece.col)
        if truth_value:
            self.times_passed = 0
    return truth_value


@staticmethod
def piece_placement(self, piece: BoardNode, row: int, col: int) -> None:
    '''Places a piece on the board and updates game state.'''
    piece.stone_here_color = self.whose_turn.unicode
    self.turn_num += 1
    self.position_played_log.append((self.whose_turn.color, row, col))
