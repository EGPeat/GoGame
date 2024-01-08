import uifunctions as ui
import PySimpleGUI as sg
import math
import pygame
import sys
from player import Player
from handicap import Handicap

import config as cf
from typing import Tuple, Optional, List, Set, Union


sys.setrecursionlimit(10000)


def choose_board_type(vs_bot: Optional[bool] = False,
                      vs_other_person: Optional[bool] = False,
                      password: Optional[int] = 13,
                      ip_address: Optional[str] = None, *args):
    from botnormalgo import BotBoard
    from multiplayer import MultiplayerBoard
    if vs_bot:
        GameBoard = BotBoard(*args)
    elif vs_other_person:
        if ip_address:
            GameBoard = MultiplayerBoard(password, ip_address, *args)
        else:
            GameBoard = MultiplayerBoard(password, None, *args)
    else:
        GameBoard = GoBoard(*args)
    return GameBoard


def initializing_game(window, board_size: int, defaults: Optional[bool] = True,
                      fixes_handicap: Optional[bool] = False, vs_bot: Optional[bool] = False,
                      vs_other_person: Optional[bool] = False,
                      password: Optional[int] = 13, ip_address: Optional[str] = None) -> None:

    info: str = "Click yes if you want to modify the player names and komi"
    if not defaults:
        only_modify_name: str = (sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15)))
        if only_modify_name == "No":
            GameBoard = choose_board_type(vs_bot, vs_other_person, password, ip_address, board_size, True)
        else:
            GameBoard = choose_board_type(vs_bot, vs_other_person, password, ip_address, board_size, defaults)

    else:
        GameBoard = choose_board_type(vs_bot, vs_other_person, password, ip_address, board_size, defaults)

    window.close()
    ui.setup_board_window_pygame(GameBoard)
    info: str = "Click yes if you want to modify the handicap"
    if fixes_handicap:
        modify_handicap: str = (sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15)))
        if modify_handicap == "Yes":
            GameBoard.play_game(fixes_handicap=True)
        else:
            GameBoard.play_game(fixes_handicap=False)

    else:
        GameBoard.play_game(fixes_handicap)


class BoardNode():
    def __init__(self, row_value: Optional[int] = None, col_value: Optional[int] = None):
        self.row: int = row_value
        self.col: int = col_value
        self.screen_row: float = None
        self.screen_col: float = None
        self.stone_here_color: Tuple[int, int, int] = cf.unicode_none
        self.connections: Set[BoardNode] = set()

    def __str__(self) -> str:
        return (f"This is a BoardNode with coordinates of ({self.col},{self.row}) and a stone of {self.stone_here_color}")


class BoardString():
    def __init__(self, color: str, member_set: Set[BoardNode]) -> None:
        self.color: str = color
        self.member_set: Set[BoardNode] = member_set
        self.list_idx: List[Tuple[int, int]] = self.make_list_idx(member_set)
        self.list_values: List[Tuple[int, int, Tuple[int, int, int]]] = self.make_list_values(member_set)

    def __str__(self) -> str:
        return (f"this is a board string of color {self.color} and with len of {len(self.list_idx)} and values {self.list_idx}\
             and a xmax and xmin of {self.xmax, self.xmin}, and a ymax and ymin of {self.ymax, self.ymin}")

    def make_list_idx(self, set_objects: Set[BoardNode]) -> List[Tuple[int, int]]:
        from operator import itemgetter
        sorting_list: List[Tuple[int, int]] = []
        for item in set_objects:
            sorting_list.append((item.col, item.row))
        sorting_list.sort(key=lambda item: (item[0], item[1]))
        self.xmax: int = sorting_list[-1][0]
        self.xmin: int = sorting_list[0][0]
        self.ymax: int = max(sorting_list, key=itemgetter(1))[1]
        self.ymin: int = min(sorting_list, key=itemgetter(1))[1]
        return sorting_list

    def make_list_values(self, set_objects: Set[BoardNode]) -> List[Tuple[int, int, Tuple[int, int, int]]]:
        sorting_list: List[Tuple[int, int]] = []
        for item in set_objects:
            sorting_list.append((item.col, item.row, (item.stone_here_color)))
        sorting_list.sort(key=lambda item: (item[0], item[1]))
        return sorting_list


class GoBoard():
    def __init__(self, board_size=19, defaults=True):
        self.board_size: int = board_size
        self.defaults: bool = defaults
        self.board: List[List[BoardNode]] = self.setup_board()
        self.player_black: Player = Player.setup_player(self.defaults, "Player One", "Black", cf.unicode_black)
        self.player_white: Player = Player.setup_player(self.defaults, "Player Two", "White", cf.unicode_white)
        self.whose_turn: Player = self.player_black
        self.not_whose_turn: Player = self.player_white
        self.times_passed: int = 0
        self.turn_num: int = 0
        PPL_Type = List[Union[str, Tuple[str, int, int]]]
        self.position_played_log: PPL_Type = list()
        self.visit_kill: Set[BoardNode] = set()
        self.killed_last_turn: Set[BoardNode] = set()
        KL_Type = List[List[Union[Tuple[Tuple[int, int, int], int, int], List[None]]]]
        self.killed_log: KL_Type = list()
        self.mode: str = "Playing"
        self.mode_change: bool = True
        self.handicap: Tuple[bool, str, int] = Handicap.default_handicap()
        self.window: sg.Window = None
        self.screen: pygame.Surface = None
        self.backup_board: pygame.Surface = None
        self.pygame_board_vals: Tuple[int, float, float] = None  # (workable_area, distance, circle_radius)

    def make_board_string(self) -> List[str]:   # Target of optimization
        # It needs to add in the turn choice made somehow.
        board_string: str = ''
        if self.whose_turn == self.player_black:
            board_string += '1'
        else:
            board_string += '2'
        for xidx in range(len(self.board)):
            for yidx in range(len(self.board)):
                if self.board[yidx][xidx].stone_here_color == cf.unicode_none:
                    board_string += "0"
                elif self.board[yidx][xidx].stone_here_color == cf.unicode_black:
                    board_string += '1'
                else:
                    board_string += '2'
        return board_string

    def setup_board(self) -> List[List[BoardNode]]:
        board: List[List[BoardNode]] = [[BoardNode(row, col) for col in range(self.board_size)] for row in range(self.board_size)]
        for node in board:
            for item in node:
                workable_area: int = 620 / (self.board_size - 1)
                item.screen_row: float = 40 + workable_area * item.row
                item.screen_col: float = 40 + workable_area * item.col
                friends: List[Tuple[int, int]] = self.check_neighbors(item)
                for place in friends:
                    item.connections.add(board[place[0]][place[1]])
        return board

    def switch_player(self) -> None:
        if self.whose_turn == self.player_black:
            self.whose_turn = self.player_white
            self.not_whose_turn = self.player_black
        else:
            self.whose_turn = self.player_black
            self.not_whose_turn = self.player_white

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
                self.play_turn()
        if fixes_handicap:
            hc: Handicap = Handicap(self)
            self.handicap = hc.custom_handicap(False)
        while (self.times_passed <= 1):
            self.play_turn()
        self.mode = "Scoring"
        self.times_passed = 0
        self.resuming_scoring_buffer("Scoring")
        ui.end_game_popup()
        self.scoring_block()

    def play_game_view_endgame(self) -> None:
        self.refresh_board_pygame()
        event, _ = self.window.read()
        if event == "Exit Game":
            from main import play_game_main
            self.close_window()
            play_game_main()
            quit()
        elif event == sg.WIN_CLOSED:
            quit()

    def switch_button_mode(self) -> None:
        if self.mode == "Scoring":
            self.window["Res"].update("Resume Game")
            self.times_passed = 0
        elif self.mode == "Playing":
            self.window["Res"].update("Quit Program")
        self.mode_change = False

    def scoring_block(self) -> bool:
        while self.mode != "Finished":
            if self.mode_change:
                self.switch_button_mode()
            while self.mode == "Scoring":
                self.remove_dead()
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
        winner = self.making_score_board_object()
        return winner

    def resuming_scoring_buffer(self, text) -> None:
        self.turn_num += 1
        self.position_played_log.append(text)
        self.killed_log.append([])

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

    def remove_stones_and_update_score(self, piece_string: List[Tuple[Tuple[int, int], Tuple[int, int, int]]]) -> None:
        for tpl in piece_string:
            item: BoardNode = self.board[tpl[0][0]][tpl[0][1]]
            item.stone_here_color = cf.unicode_none

        self.refresh_board_pygame()
        captured_count: int = len(piece_string)
        self.player_white.captured += captured_count if piece_string[0][1] == self.player_black.unicode else 0
        self.player_black.captured += captured_count if piece_string[0][1] == self.player_white.unicode else 0

        temp_list: List[Tuple[Tuple[int, int, int], int, int, str]] = list()
        for item in piece_string:
            temp_list.append((item[1], item[0][0], item[0][1], "Scoring"))

        self.killed_log.append(temp_list)
        self.position_played_log.append("Dead Removed")
        self.turn_num += 1

    def remove_dead_found_piece(self, piece: BoardNode) -> Tuple[str, List[Tuple[Tuple[int, int], Tuple[int, int, int]]]]:
        from scoringboard import ScoringBoard
        series: Tuple[Set[BoardNode], Set[BoardNode]] = ScoringBoard.flood_fill(piece)  # !
        piece_string: List[Tuple[Tuple[int, int], Tuple[int, int, int]]] = list()
        for item in series[0]:
            if item.stone_here_color == self.player_black.unicode:
                piece_string.append(((item.row, item.col), item.stone_here_color))
                item.stone_here_color = cf.unicode_diamond_black

            else:
                piece_string.append(((item.row, item.col), item.stone_here_color))
                item.stone_here_color = cf.unicode_diamond_white
        self.refresh_board_pygame()
        info: str = "Other player, please click yes if you are ok with these changes"
        other_user_agrees: str = sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))
        return other_user_agrees, piece_string

    def remove_dead_undo_list(self, piece_string: List[Tuple[Tuple[int, int], Tuple[int, int, int]]]) -> None:
        for tpl in piece_string:
            item: BoardNode = self.board[tpl[0][0]][tpl[0][1]]
            if item.stone_here_color == cf.unicode_diamond_black:
                item.stone_here_color = self.player_black.unicode
            elif item.stone_here_color == cf.unicode_diamond_white:
                item.stone_here_color = self.player_white.unicode
        self.refresh_board_pygame()

    def end_of_game(self) -> None:
        ui.end_game_popup_two(self)
        ui.default_popup_no_button("Please save to a file, thank you.", 3)
        self.save_pickle()
        from main import play_game_main
        self.close_window()
        play_game_main()
        quit()

    def find_piece_click(self, input_location: Tuple[float, float]) -> Tuple[bool, Union[List[int], BoardNode]]:
        for item_row in self.board:
            for item in item_row:
                item_location = [item.screen_row, item.screen_col]
                if math.dist(input_location, item_location) <= self.pygame_board_vals[2]:
                    return True, item
        return False, [-1, -1]

    def play_turn(self) -> None:
        ui.update_scoring(self)
        truth_value: bool = False
        while not truth_value:
            event, values = self.window.read()
            if event != "-GRAPH-":
                self.turn_options(event, text="Passed")
                if event == "Pass Turn" or event == "Res" or event == "Undo Turn":
                    return
            else:
                row, col = values['-GRAPH-']
                found_piece, piece = self.find_piece_click([row, col])
                if found_piece:
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

    def turn_options(self, event, text: Optional[str] = None) -> None:
        if event in (sg.WIN_CLOSED, "Res"):
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
            from main import play_game_main
            self.close_window()
            play_game_main()
            quit()
        else:
            raise ValueError

    def remove_dead_event_handling(self, event) -> None:
        if event == "Pass Turn":
            self.turn_options(event, text="Scoring Passed")
            return
        elif event == "Save Game":
            self.save_pickle()
        elif event == "Res":
            self.mode = "Playing"
            self.mode_change = True
            self.resuming_scoring_buffer("Resumed")
            return
        elif event == "Undo Turn":
            self.turn_options(event)
            return
        elif event == "Exit Game":
            from main import play_game_main
            self.close_window()
            play_game_main()
            quit()
        elif event == sg.WIN_CLOSED:
            quit()
        else:
            return True

    def play_piece(self, row: int, col: int) -> bool:
        piece: BoardNode = self.board[row][col]
        if (piece.stone_here_color != cf.unicode_none):
            ui.def_popup("You tried to place where there is already a piece. Please try your turn again.", 2)
            return False
        elif (self.turn_num > 2 and self.ko_rule_break(piece) is True):
            ui.def_popup("Place the piece there would break the ko rule. Please try your turn again.", 2)
            return False
        elif (self.kill_stones(piece) is True):
            self.piece_placement(piece, row, col)
            return True
        elif (self.self_death_rule(piece, self.whose_turn) == 0):
            ui.def_popup("Place the piece there would break the self death rule. Please try your turn again.", 2)
            return False
        else:
            self.piece_placement(piece, row, col)
            self.killed_last_turn.clear()
            return True

    def piece_placement(self, piece: BoardNode, row: int, col: int) -> None:
        piece.stone_here_color = self.whose_turn.unicode
        self.turn_num += 1
        self.position_played_log.append((self.whose_turn.color, row, col))
        self.refresh_board_pygame()

    def undo_checker(self) -> None:
        if self.mode == "Scoring":
            self.undo_turn(scoring=True)
        else:
            self.undo_turn()

    def undo_turn(self, scoring: Optional[bool] = False) -> None:
        if self.undo_special_cases():
            return
        if not scoring:
            _, row, col = self.position_played_log.pop()
            self.board[row][col].stone_here_color = cf.unicode_none
        else:
            self.position_played_log.pop()
        # This part reverts the board back to its state 1 turn ago
        revive = self.killed_log.pop()
        capture_update_val: int = len(revive)

        if len(revive) > 0:
            unicode: Tuple[int, int, int] = revive[0][0]
        else:
            unicode: Tuple[int, int, int] = cf.unicode_none
        for item in revive:
            if not scoring:
                unicode, row, col = item
            else:
                unicode, row, col, scoring = item
            place: BoardNode = self.board[row][col]
            place.stone_here_color = unicode
        self.refresh_board_pygame()
        self.turn_num -= 1
        self.not_whose_turn.captured -= capture_update_val
        self.switch_player()

    def undo_special_cases(self) -> bool:
        last_entry: str = self.position_played_log[-1]

        if last_entry == "Resumed" or last_entry == "Scoring":
            tmp: str = self.position_played_log.pop()
            self.move_back()
            self.turn_num -= 1
            self.mode_change = True

            if tmp == "Resumed":
                self.mode = "Scoring"
                self.times_passed = 2
            elif tmp == "Scoring":
                self.mode = "Playing"
            return True

        if last_entry[0] in {"Passed", "Scoring Passed"}:
            self.position_played_log.pop()
            self.move_back()
            self.turn_num -= 1
            self.times_passed = 0

            if self.position_played_log and self.position_played_log[-1][0] in {"Passed", "Scoring Passed"}:
                self.times_passed = 1

            self.switch_player()
            return True
        return False

    def move_back(self) -> None:
        if len(self.killed_log) > 0:
            self.killed_last_turn.clear()
            temp_list = self.killed_log.pop()
            for item in temp_list:
                temp_node = BoardNode(row_value=item[1], col_value=item[2])
                self.killed_last_turn.add(temp_node)

    def ko_rule_break(self, piece: BoardNode) -> bool:  # no superko, but if it becomes a problem...
        if self.self_death_rule(piece, self.whose_turn) > 0:
            return False
        if piece in self.killed_last_turn:
            return True
        return False

    # Takes in a boardNode, returns a list of tuples of coordinates
    def check_neighbors(self, piece) -> List[Tuple[int, int]]:
        neighbors = [(piece.row - 1, piece.col), (piece.row + 1, piece.col),
                     (piece.row, piece.col - 1), (piece.row, piece.col + 1)]
        valid_neighbors: List[Tuple[int, int]] = []
        for coordinate in neighbors:
            if 0 <= coordinate[0] < self.board_size and 0 <= coordinate[1] < self.board_size:
                valid_neighbors.append(coordinate)
        return valid_neighbors

    # Uses BFS to figure out liberties and connected pieces of the same type
    def self_death_rule(self, piece: BoardNode, which_player: Player, visited: Optional[Set[BoardNode]] = None) -> int:
        if visited is None:
            visited: Set[BoardNode] = set()
        visited.add(piece)
        neighboring_piece: Set[BoardNode] = piece.connections
        liberties: int = 0
        for neighbor in neighboring_piece:
            if neighbor.stone_here_color == cf.unicode_none and neighbor not in visited:
                liberties += 1
            elif neighbor.stone_here_color != which_player.unicode:
                pass
            elif neighbor not in visited:
                liberties += self.self_death_rule(neighbor, which_player, visited)
        self.visit_kill = visited
        return liberties

    def remove_stones(self) -> None:
        self.killed_last_turn.clear()
        for position in self.visit_kill:
            self.killed_last_turn.add(position)
            self.whose_turn.captured += 1
            position.stone_here_color = cf.unicode_none

    def kill_stones(self, piece: BoardNode) -> bool:  # needs to return true if it does kill stones
        piece.stone_here_color: Tuple[int, int, int] = self.whose_turn.unicode
        neighboring_pieces: Set[BoardNode] = piece.connections
        truth_value: bool = False
        for neighbor in neighboring_pieces:
            if neighbor.stone_here_color == self.not_whose_turn.unicode:
                if (self.self_death_rule(neighbor, self.not_whose_turn) == 0):
                    self.remove_stones()
                    truth_value = True
        if truth_value is False:
            piece.stone_here_color = cf.unicode_none
        return truth_value

    def save_to_SGF(self, filename2: str) -> None:
        with open(f"{filename2}.sgf", 'w', encoding='utf-8') as file:
            from datetime import date
            seqs = ["Dead Removed", "Break between handicaps and normal play", "Dead Removed",
                    "Resumed", "Scoring", "Scoring Passed"]
            movement_string: str = ""
            today = date.today()
            header: str = f"(;\nFF[4]\nCA[UTF-8]\nGM[1]\nDT[{today}]\nGN[relaxed]\n\
            PC[https://github.com/EGPeat/GoGame]\n\
            PB[{self.player_black.name}]\n\
            PW[{self.player_white.name}]\n\
            BR[Unknown]\nWR[Unknown]\n\
            OT[Error: time control missing]\nRE[?]\n\
            SZ[{self.board_size}]\nKM[{self.player_white.komi}]\nRU[Japanese];"
            file.write(header)
            handicap_flag: bool = self.handicap[0]
            for idx, item in enumerate(self.position_played_log):
                if handicap_flag and idx < self.handicap[2]:
                    color: str = 'B' if self.handicap[1] == "Black" else 'W'
                    row: str = chr(97 + int(item[1]))
                    col: str = chr(97 + int(item[2]))
                    text: str = f";{color}[{col}{row}]\n"
                    movement_string += text
                elif item[0] in seqs or item in seqs:
                    pass
                elif item[0] == "Passed":
                    if movement_string[-7] == "B" or movement_string[-5] == "B":
                        text2: str = ";W[]\n"
                    else:
                        text2: str = ";B[]\n"
                    movement_string += text2
                else:
                    row: str = chr(97 + int(item[1]))
                    col: str = chr(97 + int(item[2]))
                    color: str = 'B' if item[0] == self.player_black.color else 'W'
                    text: str = f";{color}[{col}{row}]\n"
                    movement_string += text
            movement_string += ")"
            file.write(movement_string)

    def save_pickle(self) -> None:
        import pickle
        from os import chdir, getcwd, path
        wd = getcwd()
        full_path = path.join(wd, 'pklfiles')
        if not wd.endswith('pklfiles'):
            chdir(full_path)
        filename: str = ''
        while len(filename) < 1:
            text: str = "Please write the name of the file you want to save to. Do not include the file extension."
            filename: str = (sg.popup_get_text(text, title="Please Enter Text", font=('Arial Bold', 15)))
            if filename is None:
                return
        filename = path.join(full_path, f"{filename}")
        with open(f"{filename}.pkl", "wb") as pkl_file:
            backup_window: sg.Window = self.window
            backup_screen: pygame.Surface = self.screen
            backup_backup_board: pygame.Surface = self.backup_board
            del self.window
            del self.screen
            del self.backup_board
            pickle.dump(self, pkl_file)
            self.window: sg.Window = backup_window
            self.screen: pygame.Surface = backup_screen
            self.backup_board: pygame.Surface = backup_backup_board

    def load_pkl(self, inputPath):
        import pickle
        with open(inputPath, 'rb') as file:
            friend = pickle.load(file)
        return friend

    def refresh_board_pygame(self) -> None:
        self.screen.blit(self.backup_board, (0, 0))
        for board_row in self.board:
            for item in board_row:
                if item.stone_here_color == cf.unicode_black or item.stone_here_color == cf.unicode_white:  # this is bad, fix
                    pygame.draw.circle(self.screen, item.stone_here_color,
                                       (item.screen_row, item.screen_col), self.pygame_board_vals[2])
                elif item.stone_here_color == cf.unicode_diamond_black or item.stone_here_color == cf.unicode_diamond_white:
                    pygame.draw.circle(self.screen, item.stone_here_color,
                                       (item.screen_row, item.screen_col), self.pygame_board_vals[2])
                elif item.stone_here_color == cf.unicode_triangle_black or item.stone_here_color == cf.unicode_triangle_white:
                    pygame.draw.circle(self.screen, item.stone_here_color,
                                       (item.screen_row, item.screen_col), self.pygame_board_vals[2])
        pygame.display.update()

    def close_window(self):
        import platform
        if platform.system() == "Linux":
            self.window.close()
        elif platform.system() == "Windows":
            self.window.close()
            del self.window
            del self.backup_board
            pygame.display.quit()

    def making_score_board_object(self):
        from scoringboard import ScoringBoard
        import platform  # Required as for some reason the code/window behaves differently between linux and windows
        self.scoring_dead = ScoringBoard(self)
        if platform.system() == "Linux":
            self.window.close()
            ui.setup_board_window_pygame(self.scoring_dead)  # Makes a window, but nothing you click will do anything
            self.scoring_dead.refresh_board_pygame()
            winner = self.scoring_dead.dealing_with_dead_stones()
            return winner
        elif platform.system() == "Windows":
            self.close_window()
            ui.setup_board_window_pygame(self.scoring_dead)
            self.scoring_dead.refresh_board_pygame()
            winner = self.scoring_dead.dealing_with_dead_stones()
            return winner
