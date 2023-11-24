import uifunctions as ui
import PySimpleGUI as sg
from time import sleep
import math
import pygame


class Player():
    def __init__(self, name=None, color=None, captured=0, komi=0, unicode_choice=None):
        self.name = name
        self.color = color
        self.captured = captured
        self.komi = komi
        self.unicode = unicode_choice
        self.territory = 0

    def choose_name(self):  # feels like i could somehow combine choose_name and choose_komi...
        info = "Please Click Yes if you want to change your name"
        modify_name = sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))
        if modify_name == "No":
            self.name = "Player Two"
            if self.color == "Black":
                self.name = "Player One"
            return
        info = "Please Enter a name you would like to use, but keep it less than 30 characters:"
        while self.name is None:
            try:
                self.name = ui.validation_gui(info, lambda x: str(x)[:30])
                break
            except SyntaxError:
                ui.default_popup_no_button("It seems you entered a name longer than 30 characters. Please try again", time=2)
                sleep(1.3)

    def choose_komi(self):
        info = "Please Click Yes if you want to change your Komi"
        modify_komi = sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))
        if modify_komi == "No":
            if self.color == "White":
                self.komi = 6.5
            return
        done = False

        while self.komi == 0 and done is not True:
            try:
                info = f"Your color is {self.color}. Please enter Komi Value. 6.5 is normally done, but only for white:"
                self.komi = ui.validation_gui(info, float)
                break
            except ValueError:
                ui.default_popup_no_button(info="It seems you entered something that isn't a float. Please try again", time=2)
                sleep(1.3)


unicode_black = (0, 0, 0)
unicode_white = (255, 255, 255)
unicode_none = (120, 120, 120)
unicode_triangle_black = (120, 80, 40)
unicode_triangle_white = (160, 80, 0)
unicode_diamond_black = (169, 169, 169)  # represents dead pieces
unicode_diamond_white = (69, 69, 69)


class BoardNode():
    def __init__(self, row_value=None, col_value=None):
        self.row = row_value
        self.col = col_value
        self.screen_row = None
        self.screen_col = None
        self.stone_here_color = unicode_none
        self.connections = set()

    def __str__(self):
        #return (f"This is a BoardNode with coordinates of ({self.row},{self.col}) and a stone of {self.stone_here_color}")
        return (f"This is a BoardNode with coordinates of ({self.col},{self.row}) and a stone of {self.stone_here_color}")
    # Allows for updating a specific variable in the BoardNode class
    def change_boardnode_value(self, class_value, value):
        if hasattr(self, class_value):
            setattr(self, class_value, value)
        else:
            ui.p("No attribute for that")


class BoardString():  #probably not needed eventually, but using it to prototype stuff
    def __init__(self, color, member_set) -> None:
        self.color = color
        self.member_set = member_set
        self.list_idx = self.calculate_idx(member_set)
        self.connected_strings = None

    def __str__(self) -> str:
        return (f"this is a board string of color {self.color} and with len of {len(self.list_idx)} and values {self.list_idx}\
             and a xmax and xmin of {self.xmax, self.xmin}, and a ymax and ymin of {self.ymax, self.ymin}")

    def calculate_idx(self, set_objects):
        from operator import itemgetter
        sorting_list = []
        for item in set_objects:
            sorting_list.append((item.col, item.row))  #idk why it's weird...
            
        
        sorting_list.sort(key=lambda item: (item[0], item[1]))
        self.xmax = sorting_list[-1][0]
        self.xmin = sorting_list[0][0]
        self.ymax = max(sorting_list, key=itemgetter(1))[1]
        self.ymin = min(sorting_list, key=itemgetter(1))[1]
        
        return sorting_list

class GoBoard():
    def __init__(self, board_size=17, defaults=True):
        self.board_size = board_size
        self.defaults = defaults
        self.board = self.setup_board()
        self.player_black = self.setup_player(self.defaults, "Player One", "Black", unicode_black)
        self.player_white = self.setup_player(self.defaults, "Player Two", "White", unicode_white)
        self.whose_turn = self.player_black
        self.not_whose_turn = self.player_white
        self.times_passed = 0
        self.turn_num = 0
        self.position_played_log = list()
        self.visit_kill = set()
        self.killed_last_turn = set()
        self.killed_log = list()
        self.mode = "Playing"
        self.mode_change = True
        self.handicap = self.default_handicap()
        self.window = None
        self.screen = None  # Could make problems
        self.backup_board = None
        self.pygame_board_vals = None  # (workable_area, distance, circle_radius)
        self.empty_strings = list()
        self.black_strings = list()
        self.white_strings = list()

    def setup_board(self):
        board2 = [[BoardNode(row, col) for col in range(self.board_size)] for row in range(self.board_size)]
        for item_row in board2:
            for item in item_row:
                workable_area = 620 / (self.board_size - 1)
                item.screen_row = 40 + workable_area * item.row  # hardcoded values. Suboptimal
                item.screen_col = 40 + workable_area * item.col  # hardcoded values. Suboptimal
                friends = self.check_neighbors(item)
                for place in friends:
                    item.connections.add(board2[place[0]][place[1]])
        return board2

    # This sets up the Player class, assigning appropriate values to each player as needed
    def setup_player(self, defaults, nme, clr, uc):
        if defaults:
            if clr == "Black":
                player_assignment = Player(name=nme, color=clr, unicode_choice=uc)
            else:
                player_assignment = Player(name=nme, color=clr, komi=6.5, unicode_choice=uc)
        else:
            player_assignment = Player(color=clr, unicode_choice=uc)
            player_assignment.choose_name()
            player_assignment.choose_komi()
        return player_assignment

# By default there should not be any handicap.
    def default_handicap(self):
        return (False, "None", 0)

    def switch_player(self):
        if self.whose_turn == self.player_black:
            self.whose_turn = self.player_white
            self.not_whose_turn = self.player_black
        else:
            self.whose_turn = self.player_black
            self.not_whose_turn = self.player_white

    def custom_handicap(self, defaults):
        if defaults is True:
            return (False, "None", 0)
        info = "Please Click Yes if you want choose where you play your handicap."
        manual_handicap = sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))
        handicap_points9 = [(2, 6), (6, 2), (6, 6), (2, 2), (4, 4)]
        handicap_points13 = [(3, 9), (9, 3), (9, 9), (3, 3), (6, 6), (6, 3), (6, 9), (3, 6), (9, 6)]
        handicap_points17 = [(3, 13), (13, 3), (13, 13), (3, 3), (8, 8), (8, 3), (8, 13), (3, 8), (13, 8)]
        choosen_list = handicap_points17
        if self.board_size == 9:
            choosen_list = handicap_points9
        elif self.board_size == 13:
            choosen_list = handicap_points13
        player_choice = ui.handicap_person_gui()
        if player_choice == "Black":
            self.whose_turn = self.player_black
        elif player_choice == "White":
            self.whose_turn = self.player_white
        else:
            return (False, "None", 0)
        handicap_info = ui.handicap_number_gui(self.board_size)
        if manual_handicap == "No":
            for idx in range(handicap_info):
                row, col = choosen_list[idx]
                place = self.board[row][col]
                self.play_piece(row, col)
                pygame.draw.circle(self.screen, self.whose_turn.unicode,
                                   (place.screen_row, place.screen_col), self.pygame_board_vals[2])
            self.refresh_board_pygame()
            self.switch_player()
        else:
            self.manual_handicap_placement(handicap_info)
        self.position_played_log.append(("Break between handicaps and normal play", -1, -1))
        self.turn_num = 0
        return (True, self.not_whose_turn.color, handicap_info)

    def manual_handicap_placement(self, handicap_info):
        ui.def_popup(f"Please place {handicap_info} number of pieces where you wish,\
                    as a handicap.Then the opponent will play.", 3)
        for idx in range(handicap_info):
            valid_piece = False
            while not valid_piece:
                event, values = self.window.read()
                while event == "Pass Turn" or event == "Save Game" or event == "Undo Turn":
                    ui.def_popup("You can't do these actions during the handicap stage.", 3)
                    event, values = self.window.read()
                if event == "Exit Game" or event == "Res":
                    self.turn_options(event)
                row, col = values['-GRAPH-']
                found_piece, piece = self.find_piece_click([row, col])
                if found_piece:
                    if piece.stone_here_color == unicode_none:
                        valid_piece = found_piece

            if found_piece:
                self.times_passed = 0
                truth_value = self.play_piece(piece.row, piece.col)
                if truth_value:
                    pygame.draw.circle(self.screen, self.whose_turn.unicode,
                                       (piece.screen_row, piece.screen_col), self.pygame_board_vals[2])
                    pygame.display.update()
        self.switch_player()

    def play_game(self, fromFile=False, fixes_handicap=False):
        if self.mode == "Playing":
            if fromFile is not True:
                self.board = self.setup_board()
            else:
                self.refresh_board_pygame()
                if self.position_played_log[-1][0] == "Black":
                    self.switch_player()
                    self.play_turn()
            if fixes_handicap is True:
                self.handicap = self.custom_handicap(False)

            while (self.times_passed <= 1):
                self.play_turn()
            self.mode = "Scoring"
            self.times_passed = 0
            self.resuming_scoring_buffer("Scoring")
            ui.end_game_popup()
            self.scoring_block()
        elif self.mode == "Finished":
            self.refresh_board_pygame()
            event, values = self.window.read()
            if event == "Exit Game":
                from main import play_game_main
                self.window.close()
                play_game_main()
                quit()
            elif event == sg.WIN_CLOSED:
                quit()
        else:
            self.mode_change = True
            self.times_passed = 0
            self.scoring_block()

    def switch_button_mode(self):
        if self.mode == "Scoring":
            self.window["Res"].update("Resume Game")
            self.times_passed = 0
        elif self.mode == "Playing":
            self.window["Res"].update("Quit Program")
        self.mode_change = False

    def scoring_block(self):
        while not self.mode == "Finished":
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
        self.dealing_with_dead_stones()
        self.counting_territory()
        self.end_of_game()

    def resuming_scoring_buffer(self, text):
        self.turn_num += 1
        self.position_played_log.append(text)
        self.killed_log.append([])

    def remove_dead(self):  # make shorter
        self.killed_last_turn.clear()
        ui.update_scoring(self)
        truth_value = False
        while not truth_value:
            event, values = self.window.read()
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
                self.window.close()
                play_game_main()
                quit()
            elif event == sg.WIN_CLOSED:
                quit()
            else:
                row, col = values['-GRAPH-']
                found_piece, piece = self.find_piece_click([row, col])

                if found_piece and piece.stone_here_color == unicode_none:
                    ui.def_popup("You can't remove empty areas", 1)
                elif found_piece:
                    series = self.making_go_board_strings_helper(piece)
                    piece_string = list()
                    for item in series:
                        if item.stone_here_color == self.player_black.unicode:
                            piece_string.append(((item.row, item.col), item.stone_here_color, unicode_diamond_black))
                            item.stone_here_color = unicode_diamond_black

                        else:
                            piece_string.append(((item.row, item.col), item.stone_here_color, unicode_diamond_white))
                            item.stone_here_color = unicode_diamond_white
                    self.refresh_board_pygame()
                    info = "Other player, please click yes if you are ok with these changes"
                    modify_name = sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))
                    if modify_name == "No":
                        for item in series:
                            if item.stone_here_color == unicode_diamond_black:
                                item.stone_here_color = self.player_black.unicode
                            elif item.stone_here_color == unicode_diamond_white:
                                item.stone_here_color = self.player_white.unicode
                        self.refresh_board_pygame()
                        return

                    for item in series:
                        self.board[item.row][item.col].stone_here_color = unicode_none
                    self.refresh_board_pygame()
                    if piece_string[0][1] == self.player_black.unicode:
                        self.player_white.captured += len(piece_string)
                    else:
                        self.player_black.captured += len(piece_string)
                    temp_list = list()
                    for item in piece_string:
                        temp_list.append((item[1], item[0][0], item[0][1], "Scoring"))
                    self.killed_log.append(temp_list)
                    self.position_played_log.append("Dead Removed")
                    self.turn_num += 1
                    truth_value = True
        self.switch_player()
        return

    def end_of_game(self):
        ui.end_game_popup_two(self)
        ui.default_popup_no_button("Please save to a file, thank you.", 3)
        self.save_pickle()
        from main import play_game_main
        self.window.close()
        play_game_main()
        quit()

    def find_piece_click(self, input_location):
        for item_row in self.board:  # ! list comprehension?
            for item in item_row:
                item_location = [item.screen_row, item.screen_col]
                if math.dist(input_location, item_location) <= self.pygame_board_vals[2]:
                    return True, item
        return False, [-1, -1]

    def play_turn(self):
        ui.update_scoring(self)
        truth_value = False
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
        temp_list = list()
        for item in self.killed_last_turn:
            temp_list.append((self.not_whose_turn.unicode, item.row, item.col))
        self.killed_log.append(temp_list)
        self.switch_player()
        return

    def turn_options(self, event, text=None):
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
            self.window.close()
            play_game_main()
            quit()
        else:
            raise ValueError

    def play_piece(self, row, col):
        piece = self.board[row][col]
        liberty_value = 0
        if (piece.stone_here_color != unicode_none):
            ui.def_popup("You tried to place where there is already a piece. Please try your turn again.", 2)
            return False
        elif (self.turn_num > 2 and self.ko_rule_break(piece) is True):
            ui.def_popup("Place the piece there would break the ko rule. Please try your turn again.", 2)
            return False
        elif (self.kill_stones(piece) is True):
            piece.stone_here_color = self.whose_turn.unicode
            self.turn_num += 1
            self.position_played_log.append((self.whose_turn.color, row, col))
            self.refresh_board_pygame()
            return True
        elif (self.sfunction(piece, self.whose_turn) == liberty_value):
            ui.def_popup("Place the piece there would break the self death rule. Please try your turn again.", 2)
            return False

        else:  # No rules or special cases are broken, play piece as normal.
            self.position_played_log.append((self.whose_turn.color, row, col))
            piece.stone_here_color = self.whose_turn.unicode
            self.killed_last_turn.clear()
        self.turn_num += 1
        return True

    def undo_checker(self):
        if self.mode == "Scoring":
            self.undo_turn(scoring=True)
        else:
            self.undo_turn()

    def undo_turn(self, scoring=False):
        if self.position_played_log[-1] == "Resumed" or self.position_played_log[-1] == "Scoring":
            tmp = self.position_played_log.pop()
            self.move_back(scoring)
            self.turn_num -= 1
            self.mode_change = True
            if tmp == "Resumed":  # Could modify this to undo two turns somehow.
                self.mode = "Scoring"
                self.times_passed = 2
            elif tmp == "Scoring":
                self.mode = "Playing"
            return

        elif self.position_played_log[-1][0] == "Passed" or self.position_played_log[-1][0] == "Scoring Passed":
            self.position_played_log.pop()
            self.move_back(scoring)
            self.turn_num -= 1
            self.times_passed = 0
            if len(self.position_played_log) > 0:
                if self.position_played_log[-1][0] == "Passed" or self.position_played_log[-1][0] == "Scoring Passed":
                    self.times_passed = 1
            self.switch_player()
            return

        if not scoring:
            color, row, col = self.position_played_log.pop()
            self.board[row][col].stone_here_color = unicode_none
        else:
            self.position_played_log.pop()
        # This part reverts the board back to its state 1 turn ago
        revive = self.killed_log.pop()
        capture_update_val = len(revive)

        if len(revive) > 0:
            unicode = revive[0][0]
        else:
            unicode = unicode_none
        for item in revive:
            if not scoring:
                unicode, row, col = item
            else:
                unicode, row, col, scoring = item
            place = self.board[row][col]
            place.stone_here_color = unicode
        self.refresh_board_pygame()
        self.turn_num -= 1
        self.not_whose_turn.captured -= capture_update_val
        self.switch_player()

    def move_back(self, scoring=False):
        if len(self.killed_log) > 0:
            self.killed_last_turn.clear()
            temp_list = self.killed_log.pop()
            for item in temp_list:
                temp_node = BoardNode(row_value=item[1], col_value=item[2])
                self.killed_last_turn.add(temp_node)

    def ko_rule_break(self, piece):
        if self.sfunction(piece, self.whose_turn) > 0:
            return False
        if piece in self.killed_last_turn:
            return True
        return False

    # Takes in a boardNode, returns a list of tuples of coordinates
    def check_neighbors(self, piece):
        neighbors = [(piece.row - 1, piece.col), (piece.row + 1, piece.col),
                     (piece.row, piece.col - 1), (piece.row, piece.col + 1)]
        valid_neighbors = []
        for coordinate in neighbors:
            if 0 <= coordinate[0] < self.board_size and 0 <= coordinate[1] < self.board_size:
                valid_neighbors.append(coordinate)
        return valid_neighbors

    # Uses BFS to figure out liberties and connected pieces of the same type
    def sfunction(self, piece, which_player, visited=None):  # needs to be which_player, not whose_turn
        if visited is None:
            visited = set()
        visited.add(piece)
        neighboring_piece = piece.connections
        liberties = 0
        for neighbor in neighboring_piece:
            if neighbor.stone_here_color == unicode_none and neighbor not in visited:
                liberties += 1
            elif neighbor.stone_here_color != which_player.unicode:
                pass
            elif neighbor not in visited:
                liberties += self.sfunction(neighbor, which_player, visited)
        self.visit_kill = visited
        return liberties

    # This takes in the player who is gaining the captured pieces
    def remove_stones(self):
        self.killed_last_turn.clear()
        for position in self.visit_kill:
            self.killed_last_turn.add(position)
            self.whose_turn.captured += 1
            position.stone_here_color = unicode_none

    def kill_stones(self, piece):  # needs to return true if it does kill stones
        piece.stone_here_color = self.whose_turn.unicode
        neighboring_pieces = piece.connections
        truth_value = False
        for neighbor in neighboring_pieces:
            if neighbor.stone_here_color == self.not_whose_turn.unicode:
                if (self.sfunction(neighbor, self.not_whose_turn) == 0):
                    self.remove_stones()
                    truth_value = True
        if truth_value is False:
            piece.stone_here_color = unicode_none
        return truth_value

    def save_to_SGF(self, filename2):
        with open(f"{filename2}.sgf", 'w', encoding='utf-8') as file:
            from datetime import date
            seqs = ["Dead Removed", "Break between handicaps and normal play", "Dead Removed",
                    "Resumed", "Scoring", "Scoring Passed"]
            movement_string = ""
            today = date.today()
            text = f"(;\nFF[4]\nCA[UTF-8]\nGM[1]\nDT[{today}]\nGN[relaxed]\n\
            PC[https://github.com/EGPeat/GoGame]\n\
            PB[{self.player_black.name}]\n\
            PW[{self.player_white.name}]\n\
            BR[Unknown]\nWR[Unknown]\n\
            OT[Error: time control missing]\nRE[?]\n\
            SZ[{self.board_size}]\nKM[{self.player_white.komi}]\nRU[Japanese];"
            file.write(text)
            handicap_idx = 0
            handicap_flag = self.handicap[0]
            for item in self.position_played_log:
                if handicap_flag and handicap_idx < self.handicap[2]:
                    row = chr(97 + int(item[1]))
                    col = chr(97 + int(item[2]))
                    if self.handicap[1] == "Black":
                        text2 = f";AB[{col}{row}]\n"
                        movement_string += text2
                    elif self.handicap[1] == "White":
                        text2 = f";AW[{col}{row}]\n"
                        movement_string += text2
                    else:
                        raise IndexError
                    handicap_idx += 1

                elif item[0] in seqs or item in seqs:
                    pass
                elif item[0] == "Passed":
                    if movement_string[-7] == "B" or movement_string[-5] == "B":
                        text2 = ";W[]\n"
                    else:
                        text2 = ";B[]\n"
                    movement_string += text2
                else:
                    row = chr(97 + int(item[1]))
                    col = chr(97 + int(item[2]))
                    if item[0] == self.player_black.color:
                        text2 = f";B[{col}{row}]\n"
                    else:
                        text2 = f";W[{col}{row}]\n"
                    movement_string += text2
            movement_string += ")"
            file.write(movement_string)

    def save_pickle(self):
        import pickle
        filename = ''
        while len(filename) < 1:
            text = "Please write the name of the file you want to save to. Do not include the file extension in what you write"
            filename = (sg.popup_get_text(text, title="Please Enter Text", font=('Arial Bold', 15)))
            if filename is None:
                return
        with open(f"{filename}.pkl", "wb") as pkl_file:
            backup_window = self.window
            backup_screen = self.screen
            backup_backup_board = self.backup_board
            del self.window
            del self.screen
            del self.backup_board
            pickle.dump(self, pkl_file)
            self.window = backup_window
            self.screen = backup_screen
            self.backup_board = backup_backup_board

    def load_pkl(self, inputPath):
        import pickle
        with open(inputPath, 'rb') as file:
            friend = pickle.load(file)
        return friend

    def refresh_board_pygame(self):
        self.screen.blit(self.backup_board, (0, 0))
        for board_row in self.board:
            for item in board_row:
                if item.stone_here_color == unicode_black or item.stone_here_color == unicode_white:  # this is bad, fix
                    pygame.draw.circle(self.screen, item.stone_here_color,
                                       (item.screen_row, item.screen_col), self.pygame_board_vals[2])
                elif item.stone_here_color == unicode_diamond_black or item.stone_here_color == unicode_diamond_white:
                    pygame.draw.circle(self.screen, item.stone_here_color,
                                       (item.screen_row, item.screen_col), self.pygame_board_vals[2])
                elif item.stone_here_color == unicode_triangle_black or item.stone_here_color == unicode_triangle_white:
                    pygame.draw.circle(self.screen, item.stone_here_color,
                                       (item.screen_row, item.screen_col), self.pygame_board_vals[2])

        pygame.display.update()
  
    def pieces_into_sets(self):
        self.empty_space_set = set()
        self.black_set = set()
        self.white_set = set()
        self.empty_strings = list() #remove later
        self.black_strings = list() #remove later
        self.white_strings = list() #remove later
        for xidx in range(self.board_size):  # This puts all node spots into 3 sets
            for yidx in range(self.board_size):
                temp_node = self.board[xidx][yidx]
                if temp_node.stone_here_color == unicode_white:
                    self.white_set.add(temp_node)
                elif temp_node.stone_here_color == unicode_black:
                    self.black_set.add(temp_node)
                else:
                    self.empty_space_set.add(temp_node)
    
    def dealing_with_dead_stones(self):
        self.pieces_into_sets()
        self.making_go_board_strings(self.empty_space_set, unicode_none, False)
        self.making_go_board_strings(self.black_set, unicode_black, False)
        self.making_go_board_strings(self.white_set, unicode_white, False)
        #print("Making strings of black pieces")
        #for item in self.black_strings:
        #    print(item)
        
        self.mixed_str = list()
        print(f"the len of self.empty_strings is {len(self.empty_strings)}")
        print(f"the len of self.black_strings is {len(self.black_strings)}")
        print(f"the len of self.white_strings is {len(self.white_strings)}")
        for string_obj in self.empty_strings.copy(): #copy is bad
            print("new round\n\n")
            obj = next(iter(string_obj.member_set))
            #im unsure if making the mixed string for only 1 color at a time would be a problem? idk
            #tmp= self.making_mixed_string(obj, self.player_black.unicode, self.black_strings[0], self.black_strings)
            #if tmp[0]:
            #    self.mixed_str.append(tmp[1])
        print(f"the len of self.empty_strings is {len(self.empty_strings)}")
        print(f"the len of self.black_strings is {len(self.black_strings)}")
        print(f"the len of self.white_strings is {len(self.white_strings)}")
        #print(f"the len of self.mixed_str is {len(self.mixed_str)}")
        #for item in self.mixed_str:
        #    print(item)
        print("black strings")
        for item in self.black_strings:
            print(item)
        
        
    def counting_territory(self):  #something somewhere makes row and col switch...
        self.pieces_into_sets()
        self.making_go_board_strings(self.empty_space_set, unicode_none, True)
        
    def mixed_string_set_removal(self, connections_set, color, enemy_list):
        while connections_set:
            piece = connections_set.pop()
            piece_color = piece.stone_here_color
            piece_string = self.flood_fill(piece)
            piece_string_obj = BoardString(color, piece_string[0])
            if piece_color == unicode_none:
                for obj in self.empty_strings:
                    if obj.list_idx == piece_string_obj.list_idx:
                        self.empty_strings.remove(obj)
            elif piece_color != color:
                for obj in enemy_list:
                    if obj.list_idx == piece_string_obj.list_idx:
                        enemy_list.remove(obj)
            else:
                print(piece_color, color)
                print("WrongColorInSetError")
            

    def making_mixed_string(self, piece, color, original_string, strings_set):
        connections, disconnected_temp = self.making_mixed_string_helper(piece, color, original_string, strings_set)
        
        connections_string = BoardString("Empty and Enemy", connections)
        disconnected_strings = BoardString("Disconnected Outer String", disconnected_temp)
        strings_set.append(disconnected_strings)
        if connections_string.xmin < disconnected_strings.xmin or connections_string.xmax > disconnected_strings.xmax:
            print("a")
            return (False, -1)
        elif connections_string.ymin < disconnected_strings.ymin or connections_string.ymax > disconnected_strings.ymax:
            print("b")
            return (False, -1)
        else:
            if strings_set == self.black_strings:
                self.mixed_string_set_removal(connections, color, self.white_strings)  
                #probably need to remake the set of strings? using like pieces into sets, and then sets to strings idk
                #bc i need to run the thing twice, on black and on white
            else:
                self.mixed_string_set_removal(connections, color, self.black_strings)
            print(connections_string)
            print("lets gooooo")
            print(disconnected_strings)
            return (True, connections_string)
            #after this need to check all possibilites, using the connections_string, 
            # as well as all liberties of disconnected_strings
            #need to make sure when i check all posibility it doesn't like... kill eyes lol
    
    
    def making_mixed_string_helper(self, piece, color, original_string, strings_set, connected_pieces=None, outer_pieces=None):
        if connected_pieces is None:
            connected_pieces = set()
        if outer_pieces is None:
            outer_pieces = original_string.member_set
        connected_pieces.add(piece)
        neighboring_pieces = piece.connections
        for neighbor in neighboring_pieces:
            if neighbor.stone_here_color != color and neighbor not in connected_pieces:
                self.making_mixed_string_helper(neighbor, color, original_string, strings_set, connected_pieces, outer_pieces)
            elif neighbor.stone_here_color == color:
                if neighbor not in outer_pieces:
                    for place in outer_pieces.copy():
                        #xdiff = place.row - neighbor.row
                        #ydiff = place.col - neighbor.col
                        #if abs(xdiff) == 1 and abs(ydiff) == 1:
                            #open = self.board[place.row + xdiff][place.col].stone_here_color == unicode_none
                            #yopen = self.board[place.row][place.col + ydiff].stone_here_color == unicode_none
                            #if xopen or yopen:
                                for item in strings_set.copy():
                                    if neighbor in item.member_set:
                                        outer_pieces.update(item.member_set)
                                        strings_set.remove(item)
                                else:
                                    pass
            else:
                pass
        return connected_pieces, outer_pieces

    def making_go_board_strings(self, piece_set, piece_type, final):
        list_of_piece_strings = list()
        while len(piece_set):
            piece = piece_set.pop()
            string = self.making_go_board_strings_helper(piece)
            list_of_piece_strings.append(string)
            piece_set -= string
        for item in list_of_piece_strings:
            string_obj = BoardString(piece_type, item)
            if piece_type == unicode_none:
                self.empty_strings.append(string_obj)
            elif piece_type == unicode_black:
                self.black_strings.append(string_obj)
            elif piece_type == unicode_white:
                self.white_strings.append(string_obj)
            if final:
                item2 = item.pop()
                item.add(item2)
                sets = self.flood_fill(item2)
                self.assignment_logic(sets, piece_type)

    def making_go_board_strings_helper(self, piece, connected_pieces=None):
        if connected_pieces is None:
            connected_pieces = set()
        connected_pieces.add(piece)
        neighboring_pieces = piece.connections
        diagonal_change = [[1, 1], [-1, -1], [1, -1], [-1, 1]]
        diagonals = set()
        for item in diagonal_change:
            new_row = piece.row + item[0]
            new_col = piece.col + item[1]
            if new_row >= 0 and new_row < self.board_size and new_col >= 0 and new_col < self.board_size:
                diagonals.add(self.board[new_row][new_col])

        for neighbor in neighboring_pieces:
            if neighbor.stone_here_color == piece.stone_here_color and neighbor not in connected_pieces:
                self.making_go_board_strings_helper(neighbor, connected_pieces)

        for diagonal in diagonals:
            if diagonal.stone_here_color == piece.stone_here_color and diagonal not in connected_pieces:
                xdiff = diagonal.row - piece.row
                ydiff = diagonal.col - piece.col
                xopen = self.board[piece.row + xdiff][piece.col].stone_here_color == unicode_none
                yopen = self.board[piece.row][piece.col + ydiff].stone_here_color == unicode_none
                if xopen or yopen:
                    self.making_go_board_strings_helper(diagonal, connected_pieces)
                else:
                    pass
            else:
                pass
        return connected_pieces

    def assignment_logic(self, sets, empty):
        neighboring = sets[1] - sets[0]
        pieces_string = sets[0]
        black_pieces, white_pieces = 0, 0
        for item in neighboring:
            if item.stone_here_color == unicode_black:
                black_pieces += 1
            else:
                white_pieces += 1
        if black_pieces == 0 or white_pieces == 0:
            if black_pieces == 0:
                player, unicode_choice = self.player_white, unicode_triangle_white
            elif white_pieces == 0:
                player, unicode_choice = self.player_black, unicode_triangle_black
            player.territory += len(pieces_string)
            if empty == "Empty":
                for item in pieces_string:
                    pygame.draw.circle(self.screen, unicode_choice,
                                    (item.screen_row, item.screen_col), self.pygame_board_vals[2])
                    self.board[item.row][item.col].stone_here_color = unicode_choice
                pygame.display.update()
        return

    def flood_fill(self, piece, connected_pieces=None):
        if connected_pieces is None:
            connected_pieces = (set(), set())
        connected_pieces[0].add(piece)
        neighboring_pieces = piece.connections
        for neighbor in neighboring_pieces:
            if neighbor.stone_here_color == piece.stone_here_color and neighbor not in connected_pieces[0]:
                self.flood_fill(neighbor, connected_pieces)
            else:
                connected_pieces[1].add(neighbor)
                pass
        return connected_pieces


def initializing_game(window, board_size, defaults=True, fixes_handicap=False, choosen_file=None):
    info = "Click yes if you want to modify the player names and komi"
    if not defaults:
        only_modify_name = (sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15)))
        if only_modify_name == "No":
            GameBoard = GoBoard(board_size, True)
        else:
            GameBoard = GoBoard(board_size, defaults)
    else:
        GameBoard = GoBoard(board_size, defaults)
    window.close()
    ui.setup_board_window_pygame(GameBoard)
    info = "Click yes if you want to modify the handicap"
    if fixes_handicap:
        modify_handicap = (sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15)))
        if modify_handicap == "Yes":
            GameBoard.play_game(fixes_handicap=True)
        else:
            GameBoard.play_game(fixes_handicap=False)

    else:
        GameBoard.play_game(fixes_handicap)
