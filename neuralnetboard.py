from handicap import Handicap
from goclasses import GoBoard, BoardNode, BoardString
import config as cf
from random import randrange
import PySimpleGUI as sg
import sys
from typing import Tuple, Optional, List, Set, Union, Type
from scoringboard import ScoringBoard

sys.setrecursionlimit(10000)

# Some of these functions are never used, but are editted to remove window/pygame/pysimplegui stuff
# It should be possible to remove those things from this code


class NNBoard(GoBoard):  # Need to override the scoring/removing dead pieces bit... once i finish that...
    def __init__(self, board_size=19, defaults=True):
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

    def play_game(self, from_file: Optional[bool] = False, fixes_handicap: Optional[bool] = False):
        '''
        This function figures out the gamemode of the board (playing, finished, scoring) and then calls the appropriate function.
        from_file: a bool representing if the board should be loaded from file
        fixes_handicap: a bool representing if a player has a handicap or not
        '''
        temp = self.play_game_playing_mode(from_file, fixes_handicap)
        return temp  # This is a hack to manage AI training. Fix eventually.

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
        print("Pause1. This is scoringboard stuff. Unsure if needs window or not.")
        winner = self.making_score_board_object()
        print(f"winner is {winner}")
        return (self.ai_training_info, winner)  # This is a hack to manage AI training. Fix eventually.

    def play_turn(self, bot: Optional[bool] = False) -> None:
        '''
        This function plays a turn by capturing info from a mouse click or a bot move and then plays the turn.
        bot: a bool indicating if a bot is playing this turn.
        '''
        truth_value: bool = False
        placement = None
        tries = 0
        while not truth_value:
            if bot:  # ! Black Box Func for now
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
                truth_value = self.play_piece_bot(piece.row, piece.col)
                if truth_value:
                    self.times_passed = 0
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
        truth_value: bool = False
        while not truth_value:
            event, values = self.window.read()
            else_choice: bool = self.remove_dead_event_handling(event)
            if not else_choice:
                return
            row, col = values['-GRAPH-']
            found_piece, piece = self.find_piece_click([row, col])
            if found_piece:
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

    def play_game_view_endgame(self) -> None:  # Might be wrong, requires testing.
        '''Allows the user to view a completed game'''
        event, _ = self.window.read()
        if event == "Exit Game":
            from main import play_game_main
            self.close_window()
            play_game_main()
            quit()
        elif event == sg.WIN_CLOSED:
            quit()

    def remove_dead_found_piece(self, piece: BoardNode) -> Tuple[str, List[Tuple[Tuple[int, int], Tuple[int, int, int]]]]:
        '''
        Helper function for remove_dead().
        Uses floodfill to find all connected Nodes of the same color as the variable piece.
        Gets the agreement (or disagreement) of the other player.
        '''
        series: Tuple[Set[BoardNode], Set[BoardNode]] = NNScoringBoard.flood_fill(piece)  #!
        piece_string: List[Tuple[Tuple[int, int], Tuple[int, int, int]]] = list()
        for item in series[0]:
            if item.stone_here_color == self.player_black.unicode:
                piece_string.append(((item.row, item.col), item.stone_here_color))
                item.stone_here_color = cf.unicode_diamond_black

            else:
                piece_string.append(((item.row, item.col), item.stone_here_color))
                item.stone_here_color = cf.unicode_diamond_white
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

    def remove_stones_and_update_score(self, piece_string: List[Tuple[Tuple[int, int], Tuple[int, int, int]]]) -> None:
        '''
        Helper function for remove_dead().
        Removes stones marked as dead during scoring and update player scores.
        '''
        for tpl in piece_string:
            item: BoardNode = self.board[tpl[0][0]][tpl[0][1]]
            item.stone_here_color = cf.unicode_none

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
        from main import play_game_main
        self.close_window()
        play_game_main()
        quit()

    def piece_placement(self, piece: BoardNode, row: int, col: int) -> None:
        '''Places a piece on the board and updates game state.'''
        piece.stone_here_color = self.whose_turn.unicode
        self.turn_num += 1
        self.position_played_log.append((self.whose_turn.color, row, col))

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
        self.turn_num -= 1
        self.not_whose_turn.captured -= capture_update_val
        self.switch_player()

    def making_score_board_object(self):
        '''Creates a ScoringBoard object to handle scoring and dead stones.'''
        self.scoring_dead = NNScoringBoard(self)
        winner = self.scoring_dead.dealing_with_dead_stones()
        return winner


class NNScoringBoard(ScoringBoard):
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

        self.empty_strings: List[BoardString] = list()
        self.black_strings: List[BoardString] = list()
        self.white_strings: List[BoardString] = list()

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
        #print(f"the amount is {len(self.mixed_string_for_black)} (mixed black) and {len(self.mixed_string_for_white)} (white)")
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
