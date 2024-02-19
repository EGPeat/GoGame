import uifunctions as ui
from goclasses import GoBoard
from random import randrange
from goclasses import play_turn_bot_helper


class BotBoard(GoBoard):
    def __init__(self, board_size=9, defaults=True):
        """
        Initializes a GoBoard instance with optional board size and default settings.

        Parameters:
            board_size (int): The size of the Go board (default is 9).
            defaults (bool): A boolean indicating whether to use default settings (default is True).

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
        """
        super().__init__(board_size, defaults)

    def playing_mode_end_of_game(self) -> bool:
        "generates a score_board object, and then does automatic scoring, returning the winner as a bool. T/1 means black won."
        from scoringboard import making_score_board_object
        winner = making_score_board_object(self)
        return winner

    def turn_loop(self) -> None:
        "Plays turns in a loop while the game is not in scoring mode."
        while (self.times_passed <= 1):
            if self.whose_turn == self.player_black:
                self.play_turn()
            elif self.whose_turn == self.player_white:
                self.play_turn_bot()

    def play_turn_bot(self) -> None:
        "Generates a random location for the bot to play, and then plays the turn."
        ui.update_scoring(self)
        truth_value: bool = False
        tries = 0
        while not truth_value:
            val = randrange(0, (self.board_size * self.board_size))
            tries += 1
            if tries >= 120:
                val = self.board_size * self.board_size

            truth_value = play_turn_bot_helper(self, truth_value, val)
            ui.refresh_board_pygame(self)
            if truth_value == "Passed":
                return
        self.make_turn_info()
        return
