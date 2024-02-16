from handicap import Handicap
from goclasses import GoBoard, BoardNode, BoardString
import sys
from typing import Tuple, Optional, List, Set, Union, Type
from scoringboard import ScoringBoard
from goclasses import play_turn_bot_helper

sys.setrecursionlimit(10000)


def initializing_game(board_size: int, defaults: Optional[bool] = True) -> None:
    '''
    Initialize a new game based on user preferences.
    Parameters:
        board_size: The size of the game board.
        defaults: If True, use default settings; otherwise, allow the user to modify player names and komi.
    '''
    game_board = NNBoard(board_size, defaults)
    return game_board.play_game(False)


class NNBoard(GoBoard):  # Need to override the scoring/removing dead pieces bit... once i finish that...
    # I need to inherit the BotBoard class, which will then allow me to just use the BotBoard functions for...
    # parts of play_turn, fills_eyes, play_piece_bot, diagonal_setup
    def __init__(self, board_size=19, defaults=True):
        self.ai_training_info: List[str] = []
        self.ai_output_info: List[List[float]] = []
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
        from neuralnet import nn_model
        self.nn = nn_model()
        self.nn_bad = self.nn  # This is a temp thing until I have a bad model to use

    def play_game(self, from_file: Optional[bool] = False, fixes_handicap: Optional[bool] = False):
        '''
        This function figures out the gamemode of the board (playing, finished, scoring) and then calls the appropriate function.
        from_file: a bool representing if the board should be loaded from file
        fixes_handicap: a bool representing if a player has a handicap or not
        '''
        empty_board = ''
        for _ in range(self.board_size * self.board_size):
            empty_board += '0'
        for _ in range(10):
            self.ai_training_info.append(empty_board)
        self.ai_white_board = empty_board
        self.ai_black_board = ''
        for _ in range(self.board_size * self.board_size):
            self.ai_black_board += '1'

        temp = self.play_game_playing_mode(from_file, fixes_handicap)
        return temp  # This is a hack to manage AI training. Fix eventually.

    def playing_mode_end_of_game(self):
        winner = self.making_score_board_object()
        print(f"winner is {winner}")
        import json

        file_name = 'saved_self_play.json'
        try:
            with open(file_name, "r") as fn2:
                existing_data = json.load(fn2)
        except FileNotFoundError:
            existing_data = []
        new_data = []
        for item in self.ai_output_info:
            new_data.append(tuple((item[0], item[1], winner)))
        updated_data = existing_data + new_data
        with open(file_name, "w") as fn2:
            json.dump(updated_data, fn2)

        return winner  # This is a hack to manage AI training. Fix eventually.

    def turn_loop(self):
        while (self.times_passed <= 1):
            if self.whose_turn == self.player_black:
                self.play_turn(True)  # Change this to true if you want it to be bot vs bot
            elif self.whose_turn == self.player_white:
                self.play_turn(True)  # This is in self-play mode

    def play_turn(self, good_bot: Optional[bool] = False) -> None:
        '''
        This function plays a turn by capturing info from a mouse click or a bot move and then plays the turn.
        bot: a bool indicating if a bot is playing this turn.
        '''
        from nnmcst import NNMCST
        import copy
        truth_value: bool = False
        while not truth_value:
            self.board_copy: List[BoardString] = copy.deepcopy(self.board)
            self.print_board()
            import time
            t0 = time.time()
            if good_bot:
                self.turn_nnmcst = NNMCST(self.board_copy, self.ai_training_info, self.ai_black_board,
                                          self.ai_white_board, 16, (self.whose_turn, self.not_whose_turn), self.nn)
            else:
                self.turn_nnmcst = NNMCST(self.board_copy, self.ai_training_info, self.ai_black_board,
                                          self.ai_white_board, 16, (self.whose_turn, self.not_whose_turn), self.nn_bad)

            val, output_chances, formatted_ai_training_info = self.turn_nnmcst.run_mcst()
            self.ai_output_info.append(tuple((formatted_ai_training_info, output_chances)))
            t1 = time.time()
            print(f"the times is {t1-t0}")
            print(f"val is {val}, pos is {val//9}, {val%9} and turn is {self.turn_num}")
            # Why is it doing things column first...

            truth_value = play_turn_bot_helper(self, val)
            if truth_value == "Break":
                return
        self.make_turn_info()
        return

    def make_turn_info(self):
        temp_list: List[Tuple[Tuple[int, int, int], int, int]] = list()
        for item in self.killed_last_turn:
            temp_list.append((self.not_whose_turn.unicode, item.row, item.col))
        self.killed_log.append(temp_list)
        turn_string = self.make_board_string()
        self.ai_training_info.append(turn_string)
        self.switch_player()

    def print_board(self):
        print_board = self.ai_training_info[-1]
        for idx in range(9):
            temp = print_board[(idx * 9 + 1):(idx * 9 + 10)]
            temp_emoji = str()
            for idx in range(len(temp)):
                if temp[idx] == '1':
                    temp_emoji += '\u26AB'
                elif temp[idx] == '2':
                    temp_emoji += '\u26AA'
                else:
                    temp_emoji += "\u26D4"
            print(temp_emoji)

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
        self.position_played_log: List[Union[str, Tuple[str, int, int]]] = self.parent.position_played_log
        self.visit_kill: Set[BoardNode] = self.parent.visit_kill
        self.killed_last_turn: Set[BoardNode] = self.parent.killed_last_turn
        self.killed_log: List[List[Union[Tuple[Tuple[int, int, int], int, int], List[None]]]] = self.parent.killed_log

        # Mode and handicap attributes
        self.mode: str = self.parent.mode
        self.mode_change: bool = self.parent.mode_change
        self.handicap: Tuple[bool, str, int] = self.parent.handicap

        self.empty_strings: List[BoardString] = list()
        self.black_strings: List[BoardString] = list()
        self.white_strings: List[BoardString] = list()
