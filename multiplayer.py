import uifunctions as ui
import PySimpleGUI as sg
from time import sleep
import pygame
import copy
from player import Player
from handicap import Handicap
from goclasses import GoBoard, BoardNode, BoardString
import config as cf
from typing import Tuple, List, Set, Union, Literal, Type, Optional
from random import randrange


class MultiplayerBoard(GoBoard):
    def __init__(self, board_size=19, defaults=True):
        super().__init__(board_size, defaults)

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
                self.play_turn(True) #!
            elif self.whose_turn == self.player_white:
                self.play_turn(True) #!
            sleep(0.3)
        self.mode = "Scoring"
        self.times_passed = 0
        self.resuming_scoring_buffer("Scoring")
        ui.end_game_popup()
        self.scoring_block()
        
    def play_turn(self, bot: Optional[bool] = False, mp_other: Optional[bool] = False) -> None:
        self.refresh_board_pygame()  # Maybe unnecessary
        ui.update_scoring(self)
        truth_value: bool = False
        while not truth_value:
            if not mp_other:
                event, values = self.window.read()
            else:
                #event = "-GRAPH-" #! Black Box Func for now
                #mp_other catch
                
            if event != "-GRAPH-":
                #self.combined_network.send(f"{event} ")
                self.turn_options(event, text="Passed")
                if event == "Pass Turn" or event == "Res" or event == "Undo Turn":
                    return
            else:
                if not bot:
                    row, col = values['-GRAPH-']
                    found_piece, piece = self.find_piece_click([row, col])
                else: #! Black Box Func for now
                    row = randrange(0, 9)
                    col = randrange(0, 9)
                    piece = self.board[row][col]
                    found_piece = True
                #self.combined_network.send(f"{piece.row, piece.col} ")
                if found_piece:
                    if not bot:
                        truth_value = self.play_piece(piece.row, piece.col)
                    else:
                        truth_value = self.play_piece_bot(piece.row, piece.col)
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
    