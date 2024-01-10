import uifunctions as ui
import pygame
from handicap import Handicap
from goclasses import GoBoard, BoardNode
import config as cf
from random import randrange

import PySimpleGUI as sg
import math
import sys
from player import Player
from typing import Tuple, Optional, List, Set, Union, Type


sys.setrecursionlimit(10000)

class NNBoard(GoBoard):  # Need to override the scoring/removing dead pieces bit... once i finish that...
    def __init__(self, board_size=19, defaults=True):
        #super().__init__(board_size, defaults)
        self.ai_training_info: List[Tuple[str, Tuple[int, int]]] = []  # Might be Tuple of placement, or maybe a string

        self.defaults: bool = defaults
        self.board_size: int = board_size
        self.board: List[List[BoardNode]] = self.setup_board()
        self.init_helper_player()

        # Turn and log attributes
        self.times_passed, self.turn_num = 0, 0
        PPL_Type = List[Union[str, Tuple[str, int, int]]]
        self.position_played_log: PPL_Type = []
        self.visit_kill: Set[BoardNode] = set()
        self.killed_last_turn: Set[BoardNode] = set()
        KL_Type = List[List[Union[Tuple[Tuple[int, int, int], int, int], List[None]]]]
        self.killed_log: KL_Type = list()

        # Mode and handicap attributes
        self.mode, self.mode_change = "Playing", True
        self.handicap: Tuple[bool, str, int] = Handicap.default_handicap()

        # pygame and pySimpleGui attributes
        #self.window: sg.Window = None
        #self.screen: pygame.Surface = None
        #self.backup_board: pygame.Surface = None
        #self.pygame_board_vals: Tuple[int, float, float] = None  # (workable_area, distance, circle_radius)


    def play_game(self, from_file: Optional[bool] = False, fixes_handicap: Optional[bool] = False):
        '''
        This function figures out the gamemode of the board (playing, finished, scoring) and then calls the appropriate function.
        from_file: a bool representing if the board should be loaded from file
        fixes_handicap: a bool representing if a player has a handicap or not
        '''
        if self.mode == "Playing":
            temp = self.play_game_playing_mode(from_file, fixes_handicap)
            return temp  # This is a hack to manage AI training. Fix eventually.
        elif self.mode == "Finished":
            self.play_game_view_endgame()
        elif from_file is True and not self.mode_change:
            #self.refresh_board_pygame()
            self.scoring_block()

        else:
            #self.refresh_board_pygame()
            self.mode_change = True
            self.times_passed = 0
            self.scoring_block()

    def play_game_playing_mode(self, from_file, fixes_handicap):
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
            #self.refresh_board_pygame()
            if self.position_played_log[-1][0] == "Black":
                self.switch_player()
                self.play_turn(True)
        if fixes_handicap:
            hc: Handicap = Handicap(self)
            self.handicap = hc.custom_handicap(False)
        while (self.times_passed <= 1):
            if self.whose_turn == self.player_black:
                self.play_turn(True)  # Change this to true if you want it to be bot vs bot
            elif self.whose_turn == self.player_white:
                self.play_turn(True)

        self.mode = "Scoring"
        self.times_passed = 0  # This is a hack to manage AI training. Fix eventually.
        self.resuming_scoring_buffer("Scoring")
        # ui.end_game_popup()
        # winner = self.scoring_block()
        print("Pause1. This is scoringboard stuff. Unsure if needs window or not.")
        winner = self.making_score_board_object()
        print(f"winner is {winner}")
        return (self.ai_training_info, winner)  # This is a hack to manage AI training. Fix eventually.

    def play_turn(self, bot: Optional[bool] = False) -> None:
        '''
        This function plays a turn by capturing info from a mouse click or a bot move and then plays the turn.
        bot: a bool indicating if a bot is playing this turn.
        '''
        #ui.update_scoring(self)
        truth_value: bool = False
        placement = None
        tries = 0
        print("uwu")
        while not truth_value:
            if not bot:
                event, values = self.window.read()
            else:
                event = "-GRAPH-"  # ! Black Box Func for now

            if event != "-GRAPH-":
                # self.combined_network.send(f"{event} ")
                self.turn_options(event, text="Passed")
                if event == "Pass Turn" or event == "Res" or event == "Undo Turn":
                    return
            else:
                if not bot:
                    row, col = values['-GRAPH-']
                    found_piece, piece = self.find_piece_click([row, col])
                else:  # ! Black Box Func for now
                    #Two different ways for managing having a pass function. Choose as you like.
                    val = randrange(0, (self.board_size * self.board_size))
                    tries += 1
                    if tries >= 120:
                        val = self.board_size * self.board_size

                    """if self.turn_num >= 54:
                        val = randrange(0, (self.board_size*self.board_size)+1)
                    else:
                        val = randrange(0, (self.board_size*self.board_size))"""
                    if val == (self.board_size*self.board_size):
                        self.times_passed += 1
                        self.turn_num += 1
                        self.position_played_log.append(("Pass", -3, -3))
                        self.killed_log.append([])
                        self.switch_player()
                        return
                    else:
                        row = val // self.board_size
                        col = val % self.board_size
                        placement: Tuple = (row, col)
                        piece = self.board[row][col]
                        found_piece = True
                if found_piece:
                    if not bot:
                        truth_value = self.play_piece(piece.row, piece.col)
                    else:
                        truth_value = self.play_piece_bot(piece.row, piece.col)
                    if truth_value:
                        self.times_passed = 0
                        #pygame.draw.circle(self.screen, self.whose_turn.unicode,
                        #                   (piece.screen_row, piece.screen_col), self.pygame_board_vals[2])
                        #pygame.display.update()
        temp_list: List[Tuple[Tuple[int, int, int], int, int]] = list()
        for item in self.killed_last_turn:
            temp_list.append((self.not_whose_turn.unicode, item.row, item.col))
        self.killed_log.append(temp_list)
        turn_string = (self.make_board_string(), placement)
        self.ai_training_info.append(turn_string)
        self.switch_player()
        return

    def remove_dead(self) -> None:
        '''
        This function waits for player input to select dead stones, and then processes the removal of those stones.
        '''
        self.killed_last_turn.clear()
        ui.update_scoring(self)
        truth_value: bool = False
        while not truth_value:
            event, values = self.window.read()
            else_choice: bool = self.remove_dead_event_handling(event)
            if not else_choice:
                return
            row, col = values['-GRAPH-']
            found_piece, piece = self.find_piece_click([row, col])
            if found_piece and piece.stone_here_color == cf.unicode_none:
                ui.def_popup("You can't remove empty areas", 1)
            elif found_piece:
                other_user_agrees, piece_string = self.remove_dead_found_piece(piece)
                if other_user_agrees == "No":
                    self.remove_dead_undo_list(piece_string)
                    return

                self.remove_stones_and_update_score(piece_string)
                break
        self.switch_player()
        return

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
            self.piece_placement(piece, row, col)
            return True
        elif (self.self_death_rule(piece, self.whose_turn) == 0):
            return False
        elif self.fills_eye(piece):
            return False
        else:
            self.piece_placement(piece, row, col)
            self.killed_last_turn.clear()
            return True

    def fills_eye(self, piece: BoardNode) -> bool:
        '''Check if placing a stone in the given position would fill an eye.'''
        # False means it will not fill an eye, so it can place there
        for neighbor in piece.connections:
            if neighbor.stone_here_color != self.whose_turn.unicode:
                return False
        piece_diagonals = self.diagonals_setup(piece)
        counter = 0
        dual_eye_check = False
        bad_diagonals = False

        for item in piece_diagonals:
            if item.stone_here_color == cf.unicode_none:
                # This next thing checks to see if that diagonal is also a eye (dual eye setup) plus more
                surrounded_properly = True
                for neighbor in item.connections:
                    if neighbor.stone_here_color != self.whose_turn.unicode:
                        # This doesn't fully work safely (sometimes fills eyes),
                        # but i think a NN will eventually figure out what is a dumb move
                        surrounded_properly = False
                if not surrounded_properly:
                    counter += 1
                if surrounded_properly:
                    item_diagonals = self.diagonals_setup(piece)
                    temp_counter = 0
                    # This next thing checks to see if that diagonal is also a eye (dual eye setup)
                    for second_item in item_diagonals:
                        if second_item.stone_here_color != self.whose_turn.unicode:
                            temp_counter += 1
                    if temp_counter < 2:
                        dual_eye_check = True
                    else:
                        counter += 1
                        # This might be bad/not correct... But maybe a NN will be able to figure out not acting dumb
                # I might need to eventually add in a check regarding honeycomb shapes, if it doesn't work properly...
            elif item.stone_here_color == self.not_whose_turn.unicode:
                counter += 1

        if counter > 1:
            bad_diagonals = True

        if bad_diagonals:  # Therefore it's ok to fill
            return False
        elif dual_eye_check:  # Therefore don't fill
            return True
        else:  # Not ok to fill
            return True

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

























    def init_helper_player(self) -> None:
        '''Initializes class variables to do with the players'''
        self.player_black: Player = Player.setup_player(self.defaults, "Player One", "Black", cf.unicode_black)
        self.player_white: Player = Player.setup_player(self.defaults, "Player Two", "White", cf.unicode_white)
        self.whose_turn: Player = self.player_black
        self.not_whose_turn: Player = self.player_white

    def make_board_string(self) -> str:   # Target of optimization
        '''
        Generate a string representation of the current game board.

        Returns a string representing the board state, where each character represents the color of a stone.
        '1' for black, '2' for white, and '0' for an empty intersection.
        The first character represents the player's turn (1 for black, 2 for white).
        '''
        # It needs to add in the turn choice made somehow.
        board_string = '1' if self.whose_turn == self.player_black else '2'
        for xidx in range(len(self.board)):
            for yidx in range(len(self.board)):
                if self.board[yidx][xidx].stone_here_color == cf.unicode_none:
                    board_string += "0"
                elif self.board[yidx][xidx].stone_here_color == cf.unicode_black:
                    board_string += '1'
                else:
                    board_string += '2'
        return board_string

    def setup_board(self) -> List[List[BoardNode]]:
        '''
        Sets up and returns the initialized board.
        Returns a 2D list representing the game board with initialized BoardNode objects.
        '''
        board: List[List[BoardNode]] = [[BoardNode(row, col) for col in range(self.board_size)] for row in range(self.board_size)]
        for node in board:
            for item in node:
                workable_area: int = 620 / (self.board_size - 1)
                item.screen_row: float = 40 + workable_area * item.row
                item.screen_col: float = 40 + workable_area * item.col
                friends: List[Tuple[int, int]] = self.check_neighbors(item)
                for place in friends:
                    item.connections.add(board[place[0]][place[1]])
        return board

    def switch_player(self) -> None:
        '''Switches the current player by updating whose_turn and not_whose_turn'''
        if self.whose_turn == self.player_black:
            self.whose_turn = self.player_white
            self.not_whose_turn = self.player_black
        else:
            self.whose_turn = self.player_black
            self.not_whose_turn = self.player_white


    def play_game_view_endgame(self) -> None:  # Might be wrong, requires testing.
        '''Allows the user to view a completed game'''
        #self.refresh_board_pygame()
        event, _ = self.window.read()
        if event == "Exit Game":
            from main import play_game_main
            self.close_window()
            play_game_main()
            quit()
        elif event == sg.WIN_CLOSED:
            quit()

    def switch_button_mode(self) -> None:
        '''Updates the button text in the PySimpleGui window'''
        if self.mode == "Scoring":
            self.window["Res"].update("Resume Game")
            self.times_passed = 0
        elif self.mode == "Playing":
            self.window["Res"].update("Quit Program")
        self.mode_change = False

    def scoring_block(self) -> bool:
        '''
        Manages the scoring phase of the game.
        This function iterates through the scoring phase, allowing players to remove dead stones.
        When the scoring is finished, it calls 'making_score_board_object()' to determine the winner.
        '''
        while self.mode != "Finished":
            if self.mode_change:
                self.switch_button_mode()
            while self.mode == "Scoring":
                self.remove_dead()
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
        print("Pause2. This is scoringboard stuff. Unsure if needs window or not.")
        winner = self.making_score_board_object()
        return winner

    def resuming_scoring_buffer(self, text) -> None:
        '''Updates the some class variables when resuming a game (i.e. going from Scoring to Playing)'''
        self.turn_num += 1
        self.position_played_log.append(text)
        self.killed_log.append([])

    def remove_dead_found_piece(self, piece: BoardNode) -> Tuple[str, List[Tuple[Tuple[int, int], Tuple[int, int, int]]]]:
        '''
        Helper function for remove_dead().
        Uses floodfill to find all connected Nodes of the same color as the variable piece.
        Gets the agreement (or disagreement) of the other player.
        '''
        from scoringboard import ScoringBoard
        series: Tuple[Set[BoardNode], Set[BoardNode]] = ScoringBoard.flood_fill(piece)  # !
        piece_string: List[Tuple[Tuple[int, int], Tuple[int, int, int]]] = list()
        for item in series[0]:
            if item.stone_here_color == self.player_black.unicode:
                piece_string.append(((item.row, item.col), item.stone_here_color))
                item.stone_here_color = cf.unicode_diamond_black

            else:
                piece_string.append(((item.row, item.col), item.stone_here_color))
                item.stone_here_color = cf.unicode_diamond_white
        #self.refresh_board_pygame()
        info: str = "Other player, please click yes if you are ok with these changes"
        other_user_agrees: str = sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))
        return other_user_agrees, piece_string

    def remove_dead_undo_list(self, piece_string: List[Tuple[Tuple[int, int], Tuple[int, int, int]]]) -> None:
        '''Undoes the removal of dead stones and revert the board to its previous state.'''
        for tpl in piece_string:
            item: BoardNode = self.board[tpl[0][0]][tpl[0][1]]
            if item.stone_here_color == cf.unicode_diamond_black:
                item.stone_here_color = self.player_black.unicode
            elif item.stone_here_color == cf.unicode_diamond_white:
                item.stone_here_color = self.player_white.unicode
        #self.refresh_board_pygame()

    def remove_stones_and_update_score(self, piece_string: List[Tuple[Tuple[int, int], Tuple[int, int, int]]]) -> None:
        '''
        Helper function for remove_dead().
        Removes stones marked as dead during scoring and update player scores.
        '''
        for tpl in piece_string:
            item: BoardNode = self.board[tpl[0][0]][tpl[0][1]]
            item.stone_here_color = cf.unicode_none

        #self.refresh_board_pygame()
        captured_count: int = len(piece_string)
        self.player_white.captured += captured_count if piece_string[0][1] == self.player_black.unicode else 0
        self.player_black.captured += captured_count if piece_string[0][1] == self.player_white.unicode else 0

        temp_list: List[Tuple[Tuple[int, int, int], int, int, str]] = list()
        for item in piece_string:
            temp_list.append((item[1], item[0][0], item[0][1], "Scoring"))

        self.killed_log.append(temp_list)
        self.position_played_log.append("Dead Removed")
        self.turn_num += 1

    def end_of_game(self) -> None:
        '''Handles the end of the game, i.e. displaying the winner, saving the game state, and returning to the main menu.'''
        ui.end_game_popup_two(self)
        ui.default_popup_no_button("Please save to a file, thank you.", 3)
        self.save_pickle()
        from main import play_game_main
        self.close_window()
        play_game_main()
        quit()

    def find_piece_click(self, input_location: Tuple[float, float]) -> Tuple[bool, Union[List[int], BoardNode]]:
        '''Finds the BoardNode corresponding to a clicked location on the game board.'''
        for item_row in self.board:
            for item in item_row:
                item_location = [item.screen_row, item.screen_col]
                if math.dist(input_location, item_location) <= self.pygame_board_vals[2]:
                    return True, item
        return False, [-1, -1]


    def turn_options(self, event, text: Optional[str] = None) -> None:
        '''Handles various game options based on the given event.'''
        if event in (sg.WIN_CLOSED, "Res"):
            quit()
        if event == "Pass Turn":
            ui.def_popup("Skipped turn", 0.5)
            self.times_passed += 1
            self.turn_num += 1
            self.position_played_log.append((text, -3, -3))
            self.killed_log.append([])
            self.switch_player()
        elif event == "Save Game":
            self.save_pickle()
        elif event == "Undo Turn":
            if self.turn_num == 0:
                ui.def_popup("You can't undo when nothing has happened.", 2)
            elif self.turn_num >= 1:
                self.undo_checker()
                return
        elif event == "Exit Game":
            from main import play_game_main
            self.close_window()
            play_game_main()
            quit()
        else:
            raise ValueError

    def remove_dead_event_handling(self, event) -> None:
        '''Handles events related to removing dead stones during scoring.'''
        if event == "Pass Turn":
            self.turn_options(event, text="Scoring Passed")
            return
        elif event == "Save Game":
            self.save_pickle()
        elif event == "Res":
            self.mode = "Playing"
            self.mode_change = True
            self.resuming_scoring_buffer("Resumed")
            return
        elif event == "Undo Turn":
            self.turn_options(event)
            return
        elif event == "Exit Game":
            from main import play_game_main
            self.close_window()
            play_game_main()
            quit()
        elif event == sg.WIN_CLOSED:
            quit()
        else:
            return True

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
            self.piece_placement(piece, row, col)
            return True
        elif (self.self_death_rule(piece, self.whose_turn) == 0):
            ui.def_popup("Place the piece there would break the self death rule. Please try your turn again.", 2)
            return False
        else:
            self.piece_placement(piece, row, col)
            self.killed_last_turn.clear()
            return True

    def piece_placement(self, piece: BoardNode, row: int, col: int) -> None:
        '''Places a piece on the board and updates game state.'''
        piece.stone_here_color = self.whose_turn.unicode
        self.turn_num += 1
        self.position_played_log.append((self.whose_turn.color, row, col))
        #self.refresh_board_pygame()

# Potential for splitting the undo functionality to it's own file
    def undo_checker(self) -> None:
        '''Calls the undo_turn function with appropriate parameters'''
        if self.mode == "Scoring":
            self.undo_turn(scoring=True)
        else:
            self.undo_turn()

    def undo_turn(self, scoring: Optional[bool] = False) -> None:
        '''Undo the most recent turn, reverting the board to its state one turn ago.'''
        if self.undo_special_cases():
            return
        if not scoring:
            _, row, col = self.position_played_log.pop()
            self.board[row][col].stone_here_color = cf.unicode_none
        else:
            self.position_played_log.pop()
        # This part reverts the board back to its state 1 turn ago
        revive = self.killed_log.pop()
        capture_update_val: int = len(revive)

        if len(revive) > 0:
            unicode: Tuple[int, int, int] = revive[0][0]
        else:
            unicode: Tuple[int, int, int] = cf.unicode_none
        for item in revive:
            if not scoring:
                unicode, row, col = item
            else:
                unicode, row, col, scoring = item
            place: BoardNode = self.board[row][col]
            place.stone_here_color = unicode
        #self.refresh_board_pygame()
        self.turn_num -= 1
        self.not_whose_turn.captured -= capture_update_val
        self.switch_player()

    def undo_special_cases(self) -> bool:
        '''Handle special cases during undo, such as resuming scoring or handling consecutive passes.'''
        last_entry: str = self.position_played_log[-1]

        if last_entry == "Resumed" or last_entry == "Scoring":
            tmp: str = self.position_played_log.pop()
            self.move_back()
            self.turn_num -= 1
            self.mode_change = True

            if tmp == "Resumed":
                self.mode = "Scoring"
                self.times_passed = 2
            elif tmp == "Scoring":
                self.mode = "Playing"
            return True

        if last_entry[0] in {"Passed", "Scoring Passed"}:
            self.position_played_log.pop()
            self.move_back()
            self.turn_num -= 1
            self.times_passed = 0

            if self.position_played_log and self.position_played_log[-1][0] in {"Passed", "Scoring Passed"}:
                self.times_passed = 1

            self.switch_player()
            return True
        return False

    def move_back(self) -> None:
        '''Move back to the previous killed state, updating self.killed_last_turn.'''
        if len(self.killed_log) > 0:
            self.killed_last_turn.clear()
            temp_list = self.killed_log.pop()
            for item in temp_list:
                temp_node = BoardNode(row_value=item[1], col_value=item[2])
                self.killed_last_turn.add(temp_node)

    def ko_rule_break(self, piece: BoardNode) -> bool:  # no superko, but if it becomes a problem...
        '''Checks if placing a piece breaks the ko rule.'''
        if self.self_death_rule(piece, self.whose_turn) > 0:
            return False
        if piece in self.killed_last_turn:
            return True
        return False

    def check_neighbors(self, piece) -> List[Tuple[int, int]]:
        '''Takes in a boardNode, returns a list of tuples of coordinates'''
        neighbors = [(piece.row - 1, piece.col), (piece.row + 1, piece.col),
                     (piece.row, piece.col - 1), (piece.row, piece.col + 1)]
        valid_neighbors: List[Tuple[int, int]] = []
        for coordinate in neighbors:
            if 0 <= coordinate[0] < self.board_size and 0 <= coordinate[1] < self.board_size:
                valid_neighbors.append(coordinate)
        return valid_neighbors

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
                liberties += self.self_death_rule(neighbor, which_player, visited)
        self.visit_kill = visited
        return liberties

    def remove_stones(self) -> None:
        '''Removes stones marked for removal and updates the player's captured count.'''
        self.killed_last_turn.clear()
        for position in self.visit_kill:
            self.killed_last_turn.add(position)
            self.whose_turn.captured += 1
            position.stone_here_color = cf.unicode_none

    def kill_stones(self, piece: BoardNode) -> bool:  # needs to return true if it does kill stones
        '''
        Determines if placing a piece kills opponent's stones and removes them if needed.
        Returns True if placing the piece kills stones, False otherwise.
        '''
        piece.stone_here_color: Tuple[int, int, int] = self.whose_turn.unicode
        neighboring_pieces: Set[BoardNode] = piece.connections
        truth_value: bool = False
        for neighbor in neighboring_pieces:
            if neighbor.stone_here_color == self.not_whose_turn.unicode:
                if (self.self_death_rule(neighbor, self.not_whose_turn) == 0):
                    self.remove_stones()
                    truth_value = True
        if truth_value is False:
            piece.stone_here_color = cf.unicode_none
        return truth_value

    def save_to_SGF(self, filename2: str) -> None:
        '''Saves the current game to a SGF file.'''
        with open(f"{filename2}.sgf", 'w', encoding='utf-8') as file:
            from datetime import date
            seqs = ["Dead Removed", "Break between handicaps and normal play", "Dead Removed",
                    "Resumed", "Scoring", "Scoring Passed"]
            movement_string: str = ""
            today = date.today()
            header: str = f"(;\nFF[4]\nCA[UTF-8]\nGM[1]\nDT[{today}]\nGN[relaxed]\n\
            PC[https://github.com/EGPeat/GoGame]\n\
            PB[{self.player_black.name}]\n\
            PW[{self.player_white.name}]\n\
            BR[Unknown]\nWR[Unknown]\n\
            OT[Error: time control missing]\nRE[?]\n\
            SZ[{self.board_size}]\nKM[{self.player_white.komi}]\nRU[Japanese];"
            file.write(header)
            handicap_flag: bool = self.handicap[0]
            for idx, item in enumerate(self.position_played_log):
                if handicap_flag and idx < self.handicap[2]:
                    color: str = 'B' if self.handicap[1] == "Black" else 'W'
                    row: str = chr(97 + int(item[1]))
                    col: str = chr(97 + int(item[2]))
                    text: str = f";{color}[{col}{row}]\n"
                    movement_string += text
                elif item[0] in seqs or item in seqs:
                    pass
                elif item[0] == "Passed":
                    if movement_string[-7] == "B" or movement_string[-5] == "B":
                        text2: str = ";W[]\n"
                    else:
                        text2: str = ";B[]\n"
                    movement_string += text2
                else:
                    row: str = chr(97 + int(item[1]))
                    col: str = chr(97 + int(item[2]))
                    color: str = 'B' if item[0] == self.player_black.color else 'W'
                    text: str = f";{color}[{col}{row}]\n"
                    movement_string += text
            movement_string += ")"
            file.write(movement_string)

    def save_pickle(self) -> None:
        '''Saves the game to a pkl in the correct pklfiles folder'''
        import pickle
        from os import chdir, getcwd, path
        wd = getcwd()
        full_path = path.join(wd, 'pklfiles')
        if not wd.endswith('pklfiles'):
            chdir(full_path)
        filename: str = ''
        while len(filename) < 1:
            text: str = "Please write the name of the file you want to save to. Do not include the file extension."
            filename: str = (sg.popup_get_text(text, title="Please Enter Text", font=('Arial Bold', 15)))
            if filename is None:
                return
        filename = path.join(full_path, f"{filename}")
        with open(f"{filename}.pkl", "wb") as pkl_file:
            backup_window: sg.Window = self.window
            backup_screen: pygame.Surface = self.screen
            backup_backup_board: pygame.Surface = self.backup_board
            del self.window
            del self.screen
            del self.backup_board
            pickle.dump(self, pkl_file)
            self.window: sg.Window = backup_window
            self.screen: pygame.Surface = backup_screen
            self.backup_board: pygame.Surface = backup_backup_board

    def load_pkl(self, inputPath) -> Type['GoBoard']:
        '''Loads the current state of the game from a pkl file.'''
        import pickle
        with open(inputPath, 'rb') as file:
            friend = pickle.load(file)
        return friend

    def refresh_board_pygame(self) -> None:
        '''Refreshes the pygame screen to show the updated board'''
        self.screen.blit(self.backup_board, (0, 0))
        for board_row in self.board:
            for item in board_row:
                # Can do it better using if... in?
                if item.stone_here_color == cf.unicode_black or item.stone_here_color == cf.unicode_white:  # this is bad, fix
                    pygame.draw.circle(self.screen, item.stone_here_color,
                                       (item.screen_row, item.screen_col), self.pygame_board_vals[2])
                elif item.stone_here_color == cf.unicode_diamond_black or item.stone_here_color == cf.unicode_diamond_white:
                    pygame.draw.circle(self.screen, item.stone_here_color,
                                       (item.screen_row, item.screen_col), self.pygame_board_vals[2])
                elif item.stone_here_color == cf.unicode_triangle_black or item.stone_here_color == cf.unicode_triangle_white:
                    pygame.draw.circle(self.screen, item.stone_here_color,
                                       (item.screen_row, item.screen_col), self.pygame_board_vals[2])
        pygame.display.update()

    def close_window(self):
        '''Closes the pygame display and PySimpleGui window'''
        import platform
        if platform.system() == "Linux":
            self.window.close()
        elif platform.system() == "Windows":
            self.window.close()
            del self.window
            del self.backup_board
            pygame.display.quit()

    def making_score_board_object(self):
        '''Creates a ScoringBoard object to handle scoring and dead stones.'''
        from scoringboard import ScoringBoard
        import platform  # Required as for some reason the code/window behaves differently between linux and windows
        self.scoring_dead = ScoringBoard(self)
        if platform.system() == "Linux":
            self.window.close()
            ui.setup_board_window_pygame(self.scoring_dead)  # Makes a window, but nothing you click will do anything
            #self.scoring_dead.refresh_board_pygame()
            winner = self.scoring_dead.dealing_with_dead_stones()
            return winner
        elif platform.system() == "Windows":
            self.close_window()
            ui.setup_board_window_pygame(self.scoring_dead)
            #self.scoring_dead.refresh_board_pygame()
            winner = self.scoring_dead.dealing_with_dead_stones()
            return winner












