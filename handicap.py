import uifunctions as ui
import PySimpleGUI as sg
import pygame
import config as cf
from typing import Tuple, List


class Handicap():
    def __init__(self, parent) -> None:
        self.go_board = parent

    # By default there should not be any handicap.
    @staticmethod
    def default_handicap() -> Tuple[bool, str, int]:
        return (False, "None", 0)

    def custom_handicap(self, defaults: bool) -> Tuple[bool, str, int]:
        if defaults:
            return (False, "None", 0)
        info: str = "Please Click Yes if you want choose where you play your handicap."
        manual_handicap: str = sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))
        choosen_list: list = self.choose_handicap_list()
        actual_handicap: bool = self.handicap_person()
        if not actual_handicap:
            return (False, "None", 0)
        handicap_value: int = ui.handicap_number_gui(self.go_board.board_size)
        if manual_handicap == "No":
            self.play_automatic_handicap(handicap_value, choosen_list)
        else:
            self.manual_handicap_placement(handicap_value)
        self.go_board.position_played_log.append(("Break between handicaps and normal play", -1, -1))
        self.go_board.turn_num = 0
        return (True, self.go_board.not_whose_turn.color, handicap_value)

    def manual_handicap_placement(self, handicap_info: int) -> None:
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

    def choose_handicap_list(self) -> List:
        handicap_points9: List[Tuple[int, int]] = [(2, 6), (6, 2), (6, 6), (2, 2), (4, 4)]
        handicap_points13: List[Tuple[int, int]] = [(3, 9), (9, 3), (9, 9), (3, 3), (6, 6), (6, 3), (6, 9), (3, 6), (9, 6)]
        handicap_points19: List[Tuple[int, int]] = [(3, 13), (13, 3), (13, 13), (3, 3), (8, 8), (8, 3), (8, 13), (3, 8), (13, 8)]
        choosen_list = handicap_points19
        if self.go_board.board_size == 9:
            choosen_list = handicap_points9
        elif self.go_board.board_size == 13:
            choosen_list = handicap_points13
        return choosen_list

    def handicap_person(self) -> bool:
        player_choice: str = ui.handicap_person_gui()
        if player_choice == "Black":
            self.go_board.whose_turn = self.go_board.player_black
            return True
        elif player_choice == "White":
            self.go_board.whose_turn = self.go_board.player_white
            return True
        else:
            return False

    def play_automatic_handicap(self, handicap_value: int, choosen_list: List[Tuple[int, int]]) -> None:
        for idx in range(handicap_value):
            row, col = choosen_list[idx]
            place = self.go_board.board[row][col]
            self.go_board.play_piece(row, col)
            pygame.draw.circle(self.go_board.screen, self.go_board.whose_turn.unicode,
                               (place.screen_row, place.screen_col), self.go_board.pygame_board_vals[2])
        self.go_board.refresh_board_pygame()
        self.go_board.switch_player()

    def validate_handicap_placement(self):
        valid_piece: bool = False
        while not valid_piece:
            event, values = self.go_board.window.read()
            while event == "Pass Turn" or event == "Save Game" or event == "Undo Turn":
                ui.def_popup("You can't do these actions during the handicap stage.", 3)
                event, values = self.go_board.window.read()
            if event == "Exit Game" or event == "Res":
                self.go_board.turn_options(event)
            row, col = values['-GRAPH-']
            found_piece, piece = self.go_board.find_piece_click([row, col])
            if found_piece:
                if piece.stone_here_color == cf.unicode_none:
                    valid_piece = found_piece
        return piece
