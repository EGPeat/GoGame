import uifunctions as ui
import PySimpleGUI as sg


class Player():
    def __init__(self, name=None, color=None, captured=0, komi=0, unicode_choice=None):
        self.name = name
        self.color = color
        self.captured = captured
        self.komi = komi
        self.unicode = unicode_choice

    def choose_name(self):
        info = "Please Click Yes if you want to change your name"
        modify_name = sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))
        if modify_name == "No":
            if self.color == "Black":
                self.name = "Player One"
                return
            else:
                self.name = "Player Two"
                return
        info = "Please Enter a name you would like to use, but keep it less than 30 characters:"
        while self.name is None:
            try:
                player_name = ui.validation_gui(info, str)
                if len(player_name) > 30:
                    raise SyntaxError
                self.name = player_name

                break
            except SyntaxError:
                info2 = "It seems you entered a name longer than 30 characters. Please try again"
                sg.popup_no_buttons(info2, non_blocking=True, font=('Arial Bold', 15),
                                    auto_close=True, auto_close_duration=2)

    def choose_komi(self):
        info = "Please Click Yes if you want to change your Komi"
        modify_komi = sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))
        if modify_komi == "No":
            if self.color == "Black":
                self.komi = 0
                return
            else:
                self.komi = 6.5
                return
        done = False

        while self.komi == 0 and done is not True:
            try:
                info = f"Your color is {self.color}. Please enter Komi Value. 6.5 is normally done, but only for white:"
                komi_value = ui.validation_gui(info, float)
                self.komi = komi_value
                break
            except ValueError:
                info2 = "It seems you entered something that isn't a float. Please try again"
                sg.popup_no_buttons(info2, non_blocking=True, font=('Arial Bold', 15),
                                    auto_close=True, auto_close_duration=2)


unicodePrint = {
    "Black": u"\u26AB",
    "White": u"\u26AA",
    "None": u"\U0001F7E9",
    "BlackTriangle": u"\u25B2",
    "WhiteTriangle": u"\u25B3",
    "DiamondBlack": u"\u25C6",
    "DiamondWhite": u"\u25C7"
}
unicode_black = unicodePrint["Black"]
unicode_white = unicodePrint["White"]
unicode_none = unicodePrint["None"]
unicode_triangle_black = unicodePrint["BlackTriangle"]
unicode_triangle_white = unicodePrint["WhiteTriangle"]
unicode_diamond_black = unicodePrint["DiamondBlack"]  # represents dead pieces
unicode_diamond_white = unicodePrint["DiamondWhite"]

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
        self.board = self.setup_board()
        self.player_black = self.setup_player(self.defaults, color="Black")
        self.player_white = self.setup_player(self.defaults, color="White")
        self.times_passed = 0
        self.turn_num = 0
        self.position_played_log = list()  # (-1,-1) shows the boundary between a handicap and normal play
        self.visit_kill = set()
        self.killed_last_turn = set()  # Potentially unneeded
        self.killed_log = list()
        self.handicap = self.default_handicap()

    # This sets up the board variable of the GoBoard class, initializing as appropriate
    def setup_board(self):
        board_assign = [[BoardNode() for i in range(self.board_size)] for j in range(self.board_size)]

        for row in range(self.board_size):
            for col in range(self.board_size):
                board_assign[row][col].change_boardnode_value('row', row)
                board_assign[row][col].change_boardnode_value('col', col)

        return board_assign

    # This sets up the Player class, assigning appropriate values to each player as needed
    def setup_player(self, defaults, color):
        if defaults:
            if color == "Black":
                player_assignment = Player(name="Player One", color="Black", unicode_choice=unicode_black)
            else:
                player_assignment = Player(name="Player Two", color="White", komi=6.5, unicode_choice=unicode_white)
        else:
            if color == "Black":
                player_assignment = Player(color="Black", unicode_choice=unicode_black)
                player_assignment.choose_name()
                player_assignment.choose_komi()
            else:
                player_assignment = Player(color="White", unicode_choice=unicode_white)
                player_assignment.choose_name()
                player_assignment.choose_komi()
        return player_assignment

# By default there should not be any handicap.
    def default_handicap(self):
        return (False, "None", 0)

# Sets up a custom handicap using a CLI.
# Work On adding a GUI solution for this. Maybe add an option for default placement of stones, or custom.
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
            player = self.player_black
        elif player_choice == "White":
            player = self.player_white
        else:
            return (False, "None", 0)
        handicap_info = ui.handicap_number_gui(self.board_size)
        if manual_handicap == "No":
            for idx in range(handicap_info):
                row, col = choosen_list[idx]
                window[(row, col)].update(player.unicode)
                self.play_piece(row, col, player, window)
                self.refresh_board(window)
        else:
            self.manual_handicap_placement(window, handicap_info, player)
        self.refresh_board(window)
        self.position_played_log.append(("Break between handicaps and normal play", -1, -1))
        self.turn_num = 0
        return (True, player.color, handicap_info)

    def manual_handicap_placement(self, window, handicap_info, player):
        for idx in range(handicap_info):
            txt = f"Please place {handicap_info} number of pieces where you wish,\
                    as a handicap. Do not press undo. Then the opponent will play."
            sg.popup(txt, line_width=42, auto_close=True, auto_close_duration=3)
            event, values = window.read()
            while event == "Pass Turn" or event == "Save Game" or event == "Undo Turn" or event == "Exit Game":
                if event == "Undo Turn":
                    sg.popup("You can't undo during the handicap stage.",
                             line_width=42, auto_close=True, auto_close_duration=3)
                elif event == "Pass Turn" or event == "Save Game" or event == "Exit Game":
                    self.turn_options(window, event, player)
            window[event].update(player.unicode)

            self.play_piece(event[0], event[1], player, window)
            self.refresh_board(window)

    def play_game(self, window, fromFile=False, fixes_handicap=False):

        if fixes_handicap is True:
            self.handicap = self.custom_handicap(False, window)
        if fromFile is not True:
            self.setup_board()
        else:
            self.refresh_board(window)
            if self.position_played_log[-1][0] == "Black":
                self.play_turn(window, self.player_white)

        while (self.times_passed <= 1):
            if self.turn_num % 2 == 0:
                self.play_turn(window, self.player_black)
            else:
                self.play_turn(window, self.player_white)
        self.end_of_game(window)

    def play_turn(self, window, choosen_player):
        truth_value = False
        while not truth_value:
            event, values = window.read()
            if event == "Pass Turn":
                self.turn_options(window, event, choosen_player)
                return
            elif event == "Save Game" or event == "Undo Turn" or event == "Exit Game":
                self.turn_options(window, event, choosen_player)
            else:
                row = int(event[0])
                col = int(event[1])

                self.times_passed = 0
                truth_value = self.play_piece(row, col, choosen_player, window)
                if truth_value:
                    window[event].update(choosen_player.unicode)
        ui.update_scoring(self, window, choosen_player)

        temp_list = list()
        for item in self.killed_last_turn:
            if choosen_player == self.player_black:
                temp_list.append((self.player_white.unicode, item.row, item.col))
            else:
                temp_list.append((self.player_black.unicode, item.row, item.col))
        self.killed_log.append(temp_list)
        return

    def turn_options(self, window, event, choosen_player):
        if event == "Pass Turn":
            sg.popup("Skipped turn", line_width=42, auto_close=True, auto_close_duration=3)
            self.times_passed += 1
            self.turn_num += 1
            self.position_played_log.append((f"{choosen_player.color} passed", -2, -2))
            ui.update_scoring(self, window, choosen_player)
            return
        elif event == "Save Game":
            self.save_to_json()
        elif event == "Undo Turn":
            if self.turn_num == 0:
                sg.popup("You can't undo when nothing has happened.", line_width=42, auto_close=True, auto_close_duration=3)
            elif self.turn_num == 1:
                self.undo_turn(window)
                ui.update_scoring(self, window, choosen_player)
                choosen_player = self.player_black
            else:
                self.undo_turn(window)
                self.undo_turn(window)
                ui.update_scoring(self, window, choosen_player)
        elif event == "Exit Game":
            from main import play_game_main
            window.close()
            play_game_main()
            quit()

    def play_piece(self, row, col, which_player, window):
        piece = self.board[row][col]
        suicidal_liberty_value = 0
        if (piece.stone_here_color != unicode_none):
            sg.popup("You tried to place where there is already a piece. Please try your turn again.",
                     line_width=42, auto_close=True, auto_close_duration=3)
            return False
        elif (self.turn_num > 2 and self.ko_rule_break(piece, which_player) is True):
            sg.popup("Place the piece there would break the ko rule. Please try your turn again.",
                     line_width=42, auto_close=True, auto_close_duration=3)
            return False
        elif (self.kill_stones(piece, which_player, window) is True):
            piece.stone_here_color = which_player.unicode
            self.turn_num += 1
            self.position_played_log.append((which_player.color, row, col))
            return True
        elif (self.suicide(piece, which_player) == suicidal_liberty_value):
            sg.popup("Placing the piece there would commit suicide. Please try your turn again.",
                     line_width=42, auto_close=True, auto_close_duration=3)
            return False

        else:  # No rules or special cases are broken, play piece as normal.
            self.position_played_log.append((which_player.color, row, col))
            piece.stone_here_color = which_player.unicode
            self.killed_last_turn.clear()

        self.turn_num += 1
        return True

    def undo_turn(self, window):
        color, row, col = self.position_played_log.pop()
        self.board[row][col].stone_here_color = unicode_none
        window[(row, col)].update("")

        # This part reverts the board back to its state 1 turn ago
        revive = self.killed_log.pop()
        capture_update_val = len(revive)
        if len(revive) > 0:
            unicode = revive[1][0]
        else:
            unicode = unicode_none
        for item in revive:
            unicode, row, col = item
            self.board[row][col].stone_here_color = unicode
            window[(row, col)].update(unicode)

        # This part updates some class values (player captures, killed_last_turn, turn_num)
        self.turn_num -= 1
        if unicode == unicode_black:
            self.player_white.captured -= capture_update_val
        elif unicode == unicode_white:
            self.player_black.captured -= capture_update_val
        if len(self.killed_log) > 0:
            self.killed_last_turn.clear()
            temp_list = self.killed_log[-1]
            for item in temp_list:
                temp_node = BoardNode(row_value=item[1], col_value=item[2])
                self.killed_last_turn.add(temp_node)

    def ko_rule_break(self, piece, which_player):
        if self.suicide(piece, which_player) > 0:
            return False
        if piece in self.killed_last_turn:
            return True
        return False

    def check_neighbors(self, piece):
        neighbors = [(piece.row - 1, piece.col), (piece.row + 1, piece.col),
                     (piece.row, piece.col - 1), (piece.row, piece.col + 1)]
        valid_neighbors = []
        for coordinate in neighbors:
            if 0 <= coordinate[0] < self.board_size and 0 <= coordinate[1] < self.board_size:
                valid_neighbors.append(coordinate)
        return valid_neighbors

    # Uses BFS to figure out liberties and connected pieces of the same type
    def suicide(self, piece, which_player, visited=None):
        if visited is None:
            visited = set()
        visited.add(piece)
        neighbors = self.check_neighbors(piece)
        liberties = 0
        for coordinate in neighbors:
            neighboring_piece = self.board[coordinate[0]][coordinate[1]]
            if neighboring_piece.stone_here_color == unicode_none:
                liberties += 1
            elif neighboring_piece.stone_here_color != which_player.unicode:
                pass
            elif neighboring_piece not in visited:
                liberties += self.suicide(neighboring_piece, which_player, visited)
        self.visit_kill = visited
        return liberties

    # This takes in the player who is gaining the captured pieces
    def remove_stones(self, choosen_player, window):
        self.killed_last_turn.clear()
        for position in self.visit_kill:
            self.killed_last_turn.add(position)
            choosen_player.captured += 1
            position.stone_here_color = unicode_none
            window[(position.row, position.col)].update(' ')

    def end_of_game(self, window):
        ui.end_game_popup(self)
        self.counting_territory(window)
        event, values = window.read()
        truth_value = False
        while not truth_value:
            event, values = window.read()
            if event == "Pass Turn":
                pass
            elif event == "Save Game":
                self.save_to_json()
                event, values = window.read()
                if event == "Exit Game":
                    quit()
            elif event == "Exit Game":
                quit()
    
    def counting_territory(self, window):
        empty_space_set, black_set, white_set = set(), set(), set()
        for xidx in range(self.board_size):
            for yidx in range(self.board_size):
                temp_node = self.board[xidx][yidx]
                if temp_node.stone_here_color == unicode_white:
                    white_set.add(temp_node)
                elif temp_node.stone_here_color == unicode_black:
                    black_set.add(temp_node)
                else:
                    empty_space_set.add(temp_node)
        print(f"empty_space_set {len(empty_space_set)}, black_set {len(black_set)}, white_set {len(white_set)}")
        black_set_alive_dead = set()
        #while len(black_set) > 0:
        life_value, grouping = self.finding_eyes(black_set, self.player_black)
        print(life_value)
        print(grouping)
        if life_value == "Alive":
            for item in grouping:
                black_set_alive_dead[0].add(item)
        else:
            for item in grouping:
                black_set_alive_dead[1].add(item)


    def finding_eyes(self, piece_set, which_player):#add something for finding dead/killable shapes
        #https://senseis.xmp.net/?KillingShapes
        piece = self.board[7][7] # change
        print(piece)
        double_set = self.helper_finding_shapes(piece, which_player)

        #piece = piece_set.pop()
        #piece_set.add(piece)
        #double_set = self.helper_finding_shapes(piece, which_player)
        #for item in double_set[0]:
        #   group_set.add(item)
        for item in double_set[0]:
            print(item)
        for item in double_set[1]:
            print(item)
        eyes = 0
        liberties = 0
        while len(double_set[1]):
            item = double_set[1].pop()
            double_set[1].add(item)
            set_of_spaces = self.helper_finding_eyes(item, which_player)
            eyes += 1
            liberties += len(set_of_spaces)
            print(f"testing set of spaces, with len left of {len(double_set[1])}, eyes of {eyes} and liberties of {liberties}")
            for item in set_of_spaces[1]: #1 or 0?
                print(f"item is {item}")
                
                double_set[1].remove(item)
        if eyes >= 2 or liberties >= 3:
            return "Alive", double_set[0]



    #this finds and makes a set of connected pieces of a certain color, as well as a set of empty spaces nearby
    def helper_finding_shapes(self, piece, which_player, connected_empty_sets=None):

        if connected_empty_sets is None:
            connected_empty_sets = (set(), set())  
        connected_empty_sets[0].add(piece)
        neighbors = self.check_neighbors(piece)

        for coordinate in neighbors:
            neighboring_piece = self.board[coordinate[0]][coordinate[1]]
            if neighboring_piece.stone_here_color == unicode_none:
                connected_empty_sets[1].add(neighboring_piece)
            elif neighboring_piece.stone_here_color != which_player.unicode:
                pass
            elif neighboring_piece not in connected_empty_sets[0]:
                self.helper_finding_shapes(neighboring_piece, which_player, connected_empty_sets)
        return connected_empty_sets
    
    def helper_finding_eyes(self, piece, which_player, eye_set=None):
        if eye_set is None:
            eye_set = (set(), set())  
            # Set of verified good connected spaces, set of all connected spaces
        eye_set[0].add(piece)
        eye_set[1].add(piece)
        neighbors = self.check_neighbors(piece)
        already_removed = False
        for coordinate in neighbors:
            neighboring_piece = self.board[coordinate[0]][coordinate[1]]
            which_player_check = neighboring_piece.stone_here_color != which_player.unicode
            check_unicode_none = neighboring_piece.stone_here_color != unicode_none
            if which_player_check and check_unicode_none and already_removed == False:
                eye_set[0].remove(piece)
                already_removed = True
                pass
            elif which_player_check and check_unicode_none:
                pass
            elif neighboring_piece not in eye_set[1]:
                self.helper_finding_shapes(neighboring_piece, which_player, eye_set)
        return eye_set
        
        
        
        
        
        
                
    def kill_stones(self, piece, which_player, window):  # needs to return true if it does kill stones
        piece.stone_here_color = which_player.unicode
        neighbors = self.check_neighbors(piece)
        truth_value = False
        if which_player == self.player_black:
            not_which_player = self.player_white
        else:
            not_which_player = self.player_black

        for coordinate in neighbors:
            neighboring_piece = self.board[coordinate[0]][coordinate[1]]
            if neighboring_piece.stone_here_color == not_which_player.unicode:
                if (self.suicide(neighboring_piece, not_which_player) == 0):
                    self.remove_stones(which_player, window)
                    truth_value = True
        if truth_value is False:
            piece.stone_here_color = unicode_none
        return truth_value

    def save_to_json(self):
        import json
        filename = ''
        while len(filename) < 1:
            text = "Please write the name of the txt file you want to save to. Do not include '.txt' in what you write"
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
                "places_on_board": places_on_board
            }
            json_object = json.dumps(dictionary_to_json, indent=4)
            file.write(json_object)
        sg.popup(f"Saved to {filename}.json", line_width=42, auto_close=True, auto_close_duration=3)

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

        self.player_white.name = data["player_white.name"]
        self.player_white.color = data["player_white.color"]
        self.player_white.captured = data["player_white.captured"]
        self.player_white.komi = data["player_white.komi"]
        self.player_white.unicode = data["player_white.unicode"]
        board_list = data["places_on_board"]
        for item in board_list:
            bxidx, byidx, bcolor = item
            self.board[bxidx][byidx].stone_here_color = f"{bcolor}"

    def refresh_board(self, window):
        for xidx in range(self.board_size):
            for yidx in range(self.board_size):
                if not self.board[xidx][yidx].stone_here_color == "\U0001F7E9":
                    window[(xidx, yidx)].update(self.board[xidx][yidx].stone_here_color)


def load_and_parse_file(file):
    with open(file, 'r', encoding='utf-8') as file:
        import json
        data_to_parse = json.load(file)
    return data_to_parse


def initializing_game(window, board_size, defaults=True, file_import_option=False,
                      from_file=False, fixes_handicap=False, choosen_file=None):
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
