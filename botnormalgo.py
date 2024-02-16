import uifunctions as ui
from goclasses import GoBoard, BoardNode
import config as cf
from random import randrange
from goclasses import diagonals_setup


class BotBoard(GoBoard):  # Need to override the scoring/removing dead pieces bit... once i finish that...
    def __init__(self, board_size=19, defaults=True):
        super().__init__(board_size, defaults)

    def playing_mode_end_of_game(self):
        from scoringboard import making_score_board_object
        winner = making_score_board_object(self)
        print(f"winner is {winner}")
        return winner  # This is a hack to manage AI training. Fix eventually.

    def turn_loop(self):
        while (self.times_passed <= 1):
            if self.whose_turn == self.player_black:
                self.play_turn()  # Change this to true if you want it to be bot vs bot
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

            if val == (self.board_size * self.board_size):
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
        self.make_turn_info()
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
        piece_diagonals = diagonals_setup(self, piece)
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
                    item_diagonals = diagonals_setup(self, item)
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
