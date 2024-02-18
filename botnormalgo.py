import uifunctions as ui
from goclasses import GoBoard
from random import randrange
from goclasses import play_turn_bot_helper


class BotBoard(GoBoard):
    def __init__(self, board_size=19, defaults=True):
        super().__init__(board_size, defaults)

    def playing_mode_end_of_game(self):
        from scoringboard import making_score_board_object
        winner = making_score_board_object(self)
        print(f"winner is {winner}")
        return winner

    def turn_loop(self):
        while (self.times_passed <= 1):
            if self.whose_turn == self.player_black:
                self.play_turn()
            elif self.whose_turn == self.player_white:
                self.play_turn_bot()

    def play_turn_bot(self) -> None:
        ui.update_scoring(self)
        truth_value: bool = False
        tries = 0
        while not truth_value:
            val = randrange(0, (self.board_size * self.board_size))
            print(f"val is {val}")
            tries += 1
            if tries >= 120:
                val = self.board_size * self.board_size

            truth_value = play_turn_bot_helper(self, truth_value, val)
            ui.refresh_board_pygame(self)
            if truth_value == "Break":
                return
        self.make_turn_info()
        return
