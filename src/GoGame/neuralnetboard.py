from GoGame.handicap import Handicap
from GoGame.goclasses import GoBoard, BoardNode, BoardString
import sys
from typing import Tuple, Optional, List, Set, Union, Type
from GoGame.scoringboard import ScoringBoard
from GoGame.goclasses import play_turn_bot_helper

sys.setrecursionlimit(10000)


def initializing_game(nn, nn_bad, board_size: int, defaults: Optional[bool] = True) -> None:
    '''
    Initialize a new game based on user preferences.
    Parameters:
        board_size: The size of the game board.
        defaults: If True, use default settings; otherwise, allow the user to modify player names and komi.
        nn: current neural net
        nn_bad: second neural net, with worse weights
    '''
    game_board = NNBoard(nn, nn_bad, board_size, defaults)
    return game_board.play_game(False)


class NNBoard(GoBoard):
    def __init__(self, nn, nn_bad, board_size=9, defaults=True):
        """
        Initializes a NNBoard instance with optional board size and default settings.

        Parameters:
            board_size (int): The size of the Go board (default is 9).
            defaults (bool): A boolean indicating whether to use default settings (default is True).
            nn : neural_net model built using keras.
            nn_bad : Either a copy of nn, or a older version of nn with worse weights.

        Attributes:
            defaults (bool): Indicates whether default settings are applied.
            board_size (int): The size of the Go board.
            board (List[List[BoardNode]]): 2D list representing the Go board with BoardNode instances.
            times_passed (int): Number of consecutive passes in the game.
            turn_num (int): Current turn number.
            position_played_log (List[Union[str, Tuple[str, int, int]]]):
                Log of played positions in the format (person who played, row, col).
            visit_kill (Set[BoardNode]): Set of BoardNode instances representing visited and killed stones.
            killed_last_turn (Set[BoardNode]): Set of BoardNode instances representing stones killed in the last turn.
            killed_log (List[List[Union[Tuple[Tuple[int, int, int], int, int], List[None]]]]): Log of killed stones.
            mode (str): Current mode of the game (e.g., "Playing", "Scoring").
            mode_change (bool): Boolean indicating whether there was a change in the game mode.
            handicap (Tuple[bool, str, int]): Tuple representing handicap settings, with default being False, None, and 0.
            window (sg.Window): PySimpleGui window for the Go board.
            screen (pygame.Surface): Pygame surface for rendering the Go board.
            backup_board (pygame.Surface): Backup of the Pygame surface.
            pygame_board_vals: Tuple containing Pygame board values (workable_area, distance, circle_radius).
        Unique Attributes:
            ai_training_info List[str]: list of string representation of the board at that instance
            ai_output_info List[List[float]]: list of policy outputs at each turn.
                Policy output means the likelihood of choosing to play in a location.
        """
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
        self.nn = self.nn
        self.nn_bad = self.nn_bad

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
        return temp

    def playing_mode_end_of_game(self) -> bool:
        """
        Calculates the winner for each game by using the ScoringBoard module.
        Data is then saved to saved_self_play.json.
        Returns a bool indicating who won, with True means black won.
        """
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

        return winner

    def turn_loop(self):
        '''
        Makes the turn_loop functionality for the neuralnetboard, playing until both players pass consecutively.
        '''
        while (self.times_passed <= 1):
            if self.whose_turn == self.player_black:
                self.play_turn(True)
            elif self.whose_turn == self.player_white:
                self.play_turn(True)

    def play_turn(self, good_bot: Optional[bool] = False) -> None:
        '''
        This function plays a turn by capturing info from a mouse click or a bot move and then plays the turn.
        bot: a bool indicating if a bot is playing this turn.
        '''
        from GoGame.nnmcst import NNMCST
        import copy
        truth_value: bool = False
        while not truth_value:
            self.board_copy: List[BoardString] = copy.deepcopy(self.board)
            self.print_board()
            import time
            t0 = time.time()
            self.turn_loop
            if good_bot:
                self.turn_nnmcst = NNMCST(self.board_copy, self.ai_training_info, self.ai_black_board,
                                          self.ai_white_board, 25, (self.whose_turn, self.not_whose_turn),
                                          self.nn, self.turn_num)
            else:
                self.turn_nnmcst = NNMCST(self.board_copy, self.ai_training_info, self.ai_black_board,
                                          self.ai_white_board, 25, (self.whose_turn, self.not_whose_turn),
                                          self.nn_bad, self.turn_num)
            val, output_chances, formatted_ai_training_info = self.turn_nnmcst.run_mcst()
            self.ai_output_info.append(tuple((formatted_ai_training_info, output_chances)))
            t1 = time.time()
            print(f"the times is {t1-t0}")
            print(f"val is {val}, pos is {val//9}, {val%9} and turn is {self.turn_num}")

            truth_value = play_turn_bot_helper(self, truth_value, val)
            if truth_value == "Break":
                return
        self.make_turn_info()
        return

    def make_turn_info(self) -> None:
        '''
        Appends information to killed_log, adds the current board to ai_training_info,
        and switches the whose_turn/not_whose_turn values.
        '''
        temp_list: List[Tuple[Tuple[int, int, int], int, int]] = list()
        for item in self.killed_last_turn:
            temp_list.append((self.not_whose_turn.unicode, item.row, item.col))
        self.killed_log.append(temp_list)
        turn_string = self.make_board_string()
        self.ai_training_info.append(turn_string)
        self.switch_player()

    def print_board(self):
        '''Prints the board to the terminal.'''
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

    def making_score_board_object(self):
        '''Creates a ScoringBoard object to handle scoring and dead stones.'''
        self.scoring_dead = NNScoringBoard(self)
        winner = self.scoring_dead.dealing_with_dead_stones()
        return winner


class NNScoringBoard(ScoringBoard):
    def __init__(self, parent_obj: Type[GoBoard]) -> None:
        """
        Initializes a NNScoringBoard instance as a subclass of ScoringBoard for handling neural net scoring-related attributes.

        Parameters:
        - parent_obj (Type[GoBoard]): An instance of the parent GoBoard class.

        Attributes:
        - parent: An instance of the parent GoBoard class.
        - defaults: A boolean indicating whether default settings are used from the parent GoBoard.
        - board_size: An integer representing the size of the board inherited from the parent GoBoard.
        - board: 2D list representing the current state of the board with BoardNode instances.
        - times_passed: Number of consecutive passes during the game.
        - turn_num: Number of turns played.
        - position_played_log: List containing information about positions played during the game.
        - visit_kill: Set of BoardNode instances representing visited and killed stones.
        - killed_last_turn: Set of BoardNode instances killed in the last turn.
        - killed_log: List containing information about stones killed during the game.
        - mode: A string representing the current mode of the game.
        - mode_change: A boolean indicating whether the mode of the game has changed.
        - handicap: Tuple representing the handicap settings.
        - pygame_board_vals: Tuple containing values for Pygame board rendering.
        - empty_strings: List of BoardString instances representing empty areas on the board.
        - black_strings: List of BoardString instances representing areas controlled by the black player.
        - white_strings: List of BoardString instances representing areas controlled by the white player.
        """
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
