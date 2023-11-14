import uifunctions as ui
import PySimpleGUI as sg
from time import sleep


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


unicode_black = u"\u26AB"
unicode_white = u"\u26AA"
unicode_none = u"\U0001F7E9"
unicode_triangle_black = u"\u25B2"
unicode_triangle_white = u"\u25B3"
unicode_diamond_black = u"\u29BF"  # represents dead pieces
unicode_diamond_white = u"\u29BE"


class BoardNode():
    def __init__(self, row_value=None, col_value=None):
        self.row = row_value
        self.col = col_value
        self.stone_here_color = unicode_none

    def __str__(self):
        return (f"This is a BoardNode with coordinates of ({self.row},{self.col}) and a stone of {self.stone_here_color}")

    # Allows for updating a specific variable in the BoardNode class
    def change_boardnode_value(self, class_value, value):
        if hasattr(self, class_value):
            setattr(self, class_value, value)
        else:
            ui.p("No attribute for that")


class GoBoard():
    def __init__(self, board_size=17, defaults=True):
        self.board_size = board_size
        self.defaults = defaults
        self.board = [[BoardNode(row, col) for col in range(self.board_size)] for row in range(self.board_size)]
        self.player_black = self.setup_player(self.defaults, "Player One", "Black", unicode_black)
        self.player_white = self.setup_player(self.defaults, "Player Two", "White", unicode_white)
        self.whose_turn = self.player_black
        self.not_whose_turn = self.player_white
        self.times_passed = 0
        self.turn_num = 0
        self.position_played_log = list()
        self.visit_kill = set()  #potentially removeable
        self.killed_last_turn = set()
        self.killed_log = list()
        self.mode = "Playing"
        self.mode_change = True
        self.handicap = self.default_handicap()

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

    def custom_handicap(self, defaults, window):
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
                window[(row, col)].update(self.whose_turn.unicode)
                self.play_piece(row, col, window)
                self.refresh_board(window)
        else:
            self.manual_handicap_placement(window, handicap_info)
        self.refresh_board(window)
        self.position_played_log.append(("Break between handicaps and normal play", -1, -1))
        self.turn_num = 0
        return (True, self.whose_turn.color, handicap_info)

    def manual_handicap_placement(self, window, handicap_info):
        ui.def_popup(f"Please place {handicap_info} number of pieces where you wish,\
                    as a handicap.Then the opponent will play.", 3)
        for idx in range(handicap_info):
            event, values = window.read()
            while event == "Pass Turn" or event == "Save Game" or event == "Undo Turn":
                ui.def_popup("You can't do these actions during the handicap stage.", 3)
                event, values = window.read()
            if event == "Exit Game" or event == "Res":
                self.turn_options(window, event)
            window[event].update(self.whose_turn.unicode)
            self.play_piece(event[0], event[1], window)
            self.refresh_board(window)
        self.switch_player()

    def play_game(self, window, fromFile=False, fixes_handicap=False):
        if self.mode == "Playing":
            if fixes_handicap is True:
                self.handicap = self.custom_handicap(False, window)
            if fromFile is not True:
                self.board = [[BoardNode(row, col) for col in range(self.board_size)] for row in range(self.board_size)]
            else:
                self.refresh_board(window)
                if self.position_played_log[-1][0] == "Black":
                    self.switch_player()
                    self.play_turn(window)

            while (self.times_passed <= 1):
                self.play_turn(window)
            self.mode = "Scoring"
            self.times_passed = 0
            self.resuming_scoring_buffer("Scoring")
            ui.end_game_popup()
            self.scoring_block(window)
        elif self.mode == "Finished":
            self.refresh_board(window)
            event, values = window.read()
            if event == "Exit Game":
                from main import play_game_main
                window.close()
                play_game_main()
                quit()
        else:
            self.mode_change = True
            self.times_passed = 0
            self.scoring_block(window)

    def scoring_block(self, window): #this and playlog could use work lol. kinda works odd...
        #same for quit to menu idk
        while not self.mode == "Finished":
            if self.mode_change:
                if self.mode == "Scoring":
                    window["Res"].update("Resume Game")
                    self.times_passed = 0
                elif self.mode == "Playing":
                    window["Res"].update("Quit Program")
                self.mode_change = False
            while self.mode == "Scoring":
                self.remove_dead(window)
                if self.times_passed == 2:
                    self.mode = "Finished"
            if self.mode_change:
                if not self.mode == "Scoring":
                    window["Res"].update("Quit Program")
            while (self.times_passed <= 1):
                self.play_turn(window)
            if self.times_passed == 2 and self.mode == "Playing":
                self.mode = "Scoring"
                self.resuming_scoring_buffer("Scoring")
                self.times_passed = 0
        self.counting_territory(window)
        self.end_of_game(window)

    def resuming_scoring_buffer(self, text):
        self.turn_num += 1
        self.position_played_log.append(text)
        self.killed_log.append([])

    def remove_dead(self, window):  # needs serious bugfixes
        self.killed_last_turn.clear()
        ui.update_scoring(self, window)
        truth_value = False
        while not truth_value:
            event, values = window.read()
            if event == "Pass Turn":
                self.turn_options(window, event, text="Scoring Passed")
                return
            elif event == "Save Game":
                self.save_to_json()
            elif event == "Res":
                self.mode = "Playing"
                self.mode_change = True
                self.resuming_scoring_buffer("Resumed")
                return
            elif event == "Undo Turn":
                if self.turn_num == 0:
                    ui.def_popup("You can't undo when nothing has happened.", 1)
                elif self.turn_num >= 1:
                    self.undo_turn(window, scoring=True)
                    return
            elif event == "Exit Game":
                from main import play_game_main
                window.close()
                play_game_main()
                quit()
            else:
                row = int(event[0])
                col = int(event[1])

                if self.board[row][col].stone_here_color == unicode_none:
                    ui.def_popup("You can't remove empty areas", 1)
                else:
                    series = self.making_go_board_strings_helper(self.board[row][col])
                    piece_string = list()
                    for item in series:
                        if item.stone_here_color == self.player_black.unicode:
                            piece_string.append(((item.row, item.col), item.stone_here_color, unicode_diamond_black))
                            window[(item.row, item.col)].update(unicode_diamond_black)
                        else:
                            piece_string.append(((item.row, item.col), item.stone_here_color, unicode_diamond_white))
                            window[(item.row, item.col)].update(unicode_diamond_white)
                    info = "Other player, please click yes if you are ok with these changes"
                    modify_name = sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))
                    if modify_name == "No":
                        for item in series:
                            window[(item.row, item.col)].update(item.stone_here_color)
                        return

                    for item in series:
                        window[(item.row, item.col)].update("")
                        self.board[item.row][item.col].stone_here_color = unicode_none
                        self.fix_star_spot(window, (row, col))
                    if piece_string[0][1] == self.player_black.unicode:
                        self.player_white.captured += len(piece_string)#pretty sure i can use use whose_turn and not_whose_turn
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

    def end_of_game(self, window):
        ui.end_game_popup_two(self)
        ui.default_popup_no_button("Please save to a file, thank you.", 3)
        self.save_to_json()
        from main import play_game_main
        window.close()
        play_game_main()
        quit()

    def play_turn(self, window):
        ui.update_scoring(self, window)
        truth_value = False
        while not truth_value:
            event, values = window.read()
            if not isinstance(event, tuple):
                self.turn_options(window, event, text="Passed")
                if event == "Pass Turn" or event == "Res" or event == "Undo Turn":
                    return
            else:
                row, col = int(event[0]), int(event[1])
                self.times_passed = 0
                truth_value = self.play_piece(row, col, window)
                if truth_value:
                    window[event].update(self.whose_turn.unicode)
        temp_list = list()
        for item in self.killed_last_turn:
            temp_list.append((self.not_whose_turn.unicode, item.row, item.col))
        self.killed_log.append(temp_list)#!
        self.switch_player()
        return

    def turn_options(self, window, event, text=None):
        if event == "Pass Turn":
            ui.def_popup("Skipped turn", 0.5)
            self.times_passed += 1
            self.turn_num += 1
            self.position_played_log.append((text, -3, -3))
            self.killed_log.append([])
            self.switch_player()
        elif event == "Save Game":
            self.save_to_json()
        elif event == "Res":
            quit()
        elif event == "Undo Turn":
            if self.turn_num == 0:
                ui.def_popup("You can't undo when nothing has happened.", 2)
            elif self.turn_num >= 1:
                self.undo_checker(window)
                return
        elif event == "Exit Game":
            from main import play_game_main
            window.close()
            play_game_main()
            quit()

    def play_piece(self, row, col, window):
        piece = self.board[row][col]
        suicidal_liberty_value = 0
        if (piece.stone_here_color != unicode_none):
            ui.def_popup("You tried to place where there is already a piece. Please try your turn again.", 2)
            return False
        elif (self.turn_num > 2 and self.ko_rule_break(piece) is True):
            ui.def_popup("Place the piece there would break the ko rule. Please try your turn again.", 2)
            return False
        elif (self.kill_stones(piece, window) is True):
            piece.stone_here_color = self.whose_turn.unicode
            self.turn_num += 1
            self.position_played_log.append((self.whose_turn.color, row, col))
            return True
        elif (self.suicide(piece, self.whose_turn) == suicidal_liberty_value):
            ui.def_popup("Place the piece there would break the ko rule. Please try your turn again.", 2)
            return False

        else:  # No rules or special cases are broken, play piece as normal.
            self.position_played_log.append((self.whose_turn.color, row, col))
            piece.stone_here_color = self.whose_turn.unicode
            self.killed_last_turn.clear()
        self.turn_num += 1
        return True

    def fix_star_spot(self, window, item, unicode_test=None):
        row, col = item
        size = self.board_size
        lst9 = ((2, 2), (size - 3, 2), (size - 3, size - 3), (2, size - 3))
        lst_not_9 = ((3, 3), (size - 4, 3), (size - 4, size - 4), (3, size - 4))
        star = u"\u2B50"

        if unicode_test is None:
            if size == 9 and (row, col) in lst9:
                window[(row, col)].update(star)
            elif (size == 13 or size == 17) and (row, col) in lst_not_9:
                window[(row, col)].update(star)
        else:
            if size == 9 and (row, col) in lst9 and unicode_test == unicode_none:
                window[(row, col)].update(star)
            elif (size == 13 or size == 17) and (row, col) in lst_not_9 and unicode_test == unicode_none:
                window[(row, col)].update(star)

    def undo_checker(self, window):
        if self.mode == "Scoring":
            self.undo_turn(window, scoring=True)
        else:
            self.undo_turn(window)

    def undo_turn(self, window, scoring=False):
        if self.position_played_log[-1] == "Resumed" or self.position_played_log[-1] == "Scoring":
            tmp = self.position_played_log.pop()
            self.move_back(scoring)
            self.turn_num -= 1
            if tmp == "Resumed":
                self.mode = "Scoring"
                self.times_passed = 2
            elif tmp == "Scoring":
                self.mode = "Playing"
            self.mode_change = True
            return

        elif self.position_played_log[-1][0] == "Passed" or self.position_played_log[-1][0] == "Scoring Passed":
            self.position_played_log.pop()
            self.move_back(scoring)
            self.turn_num -= 1
            self.times_passed = 0
            if self.position_played_log[-1][0] == "Passed" or self.position_played_log[-1][0] == "Scoring Passed":
                self.times_passed = 1
            self.switch_player()
            return

        if not scoring:
            color, row, col = self.position_played_log.pop()
            self.board[row][col].stone_here_color = unicode_none
            window[(row, col)].update("")
            self.fix_star_spot(window, (row, col))
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
                unicode, row, col, scoring = item  # annoying code
            self.board[row][col].stone_here_color = unicode
            window[(row, col)].update(unicode)#make new function
            self.fix_star_spot(window, (row, col), unicode_test=unicode)
        # This part updates some class values (player captures, killed_last_turn, turn_num)
        self.turn_num -= 1
        if unicode == unicode_black:
            self.player_white.captured -= capture_update_val
        elif unicode == unicode_white:
            self.player_black.captured -= capture_update_val
        self.switch_player()

    def move_back(self, scoring=False):
        if len(self.killed_log) > 0:
            self.killed_last_turn.clear()
            temp_list = self.killed_log.pop()
            for item in temp_list:
                temp_node = BoardNode(row_value=item[1], col_value=item[2])
                self.killed_last_turn.add(temp_node)

    def ko_rule_break(self, piece):
        if self.suicide(piece, self.whose_turn) > 0:
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
    def suicide(self, piece, which_player, visited=None):  # needs to be which_player, not whose_turn
        if visited is None:
            visited = set()
        visited.add(piece)
        neighbors = self.check_neighbors(piece)
        liberties = 0
        for coordinate in neighbors:
            neighboring_piece = self.board[coordinate[0]][coordinate[1]]
            if neighboring_piece.stone_here_color == unicode_none and neighboring_piece not in visited:
                liberties += 1
            elif neighboring_piece.stone_here_color != which_player.unicode:
                pass
            elif neighboring_piece not in visited:
                liberties += self.suicide(neighboring_piece, which_player, visited)
        self.visit_kill = visited
        return liberties

    # This takes in the player who is gaining the captured pieces
    def remove_stones(self, window):
        self.killed_last_turn.clear()
        for position in self.visit_kill:
            self.killed_last_turn.add(position)
            self.whose_turn.captured += 1
            position.stone_here_color = unicode_none
            window[(position.row, position.col)].update(' ')
            

    def kill_stones(self, piece, window):  # needs to return true if it does kill stones
        piece.stone_here_color = self.whose_turn.unicode
        neighbors = self.check_neighbors(piece)
        truth_value = False

        for coordinate in neighbors:
            neighboring_piece = self.board[coordinate[0]][coordinate[1]]
            if neighboring_piece.stone_here_color == self.not_whose_turn.unicode:
                if (self.suicide(neighboring_piece, self.not_whose_turn) == 0):
                    self.remove_stones(window)
                    truth_value = True
        if truth_value is False:
            piece.stone_here_color = unicode_none
        return truth_value

    def save_to_json(self):
        import json
        filename = ''
        while len(filename) < 1:
            text = "Please write the name of the txt file you want to save to. Do not include '.json' in what you write"
            filename = (sg.popup_get_text(text, title="Please Enter Text", font=('Arial Bold', 15)))
            if filename is None:
                return
        kill_list = []
        for item in self.killed_last_turn:
            kill_list.append([item.row, item.col])
        places_on_board = list()
        for xidx in range(self.board_size):
            for yidx in range(self.board_size):
                if not self.board[xidx][yidx].stone_here_color == "\U0001F7E9":
                    places_on_board.append([xidx, yidx, self.board[xidx][yidx].stone_here_color])
        with open(f"{filename}.json", 'w', encoding='utf-8') as file:
            dictionary_to_json = {
                "board_size": self.board_size,
                "defaults": self.defaults,
                "times_passed": self.times_passed,
                "turn_num": self.turn_num,
                "handicap": self.handicap,
                "position_played_log": self.position_played_log,
                "killed_last_turn": kill_list,
                "killed_log": self.killed_log,
                "player_black.name": self.player_black.name,
                "player_black.color": self.player_black.color,
                "player_black.captured": self.player_black.captured,
                "player_black.komi": self.player_black.komi,
                "player_black.unicode": self.player_black.unicode,
                "player_white.name": self.player_white.name,
                "player_white.color": self.player_white.color,
                "player_white.captured": self.player_white.captured,
                "player_white.komi": self.player_white.komi,
                "player_white.unicode": self.player_white.unicode,
                "places_on_board": places_on_board,
                "mode": self.mode,
                "mode_change": self.mode_change,
                "whose_turn": self.whose_turn,
                "not_whose_turn": self.not_whose_turn
            }
            json_object = json.dumps(dictionary_to_json, indent=4)
            file.write(json_object)
        ui.def_popup(f"Saved to {filename}.json", 2)

    def load_from_json(self, inputPath=''):
        data = load_and_parse_file(inputPath)
        self.board_size = data["board_size"]
        self.defaults = data["defaults"]
        self.times_passed = data["times_passed"]
        self.turn_num = data["turn_num"]
        self.handicap = data["handicap"]
        self.position_played_log = data["position_played_log"]
        temp_list = data['killed_last_turn']
        for item in temp_list:
            temp_node = BoardNode(row_value=item[0], col_value=item[1])
            self.killed_last_turn.add(temp_node)
        self.killed_log = data['killed_log']
        self.player_black.name = data["player_black.name"]
        self.player_black.color = data["player_black.color"]
        self.player_black.captured = data["player_black.captured"]
        self.player_black.komi = data["player_black.komi"]
        self.player_black.unicode = data["player_black.unicode"]
        self.whose_turn = data["whose_turn"]
        self.not_whose_turn = data['not_whose_turn']
        self.mode = data["mode"]
        self.mode_change = data["mode_change"]
        self.player_white.name = data["player_white.name"]
        self.player_white.color = data["player_white.color"]
        self.player_white.captured = data["player_white.captured"]
        self.player_white.komi = data["player_white.komi"]
        self.player_white.unicode = data["player_white.unicode"]
        board_list = data["places_on_board"]
        for item in board_list:
            bxidx, byidx, bcolor = item
            self.board[bxidx][byidx].stone_here_color = f"{bcolor}"

    def update_both_boards(self, window, idx, visual_choice1, visual_choice2=None):
        window[(idx.row, idx.col)].update(visual_choice1)
        self.board[idx.row][idx.col].stone_here_color = visual_choice1
    
    def refresh_board(self, window):
        for xidx in range(self.board_size):
            for yidx in range(self.board_size):
                if not self.board[xidx][yidx].stone_here_color == "\U0001F7E9":
                    window[(xidx, yidx)].update(self.board[xidx][yidx].stone_here_color)
        star = u"\u2B50"
        size = self.board_size
        lst9 = ((2, 2), (size - 3, 2), (size - 3, size - 3), (2, size - 3))
        lst_not_9 = ((3, 3), (size - 4, 3), (size - 4, size - 4), (3, size - 4))
        if self.board_size == 9:
            for item in lst9:
                if self.board[item[0]][item[1]].stone_here_color == "\U0001F7E9":
                    window[(item[0], item[1])].update(star)
        else:
            for item in lst_not_9:
                if self.board[item[0]][item[1]].stone_here_color == "\U0001F7E9":
                    window[(item[0], item[1])].update(star)

    def making_go_board_strings_helper(self, piece, connected_pieces=None):
        if connected_pieces is None:
            connected_pieces = set()
        connected_pieces.add(piece)
        neighboring_pieces = self.check_neighbors(piece)

        for coordinate in neighboring_pieces:
            neighbor = self.board[coordinate[0]][coordinate[1]]
            if neighbor.stone_here_color == piece.stone_here_color and neighbor not in connected_pieces:
                self.making_go_board_strings_helper(neighbor, connected_pieces)
            else:
                pass
        return connected_pieces

    def counting_territory(self, window):
        self.empty_space_set = set()
        self.black_set = set()
        self.white_set = set()
        for xidx in range(self.board_size):  # This puts all node spots into 3 sets
            for yidx in range(self.board_size):
                temp_node = self.board[xidx][yidx]
                if temp_node.stone_here_color == unicode_white:
                    self.white_set.add(temp_node)
                elif temp_node.stone_here_color == unicode_black:
                    self.black_set.add(temp_node)
                else:
                    self.empty_space_set.add(temp_node)
        self.making_go_board_strings(self.empty_space_set, window)

    def making_go_board_strings(self, piece_set, window):
        list_of_piece_strings = list()
        while len(piece_set):
            piece = piece_set.pop()
            string = self.making_go_board_strings_helper(piece)
            list_of_piece_strings.append(string)
            piece_set -= string
        for item in list_of_piece_strings:
            item2 = item.pop()
            item.add(item2)
            sets = self.flood_fill(item2)
            self.assignment_logic(sets, window)

    def assignment_logic(self, sets, window):
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
            for item in pieces_string:
                self.update_both_boards(window, item, unicode_choice)
        return

    def flood_fill(self, piece, connected_pieces=None):
        if connected_pieces is None:
            connected_pieces = (set(), set())
        connected_pieces[0].add(piece)
        neighboring_pieces = self.check_neighbors(piece)

        for coordinate in neighboring_pieces:
            neighbor = self.board[coordinate[0]][coordinate[1]]
            if neighbor.stone_here_color == piece.stone_here_color and neighbor not in connected_pieces[0]:
                self.flood_fill(neighbor, connected_pieces)
            else:
                connected_pieces[1].add(neighbor)
                pass
        return connected_pieces


def load_and_parse_file(file):
    with open(file, 'r', encoding='utf-8') as file:
        import json
        data_to_parse = json.load(file)
    return data_to_parse


def initializing_game(window, board_size, defaults=True, file_import_option=False, fixes_handicap=False, choosen_file=None):
    info = "Click yes if you want to modify the player names and komi"
    if not defaults:
        only_modify_name = (sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15)))
        if only_modify_name == "No":
            GameBoard = GoBoard(board_size, True)
        else:
            GameBoard = GoBoard(board_size, defaults)
    else:
        GameBoard = GoBoard(board_size, defaults)
    if file_import_option:
        GameBoard.load_from_json(choosen_file)
    window.close()
    window2 = ui.setup_board_window(GameBoard)
    info = "Click yes if you want to modify the handicap"
    if fixes_handicap:
        modify_handicap = (sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15)))
        if modify_handicap == "Yes":
            GameBoard.play_game(window2, file_import_option, fixes_handicap=True)
        else:
            GameBoard.play_game(window2, file_import_option, fixes_handicap=False)

    else:
        GameBoard.play_game(window2, file_import_option, fixes_handicap)
