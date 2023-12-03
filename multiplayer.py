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
import select

class MultiplayerBoard(GoBoard):
    def __init__(self, password_id, ip_address=None, board_size=19, defaults=True):
        super().__init__(board_size, defaults)
        if ip_address:
            self.combined_network = Network(password_id, ip_address)
            self.you = self.player_white
        else:
            self.combined_network = Network(password_id)
            self.you = self.player_black

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
            if self.whose_turn == self.you:
                self.play_turn(True)  # !
            else:
                self.play_turn(True)  # !
                # self.play_turn(mp_other=True) #!
            sleep(0.3)
        self.mode = "Scoring"
        self.times_passed = 0
        self.resuming_scoring_buffer("Scoring")
        ui.end_game_popup()
        self.scoring_block()

    def scoring_block(self) -> None:
        while self.mode != "Finished":
            if self.mode_change:
                self.switch_button_mode()
            while self.mode == "Scoring":
                if self.whose_turn == self.you:
                    self.remove_dead()
                else:
                    self.remove_dead(True)
                if self.times_passed == 2:
                    self.mode = "Finished"
            if self.mode_change:
                if not self.mode == "Scoring":
                    self.window["Res"].update("Quit Program")
            while (self.times_passed <= 1):
                self.play_turn()
            if self.times_passed == 2 and self.mode == "Playing":
                self.mode = "Scoring"
                self.resuming_scoring_buffer("Scoring")
                self.times_passed = 0
        self.making_score_board_object()

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
                event: str = self.combined_network.recv(2048).decode()
                event_copy = event.replace(" ", "").replace("\t", "").replace("\n", "").replace("\r", "")
                event_alpha = event_copy.isalpha()

            if event != "-GRAPH-" and not mp_other:
                self.combined_network.send(f"{event} ")
                self.turn_options(event, text="Passed")
                if event == "Pass Turn" or event == "Res" or event == "Undo Turn":
                    return
            elif mp_other and event_alpha:
                self.turn_options(event, text="Passed")
                if event == "Pass Turn" or event == "Res" or event == "Undo Turn":
                    return
            else:
                if not mp_other:
                    row, col = values['-GRAPH-']
                    found_piece, piece = self.find_piece_click([row, col])
                    self.combined_network.send(f"{piece.row}  {piece.col} ")
                else:  # ! Black Box Func for now
                    event_split = event.split()
                    row = int(event_split[0])
                    col = int(event_split[1])
                    piece = self.board[row][col]
                    found_piece = True
                sleep(0.4)
                if found_piece:
                    truth_value = self.play_piece(piece.row, piece.col)
                    if truth_value:  # This should never fail from the other player....
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

    def remove_dead(self, mp_other=False) -> None:
        self.killed_last_turn.clear()
        ui.update_scoring(self)
        truth_value: bool = False
        while not truth_value:
            ready_to_read, _, _ = select.select([self.combined_network], [], [], 0.1)  # Check for socket data every 0.1 seconds

            if self.combined_network in ready_to_read:
                event: str = self.combined_network.recv(2048).decode()
                event = event.split(',')
                truthness = event[0]  # see if this area is an issue
                event = event[1]
                event_copy = event.replace(" ", "").replace("\t", "").replace("\n", "").replace("\r", "")
                if truthness == "True":
                    event_split = event.split()
                    row = int(event_split[0])
                    col = int(event_split[1])
                    piece = self.board[row][col]
                    piece_string = self.remove_dead_found_piece(piece)
                    send_value = self.get_agreement()
                    self.combined_network.send(f"False, {send_value} ")
                    self.switch_player()
                    return
            
            
            if mp_other:
                event: str = self.combined_network.recv(2048).decode()
                event = event.split(',')
                truthness = event[0]
                event = event[1]
                event_copy = event.replace(" ", "").replace("\t", "").replace("\n", "").replace("\r", "")
            else:
                event, values = self.window.read()
                

            else_choice: bool = self.remove_dead_event_handling(event)
            if not else_choice and not mp_other:  # ^^^unsure if this works right or not in general
                self.combined_network.send(f"False, {event} ")
                return

            if not mp_other:
                row, col = values['-GRAPH-']
                found_piece, piece = self.find_piece_click([row, col])
            else:
                if event == "Yes" or event == "No":
                    found_piece = True
                if event_copy.isdigit() is True:
                    event_split = event.split()
                    row = int(event_split[0])
                    col = int(event_split[1])
                    piece = self.board[row][col]
                    found_piece = True

            if found_piece and piece.stone_here_color == cf.unicode_none:
                ui.def_popup("You can't remove empty areas", 1)
            elif found_piece:
                if event == "Yes":
                    piece_string = self.remove_dead_found_piece(piece)
                    self.remove_stones_and_update_score(piece_string)
                    self.switch_player()
                    return
                if event == "No":
                    self.remove_dead_undo_list(piece_string)
                    self.switch_player()
                    return
                if not mp_other:
                    self.combined_network.send(f"True, {piece.row}  {piece.col} ")
                    piece_string = self.remove_dead_found_piece(piece)  #modify this
                    self.switch_player()
                    return

                self.remove_stones_and_update_score(piece_string)
                break
        self.switch_player()
        return

    def turn_options(self, event, text: Optional[str] = None) -> None:
        if event in (sg.WIN_CLOSED, "Res"):
            self.combined_network.send("Close Down")
            cf.server_exit_flag = True
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
            cf.server_exit_flag = True
            from main import play_game_main
            self.close_window()
            play_game_main()
            quit()
        # else:
        #    raise ValueError


    def remove_dead_found_piece(self, piece) -> Tuple[str, List[Tuple[Tuple[int, int], Tuple[int, int, int]]]]:
        series = self.flood_fill(piece)
        piece_string: List[Tuple[Tuple[int, int], Tuple[int, int, int]]] = list()
        for item in series[0]:
            if item.stone_here_color == self.player_black.unicode:
                piece_string.append(((item.row, item.col), item.stone_here_color))
                item.stone_here_color = cf.unicode_diamond_black

            else:
                piece_string.append(((item.row, item.col), item.stone_here_color))
                item.stone_here_color = cf.unicode_diamond_white
        self.refresh_board_pygame()
        return piece_string

    def get_agreement(self):
        info: str = "Player, please click yes if you are ok with these changes"
        other_user_agrees: str = sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))
        return other_user_agrees
