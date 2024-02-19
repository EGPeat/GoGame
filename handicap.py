import uifunctions as ui
import PySimpleGUI as sg
import pygame
import config as cf
from typing import Tuple, List


class Handicap():
    def __init__(self, parent) -> None:
        '''
        Helper class that manages implementing handicaps.
        This class mostly modifies attributes of the parent (a GoBoard)
        Main things that are modified:
            GoBoard.board (playing pieces)
            GoBoard.handicap (recording the handicap values)
        '''
        from goclasses import GoBoard
        self.go_board: GoBoard = parent

    @staticmethod
    def default_handicap() -> Tuple[bool, str, int]:
        '''Default Values of False, "None", and 0'''
        return (False, "None", 0)

    def custom_handicap(self, defaults: bool) -> Tuple[bool, str, int]:
        '''Allows the players to choose a custom or manual handicap. Players can choose who gets the handicap, and how much.'''
        if defaults:
            return (False, "None", 0)
        manual_handicap, chosen_list, actual_handicap, handicap_value = self.custom_handicap_player_input()
        if not actual_handicap:
            return (False, "None", 0)
        if manual_handicap == "No":
            self.play_automatic_handicap(handicap_value, chosen_list)
        else:
            self.manual_handicap_placement(handicap_value)
        self.go_board.position_played_log.append(("Break between handicaps and normal play", -1, -1))
        self.go_board.turn_num = 0
        return (True, self.go_board.not_whose_turn.color, handicap_value)

    def custom_handicap_player_input(self) -> Tuple[str, List[Tuple[int, int]], bool, int]:
        '''
        Asks the player if they want a handicap. If they do, asks which player should have the handicap,
        If they want to place the pieces manually, and how many pieces they want as a handicap.
        If they do not want a handicap, returns ("No", [], False, -1).
        '''
        actual_handicap: bool = self.handicap_person()
        if not actual_handicap:
            return ("No", [], False, -1)
        info: str = "Please Click Yes if you want choose where you play your handicap."
        manual_handicap: str = sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))
        chosen_list: list = self.choose_handicap_list()
        handicap_value: int = ui.handicap_number_gui(self.go_board.board_size)
        return manual_handicap, chosen_list, actual_handicap, handicap_value

    def manual_handicap_placement(self, handicap_info: int) -> None:
        '''Allows the player to choose where to place their handicap pieces.'''
        ui.def_popup(f"Please place {handicap_info} number of pieces where you wish,\
                    as a handicap.Then the opponent will play.", 3)
        for _ in range(handicap_info):
            piece = self.validate_handicap_placement()
            self.go_board.times_passed = 0
            truth_value: bool = self.go_board.play_piece(piece.row, piece.col)
            if truth_value:
                pygame.draw.circle(self.go_board.screen, self.go_board.whose_turn.unicode,
                                   (piece.screen_row, piece.screen_col), self.go_board.pygame_board_vals[2])
                pygame.display.update()
        self.go_board.switch_player()

    def choose_handicap_list(self) -> List[Tuple[int, int]]:
        '''Convenience function that returns the correct list of locations for a automatic handicap.'''
        handicap_points9: List[Tuple[int, int]] = [(2, 6), (6, 2), (6, 6), (2, 2), (4, 4)]
        handicap_points13: List[Tuple[int, int]] = [(3, 9), (9, 3), (9, 9), (3, 3), (6, 6), (6, 3), (6, 9), (3, 6), (9, 6)]
        handicap_points19: List[Tuple[int, int]] = [(3, 13), (13, 3), (13, 13), (3, 3), (8, 8), (8, 3), (8, 13), (3, 8), (13, 8)]
        chosen_list = handicap_points19
        if self.go_board.board_size == 9:
            chosen_list = handicap_points9
        elif self.go_board.board_size == 13:
            chosen_list = handicap_points13
        return chosen_list

    def handicap_person(self) -> bool:
        '''Allows players to choose who gets the handicap'''
        player_choice: str = ui.handicap_person_gui()
        if player_choice == "Black":
            self.go_board.whose_turn = self.go_board.player_black
            return True
        elif player_choice == "White":
            self.go_board.whose_turn = self.go_board.player_white
            return True
        else:
            return False

    def play_automatic_handicap(self, handicap_value: int, chosen_list: List[Tuple[int, int]]) -> None:
        '''Plays the handicap in customary handicap locations defined in chosen_list.'''
        for idx in range(handicap_value):
            row, col = chosen_list[idx]
            place = self.go_board.board[row][col]
            self.go_board.play_piece(row, col)
            pygame.draw.circle(self.go_board.screen, self.go_board.whose_turn.unicode,
                               (place.screen_row, place.screen_col), self.go_board.pygame_board_vals[2])
        ui.refresh_board_pygame(self.go_board)
        self.go_board.switch_player()

    def handle_special_events(self, event):
        '''Handles special events during handicap placement.'''
        while event in ["Pass Turn", "Save Game", "Undo Turn"]:
            ui.def_popup("You can't do these actions during the handicap stage.", 3)
            event, _ = self.go_board.read_window()

    def handle_exit_or_resume(self, event) -> None:
        '''Handles Exit Game or Resume events during handicap placement.'''
        if event in ["Exit Game", "Res"]:
            from turn_options import normal_turn_options
            normal_turn_options(self.go_board, event)

    def validate_handicap_placement(self):
        '''Ensures the player chooses a valid location to place a handicap stone. Returns a BoardNode.'''
        while True:
            event, values = self.go_board.read_window()
            self.handle_special_events(event)
            self.handle_exit_or_resume(event)

            row, col = values['-GRAPH-']
            found_piece, piece = self.go_board.find_piece_click([row, col])
            if found_piece and piece.stone_here_color == cf.rgb_grey:
                return piece
