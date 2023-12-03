import uifunctions as ui
import PySimpleGUI as sg
from time import sleep
import pygame
from handicap import Handicap
from network import Network
from goclasses import GoBoard
import config as cf
from typing import Tuple, List, Optional
from random import randrange
import threading


class MultiplayerBoard(GoBoard):
    def __init__(self, password_id, ip_address=None, board_size=19, defaults=True):
        super().__init__(board_size, defaults)
        if ip_address:
            self.combined_network = Network(password_id, ip_address)
        else:
            self.combined_network = Network(password_id)

    def play_game(self, fromFile: Optional[bool] = False, fixes_handicap: Optional[bool] = False) -> None:
        if self.mode == "Playing":
            self.play_game_playing_mode(fromFile, fixes_handicap)
        elif self.mode == "Finished":
            self.play_game_view_endgame()
        elif fromFile is True and not self.mode_change:
            self.refresh_board_pygame()
            self.scoring_block()

        else:
            self.refresh_board_pygame()
            self.mode_change = True
            self.times_passed = 0
            self.scoring_block()

    def play_game_playing_mode(self, fromFile, fixes_handicap) -> None:
        if not fromFile:
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
                self.play_turn(True)  # !
            elif self.whose_turn == self.player_white:
                self.play_turn(True)  # !
                # self.play_turn(mp_other=True) #!
            sleep(0.3)
        self.mode = "Scoring"
        self.times_passed = 0
        self.resuming_scoring_buffer("Scoring")
        ui.end_game_popup()
        self.scoring_block()

    def play_turn(self, bot: Optional[bool] = False, mp_other: Optional[bool] = False) -> None:

        print(f"uh oh {threading.active_count()}")
        for thread in threading.enumerate():
            print(thread.name)

        if self.combined_network.pos == "Invalid Password Issue" and threading.active_count() == 1:
            self.turn_options("Exit Game")  # It should do something else to tell it it's bad
        elif self.combined_network.pos is False:
            self.turn_options("Exit Game")  # It should do something else to tell it it's bad
        self.refresh_board_pygame()  # Maybe unnecessary
        ui.update_scoring(self)
        truth_value: bool = False
        while not truth_value:
            if not mp_other:
                event, values = self.window.read()
            else:
                event = "-GRAPH-"  # ! Black Box Func for now
                # mp_other catch

            if event != "-GRAPH-":
                # self.combined_network.send(f"{event} ")
                self.turn_options(event, text="Passed")
                print("eee222")
                if event == "Pass Turn" or event == "Res" or event == "Undo Turn":
                    return
            else:
                if not bot:
                    row, col = values['-GRAPH-']
                    found_piece, piece = self.find_piece_click([row, col])
                else:  # ! Black Box Func for now
                    row = randrange(0, 9)
                    col = randrange(0, 9)
                    piece = self.board[row][col]
                    found_piece = True
                self.combined_network.send(f"{piece.row}, {piece.col} ")
                sleep(0.4)
                if found_piece:
                    if not bot:
                        truth_value = self.play_piece(piece.row, piece.col)
                    else:
                        truth_value = self.play_piece(piece.row, piece.col)
                    if truth_value:
                        self.times_passed = 0
                        pygame.draw.circle(self.screen, self.whose_turn.unicode,
                                           (piece.screen_row, piece.screen_col), self.pygame_board_vals[2])
                        pygame.display.update()
        temp_list: List[Tuple[Tuple[int, int, int], int, int]] = list()
        for item in self.killed_last_turn:
            temp_list.append((self.not_whose_turn.unicode, item.row, item.col))
        self.killed_log.append(temp_list)
        self.switch_player()
        return

    def remove_dead(self) -> None:
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

    def turn_options(self, event, text: Optional[str] = None) -> None:
        if event in (sg.WIN_CLOSED, "Res"):
            self.combined_network.send("Close Down")
            quit()
        if event == "Pass Turn":
            ui.def_popup("Skipped turn", 0.5)
            self.times_passed += 1
            self.turn_num += 1
            self.position_played_log.append((text, -3, -3))
            self.killed_log.append([])
            self.switch_player()
        elif event == "Save Game":
            self.save_pickle()
        elif event == "Undo Turn":
            if self.turn_num == 0:
                ui.def_popup("You can't undo when nothing has happened.", 2)
            elif self.turn_num >= 1:
                self.undo_checker()
                return
        elif event == "Exit Game":
            self.combined_network.send("Close Down")
            from main import play_game_main
            self.close_window()
            play_game_main()
            quit()
        # else:
        #    raise ValueError
