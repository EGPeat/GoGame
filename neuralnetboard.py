from handicap import Handicap
from goclasses import GoBoard, BoardNode, BoardString
import config as cf
from random import randrange
import sys
from typing import Tuple, Optional, List, Set, Union, Type
from scoringboard import ScoringBoard

sys.setrecursionlimit(10000)


def choose_board_type(vs_bot: Optional[bool] = False, ai_training: Optional[bool] = False, *args):
    '''
    This function is used in the initialization of the game...
    It chooses the correct type of board (GoBoard, BotBoard) based on a set of inputs.
    Parameters:
        vs_bot: If True, play against an AI opponent.
    '''
    from botnormalgo import BotBoard
    from neuralnetboard import NNBoard
    if ai_training:
        GameBoard = NNBoard(*args)
    elif vs_bot:
        GameBoard = BotBoard(*args)
    else:
        GameBoard = GoBoard(*args)
    return GameBoard


def initializing_game(board_size: int, defaults: Optional[bool] = True,
                      fixes_handicap: Optional[bool] = False, vs_bot: Optional[bool] = False,
                      ai_training: Optional[bool] = False, no_window: Optional[bool] = False) -> None:
    '''
    Initialize a new game based on user preferences.
    Parameters:
        window: The pySimpleGui window for user interactions.
        board_size: The size of the game board.
        defaults: If True, use default settings; otherwise, allow the user to modify player names and komi.
        fixes_handicap: If True, prompt the user to modify the handicap.
        vs_bot: If True, play against an AI opponent.
    '''

    if defaults:
        game_board = choose_board_type(vs_bot, ai_training, board_size, defaults)

    if not fixes_handicap:
        if not vs_bot:  # This is a hack to manage AI training. Fix eventually.
            game_board.play_game(fixes_handicap)
        if vs_bot:   # This is a hack to manage AI training. Fix eventually.
            temp = game_board.play_game(fixes_handicap)
            return temp


class NNBoard(GoBoard):  # Need to override the scoring/removing dead pieces bit... once i finish that...
    def __init__(self, board_size=19, defaults=True):
        self.ai_training_info: List[str] = []
        self.ai_output_info: List[List[float]] = []
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
        empty_board = ''
        for _ in range(self.board_size*self.board_size):
            empty_board += '0'
        for _ in range(10):
            self.ai_training_info.append(empty_board)
        self.ai_white_board = empty_board
        self.ai_black_board = ''
        for _ in range(self.board_size*self.board_size):
            self.ai_black_board += '1'

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
                self.play_turn(True, True)  # Change this to true if you want it to be bot vs bot
            elif self.whose_turn == self.player_white:
                self.play_turn(True)

        self.mode = "Scoring"
        self.times_passed = 0  # This is a hack to manage AI training. Fix eventually.
        self.resuming_scoring_buffer("Scoring")
        winner = self.making_score_board_object()
        print(f"winner is {winner}")
        return (self.ai_training_info, winner)  # This is a hack to manage AI training. Fix eventually.

    def play_turn(self, bot: Optional[bool] = False, good_bot: Optional[bool] = False) -> None:
        '''
        This function plays a turn by capturing info from a mouse click or a bot move and then plays the turn.
        bot: a bool indicating if a bot is playing this turn.
        '''
        from nnmcst import NNMCST
        import copy
        truth_value: bool = False
        tries = 0
        while not truth_value:
            if bot:  # Rewrite this function to not use tries and be more in line with the NN
                if good_bot:
                    import cProfile
                    import pstats
                    with cProfile.Profile() as pr:
                        self.board_copy: List[BoardString] = copy.deepcopy(self.board)
                        # self.turn_nnmcst = NNMCST(self.board_copy, self.ai_training_info, self.ai_black_board,
                        #                          self.ai_white_board, 1600, (self.whose_turn, self.not_whose_turn))
                        self.turn_nnmcst = NNMCST(self.board_copy, self.ai_training_info, self.ai_black_board,
                                                  self.ai_white_board, 5, (self.whose_turn, self.not_whose_turn))
                        val, output_chances = self.turn_nnmcst.run_mcst()
                        self.ai_output_info.append(output_chances)
                        tries += 1  # Very likely unnecessary
                        stats = pstats.Stats(pr)
                        stats.sort_stats(pstats.SortKey.TIME)
                        # stats.print_stats()
                        stats.dump_stats(filename="5000x30testingv3.prof")
                    print(f"val is {val}")
                else:   # potential for a problem if the MCST output is somehow invalid?
                    val = randrange(0, (self.board_size * self.board_size))
                    tries += 1

                if self.turn_num >= 81 or tries >= 120:
                    if tries >= 120:
                        val = self.board_size * self.board_size
                    else:
                        val = randrange(0, (self.board_size*self.board_size)+1)

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
        turn_string = self.make_board_string()
        self.ai_training_info.append(turn_string)
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

    def piece_placement(self, piece: BoardNode, row: int, col: int) -> None:
        '''Places a piece on the board and updates game state.'''
        piece.stone_here_color = self.whose_turn.unicode
        self.turn_num += 1
        self.position_played_log.append((self.whose_turn.color, row, col))

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
        # print(f"the amount is {len(self.mixed_string_for_black)} (mixed black) and {len(self.mixed_string_for_white)} (white)")
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
