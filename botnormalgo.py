import uifunctions as ui
import pygame
from handicap import Handicap
from goclasses import GoBoard, BoardNode
import config as cf
from typing import Tuple, List, Optional, Set
from random import randrange
from time import sleep


class BotBoard(GoBoard):  # Need to override the scoring/removing dead pieces bit... once i finish that...
    def __init__(self, board_size=19, defaults=True):
        super().__init__(board_size, defaults)
        self.ai_training_info: List[Tuple[str, Tuple[int, int]]] = []  # Might be Tuple of placement, or maybe a string
        self.ai_info_full: Tuple[List[Tuple[str, Tuple[int, int]]], bool] = None
        # Currently there isn't any way to figure out/have the game stop...

    def play_game(self, from_file: Optional[bool] = False, fixes_handicap: Optional[bool] = False) -> None:
        '''
        This function figures out the gamemode of the board (playing, finished, scoring) and then calls the appropriate function.
        from_file: a bool representing if the board should be loaded from file
        fixes_handicap: a bool representing if a player has a handicap or not
        '''
        if self.mode == "Playing":
            self.play_game_playing_mode(from_file, fixes_handicap)
        elif self.mode == "Finished":
            self.play_game_view_endgame()
        elif from_file is True and not self.mode_change:
            self.refresh_board_pygame()
            self.scoring_block()

        else:
            self.refresh_board_pygame()
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
            self.refresh_board_pygame()
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
        self.times_passed = 0
        self.resuming_scoring_buffer("Scoring")
        # ui.end_game_popup()
        # winner = self.scoring_block()
        winner = self.making_score_board_object()
        print(f"winner is {winner}")
        sleep(5)
        self.ai_info_full = (self.ai_training_info, winner)  # !

    def play_turn(self, bot: Optional[bool] = False) -> None:
        '''
        This function plays a turn by capturing info from a mouse click or a bot move and then plays the turn.
        bot: a bool indicating if a bot is playing this turn.
        '''
        ui.update_scoring(self)
        truth_value: bool = False
        placement = None
        tries = 0
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
                    # Two different ways for managing having a pass function. Choose as you like.
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
                        pygame.draw.circle(self.screen, self.whose_turn.unicode,
                                           (piece.screen_row, piece.screen_col), self.pygame_board_vals[2])
                        pygame.display.update()
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
