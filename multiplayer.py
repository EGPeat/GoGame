import uifunctions as ui
import PySimpleGUI as sg
import pygame
from handicap import Handicap
from network import Network
from goclasses import GoBoard
import config as cf
from typing import Tuple, List, Optional
import threading


class MultiplayerBoard(GoBoard):
    def __init__(self, password_id, ip_address=None, board_size=19, defaults=True):
        #Many of these functions need to be updated based on goclasses.py
        super().__init__(board_size, defaults)
        if ip_address:
            self.combined_network = Network(password_id, ip_address)
            self.you = self.player_white
            self.first_round = True
        else:
            self.combined_network = Network(password_id)
            self.you = self.player_black

    def play_game(self, from_file: Optional[bool] = False, fixes_handicap: Optional[bool] = False) -> None:
        '''
        This function figures out the gamemode of the board (playing, finished, scoring) and then calls the appropriate function.
        from_file: a bool representing if the board should be loaded from file
        fixes_handicap: a bool representing if a player has a handicap or not
        '''
        if self.mode == "Playing":
            self.play_game_playing_mode(from_file, fixes_handicap)
        elif self.mode == "Finished":
            self.play_game_view_endgame()
        elif from_file is True and not self.mode_change:
            self.refresh_board_pygame()
            self.scoring_block()

        else:
            self.refresh_board_pygame()
            self.mode_change = True
            self.times_passed = 0
            self.scoring_block()

    def play_game_playing_mode(self, from_file, fixes_handicap) -> None:
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
            self.refresh_board_pygame()
            if self.position_played_log[-1][0] == "Black":
                self.switch_player()
                self.play_turn(True)
        if fixes_handicap:
            hc: Handicap = Handicap(self)
            self.handicap = hc.custom_handicap(False)
        while (self.times_passed <= 1):
            if self.whose_turn == self.you:
                piece = self.play_turn(False)
                self.combined_network.send_and_recieve(piece)
                self.refresh_board_pygame()
            else:
                if self.you == self.player_white:
                    if self.first_round is True:
                        self.combined_network.first_round_op()
                        self.first_round = False
                event = self.combined_network.message_in
                self.play_turn(True, info=event)
                self.refresh_board_pygame()
        if self.you == self.player_white:
            self.first_round = True
        self.mode = "Scoring"
        self.times_passed = 0
        self.resuming_scoring_buffer("Scoring")
        ui.end_game_popup()
        self.scoring_block()

    def scoring_block(self) -> None:
        '''
        Manages the scoring phase of the game.
        This function iterates through the scoring phase, allowing players to remove dead stones.
        When the scoring is finished, it calls 'making_score_board_object()' to determine the winner.
        '''
        while self.mode != "Finished":
            if self.mode_change:
                self.switch_button_mode()
            while self.mode == "Scoring":
                if self.whose_turn == self.you:
                    piece = self.remove_dead(False)
                    self.combined_network.send_and_recieve(piece)
                    self.refresh_board_pygame()
                else:
                    if self.you == self.player_white:
                        if self.first_round is True:
                            self.combined_network.first_round_op()
                            self.first_round = False
                    event = self.combined_network.message_in
                    temp: str = self.remove_dead(True, info=event)
                    self.refresh_board_pygame()
                    if temp.count("TrueTrue") == 1:
                        self.combined_network.send_and_recieve(temp)
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

    def play_turn(self, mp_other: Optional[bool] = False, info=None) -> None:
        '''This function plays a turn by capturing info from a mouse click or the other players move and then plays the turn.'''
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
                event = info
                event_copy = info.replace(" ", "").replace("\t", "").replace("\n", "").replace("\r", "")
                event_alpha = event_copy.isalpha()

            if (event != "-GRAPH-" and not mp_other) or (mp_other and event_alpha):
                self.turn_options(event, text="Passed")
                if event == "Pass Turn" or event == "Res" or event == "Undo Turn":
                    return event
            else:
                if not mp_other:
                    row, col = values['-GRAPH-']
                    found_piece, piece = self.find_piece_click([row, col])
                else:
                    event_split = event.split()
                    row = int(event_split[0])
                    col = int(event_split[1])
                    piece = self.board[row][col]
                    found_piece = True
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
        return f"{piece.row}  {piece.col} "

    def remove_dead(self, mp_other=False, info=None) -> None:
        '''
        This function waits for player input to select dead stones, and then processes the removal of those stones.
        '''
        self.killed_last_turn.clear()
        ui.update_scoring(self)
        truth_value: bool = False
        while not truth_value:
            if info is not None:
                event = info.split(',')
                truthness = event[0]  # see if this area is an issue
                event = event[1]
                event_copy = event.replace(" ", "").replace("\t", "").replace("\n", "").replace("\r", "")
                if truthness == "False" and event == " Pass Turn ":
                    self.switch_player()
                    return "Skipped"
                if truthness == "True":
                    event_split = event.split()
                    row = int(event_split[0])
                    col = int(event_split[1])
                    piece = self.board[row][col]
                    piece_string = self.remove_dead_found_piece(piece)
                    send_value = self.get_agreement()
                    if send_value == "Yes":
                        self.remove_stones_and_update_score(piece_string)
                    self.switch_player()
                    info = None
                    return f"TrueTrue,{send_value},{row},{col}"
                elif truthness == "TrueTrue":
                    event_split = info.split(',')
                    event = event_split[1]
                    row = int(event_split[2])
                    col = int(event_split[3])
                    piece = self.board[row][col]
                    found_piece = True
                    info = None
                info = None

            if not mp_other:
                event, values = self.window.read()

            else_choice = self.remove_dead_event_handling(event)
            if not else_choice and not mp_other:  # ^^^unsure if this works right or not in general
                return f"False, {event} "

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
                    piece_string = self.remove_dead_found_piece_helper(piece)  # Might be an issue
                    self.remove_stones_and_update_score(piece_string)
                    self.switch_player()
                    return "Removed"
                if event == "No":
                    piece_string = self.remove_dead_found_piece_helper(piece)  # Might be an issue
                    self.remove_dead_undo_list(piece_string)
                    self.switch_player()
                    return "Undone"
                if not mp_other:
                    piece_string = self.remove_dead_found_piece(piece)
                    self.switch_player()
                    return f"True, {piece.row}  {piece.col} "

                self.remove_stones_and_update_score(piece_string)
                break
            self.switch_player()
        return

    def turn_options(self, event, text: Optional[str] = None) -> None:
        '''Handles various game options based on the given event.'''
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

    def remove_dead_found_piece(self, piece) -> Tuple[str, List[Tuple[Tuple[int, int], Tuple[int, int, int]]]]:
        '''
        Helper function for remove_dead().
        Uses floodfill to find all connected Nodes of the same color as the variable piece.
        '''
        from scoringboard import ScoringBoard
        series = ScoringBoard.flood_fill(piece)  # Might be an issue
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

    def remove_dead_found_piece_helper(self, piece) -> Tuple[str, List[Tuple[Tuple[int, int], Tuple[int, int, int]]]]:
        '''
        Helper function for remove_dead().
        Uses floodfill to find all connected Nodes of the same color as the variable piece.
        '''
        from scoringboard import ScoringBoard
        series = ScoringBoard.flood_fill(piece)  # Might be an issue
        piece_string: List[Tuple[Tuple[int, int], Tuple[int, int, int]]] = list()
        for item in series[0]:
            if item.stone_here_color == cf.unicode_diamond_black:
                piece_string.append(((item.row, item.col), self.player_black.unicode))

            elif item.stone_here_color == cf.unicode_diamond_white:
                piece_string.append(((item.row, item.col), self.player_white.unicode))
        self.refresh_board_pygame()
        return piece_string

    def get_agreement(self) -> str:
        '''
        Asks the player for agreement with the changes made during scoring.
        Returns the player's choice.
        '''
        info: str = "Player, please click yes if you are ok with these changes"
        other_user_agrees: str = sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))
        return other_user_agrees
