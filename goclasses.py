from uifunctions import p, input_value, setup_board_window
import os.path
import ast
import PySimpleGUI as sg


class Player():
    def __init__(self, name=None, color=None, captured=0, komi=0):
        self.name = name
        self.color = color
        self.captured = captured
        self.komi = komi

    def choose_name(self):
        info = "Please Enter a name you would like to use, but keep it less than 30 characters:"
        while self.name is None:
            try:
                player_name = str(sg.popup_get_text(info, title="Please Enter Text", font=('Arial Bold', 15)))
                if len(player_name) > 30:
                    raise SyntaxError
                self.name = player_name

                break
            except SyntaxError:
                info = "It seems you entered a name longer than 30 characters. Please try again"

    def choose_komi(self):
        done = False
        info = f"Your color is {self.color}. Please enter Komi Value. 6.5 is normally done, but only for white:"
        while self.komi == 0 and done is not True:
            try:
                komi_value = float(sg.popup_get_text(info, title="Please Enter Text", font=('Arial Bold', 15)))
                self.komi = komi_value
                break
            except ValueError:
                info = "It seems you entered something that isn't a float. Please try again"


unicodePrint = {
    "Black": u" \u26AB ",
    "White": u" \u26AA ",
    "None": u" \U0001F7E9 "
}
unicode_black = unicodePrint["Black"]
unicode_white = unicodePrint["White"]
unicode_none = unicodePrint["None"]


class BoardNode():
    def __init__(self, row_value=None, col_value=None):
        self.row = row_value
        self.col = col_value
        self.stone_here_color = unicode_none

    # Allows for updating a specific variable in the BoardNode class
    def change_boardnode_value(self, class_value, value):
        if hasattr(self, class_value):
            setattr(self, class_value, value)
        else:
            p("No attribute for that")


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
        self.killed_last_turn = set()
        self.handicap = self.default_handicap()

    def print_board(self):
        p(f"This is the board at turn {self.turn_num}")
        row_num = '      '

        for col in range(self.board_size):

            if (col < 10):
                row_num += f"0{col}  "
            else:
                row_num += f"{col}  "
        p(row_num)

        for row in range(self.board_size):
            print_row = ''
            if (row < 10):
                print_row += f"0{row}   "
            else:
                print_row += f"{row}   "
            for col in range(self.board_size):
                print_row += self.board[row][col].stone_here_color
            p(print_row)

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
                player_assignment = Player(name="Player One", color="Black")
            else:
                player_assignment = Player(name="Player Two", color="White", komi=6.5)
        else:
            if color == "Black":
                player_assignment = Player(color="Black")
                player_assignment.choose_name()
                player_assignment.choose_komi()
            else:
                player_assignment = Player(color="White")
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
        done = False
        handicap_points9 = [(2, 6), (6, 2), (6, 6), (2, 2), (4, 4)]
        handicap_points13 = [(3, 9), (9, 3), (9, 9), (3, 3), (6, 6), (6, 3), (6, 9), (3, 6), (9, 6)]
        handicap_points17 = [(3, 13), (13, 3), (13, 13), (3, 3), (8, 8), (8, 3), (8, 13), (3, 8), (13, 8)]
        info = "Please enter some information regarding a handicap.\n\
          For the 100s place write 1 if there should be no handicap, or 2 if there should \n\
          For the 10s place, write 1 for Black getting the handicap, or 2 for white getting it\n\
          For the 1s place, please enter the number of stones the handicap should be\n\
          An example would be 212, meaning there is a handicap, black has it, and black gets 2 stones\n\
          Warning. If you have choosen a 9x9 board, you can have only a 5 piece handicap max"

        while done is not True:
            try:
                sg.popup(info, line_width=42)
                handicap_info = int(sg.popup_get_text("Enter number", title="Please Enter Text", font=('Arial Bold', 15)))

                if handicap_info % 10 > 5 and self.board_size == 9:
                    raise ValueError
                done = True
            except ValueError:
                p("It seems you entered something that isn't correct. Please try again")
        if handicap_info < 200:
            return (False, 0, 0)  # Handicap, player, number of pieces
        handicap_info %= 100
        if handicap_info < 20:
            player = "Black"
        else:
            player = "White"
        handicap_info %= 10
        info = f"Please place {handicap_info} number of pieces where you wish, as a handicap. Then the opponent will play."
        sg.popup(info, line_width=42)
        choosen_list = handicap_points17
        if self.board_size == 9:
            choosen_list = handicap_points9
        elif self.board_size == 13:
            choosen_list = handicap_points13
        for idx in range(handicap_info):
            row, col = choosen_list[idx]  # WorkOn. Change it for allowing players to play where they want
            event, values = window.read()
            if player == "Black":
                window[event].update('\u26AB')
            if player == "White":
                window[event].update('\u26AA')

            self.play_piece(event[0], event[1], player, window)
        self.position_played_log.append(("Break between handicaps and normal play", -1, -1))
        self.turn_num = 0
        return (True, player, handicap_info)

    def play_game(self, window, fromFile=False, fixes_handicap=False):

        if fixes_handicap is True:
            self.handicap = self.custom_handicap(False, window)
        if fromFile is not True:
            self.setup_board()
        else:
            if self.position_played_log[-1][0] == "Black":
                self.play_turn(window, self.player_white.color)

        if self.handicap[0] is True and self.handicap[1] == "Black" and self.turn_num == 0:
            self.play_turn(window, self.player_white.color)

        while (self.times_passed <= 1):
            self.play_turn(window, self.player_black.color)
            if self.times_passed == 2:
                break
            self.play_turn(window, self.player_white.color)

        self.end_of_game(window)

    def play_turn(self, window, choosen_player):
        truth_value = False
        while not truth_value:
            event, values = window.read()
            if event == "Press After Loading From File":
                for xidx in range(self.board_size):
                    for yidx in range(self.board_size):
                        if not self.board[xidx][yidx].stone_here_color == " \U0001F7E9 ":
                            window[(xidx, yidx)].update(self.board[xidx][yidx].stone_here_color)
            elif event == "Pass Turn":
                sg.popup("skipped turn", line_width=42)
                self.times_passed += 1
                self.turn_num += 1
                self.position_played_log.append((f"{choosen_player} passed", -2, -2))
                return
            elif event == "Save Game":
                self.save_to_file()
            elif event == "Exit Game":
                quit()  # add different functionality
            else:
                row = int(event[0])
                col = int(event[1])

                self.times_passed = 0
                truth_value = self.play_piece(row, col, choosen_player, window)
                if truth_value and choosen_player == "Black":
                    window[event].update('\u26AB')
                if truth_value and choosen_player == "White":
                    window[event].update('\u26AA')

        return

    def play_piece(self, row, col, which_player, window):
        piece = self.board[row][col]
        if (piece.stone_here_color != unicode_none):
            sg.popup("You tried to place where there is already a piece. Please try your turn again.", line_width=42)
            return False
        elif (self.turn_num > 2 and self.ko_rule_break(piece) is True):
            sg.popup("Place the piece there would break the ko rule. Please try your turn again.", line_width=42)
            return False
        elif (self.kill_stones(piece, which_player, window) is True):
            print(which_player)
            if which_player == "Black":
                piece.stone_here_color = unicode_black
            else:
                piece.stone_here_color = unicode_white
            self.turn_num += 1
            self.position_played_log.append((which_player, row, col))
            self.killed_last_turn.clear()
            return True
        elif (self.suicide(piece, which_player) == 0):  # This returns the number of liberties. 0 would mean suicide.
            sg.popup("Placing the piece there would commit suicide. Please try your turn again.", line_width=42)
            return False

        else:  # No rules or special cases are broken, play piece as normal.
            self.position_played_log.append((which_player, row, col))

            if which_player == "Black":
                piece.stone_here_color = unicode_black
            else:
                piece.stone_here_color = unicode_white
        self.killed_last_turn.clear()
        self.turn_num += 1
        return True

    def ko_rule_break(self, piece):
        if piece in self.killed_last_turn and len(self.killed_last_turn) == 1:  # The second condition might be a problem
            return True
        return False

    def check_neighbors(self, piece):
        neighbors = [(piece.row - 1, piece.col), (piece.row + 1, piece.col),
                     (piece.row, piece.col - 1), (piece.row, piece.col + 1)]
        validNeighbors = []
        for coordinate in neighbors:
            if 0 <= coordinate[0] < self.board_size and 0 <= coordinate[1] < self.board_size:
                validNeighbors.append(coordinate)
        return validNeighbors

    def suicide(self, piece, which_player, visited=None):
        if visited is None:
            visited = set()
        visited.add(piece)
        neighbors = self.check_neighbors(piece)
        liberties = 0

        for coordinate in neighbors:
            neighboring_piece = self.board[coordinate[0]][coordinate[1]]
            if neighboring_piece.stone_here_color == unicodePrint["None"]:
                liberties += 1
            elif neighboring_piece.stone_here_color != unicodePrint[which_player]:
                pass
            elif neighboring_piece not in visited:
                liberties += self.suicide(neighboring_piece, which_player, visited)
        self.visit_kill = visited
        return liberties

    def remove_stones(self, choosen_player, window):  # take in the player who is gaining the pieces   
        if choosen_player == "Black":
            player = self.player_black
        else:
            player = self.player_white
        for position in self.visit_kill:
            self.killed_last_turn.add(position)
            player.captured += 1
            position.stone_here_color = unicodePrint["None"]
            window[(position.row, position.col)].update(' ')

    def end_of_game(self, window):
        info = f"Your game has finished. Congrats.\nPlayer Black: {self.player_black.name} captured \
            {self.player_black.captured} and has a komi of {self.player_black.komi}\n Player White: {self.player_white.name}\
                captured {self.player_white.captured} and has a komi of {self.player_white.komi}\
                \n Player Black has a score of {self.player_black.komi+self.player_black.captured-self.player_white.captured}\n\
            Player Black has a score of {self.player_white.komi+self.player_white.captured-self.player_black.captured}\n\
            This code cannot calculate territory or dead stones, so please\
                do that yourself\nPlease save your game to a file or exit the program."
        sg.popup(info, line_width=200)
        event, values = window.read()
        truth_value = False
        while not truth_value:
            event, values = window.read()
            if event == "Pass Turn":
                pass
            elif event == "Save Game":
                self.save_to_file()
                event, values = window.read()
                if event == "Exit Game":
                    quit()
            elif event == "Exit Game":
                quit()

    def kill_stones(self, piece, which_player, window):  # needs to return true if it does kill stones
        if which_player == "Black":
            piece.stone_here_color = unicode_black
        else:
            piece.stone_here_color = unicode_white

        neighbors = self.check_neighbors(piece)
        not_which_player = ''
        truth_value = False
        if which_player == "Black":
            not_which_player = "White"
        else:
            not_which_player = "Black"
        for coordinate in neighbors:
            neighboring_piece = self.board[coordinate[0]][coordinate[1]]
            if neighboring_piece.stone_here_color == unicodePrint[not_which_player]:
                if (self.suicide(neighboring_piece, not_which_player) == 0):
                    self.remove_stones(which_player, window)
                    truth_value = True
        if truth_value is False:
            piece.stone_here_color = unicode_none
        return truth_value

    def save_to_file(self):  # Change this to json
        text = "Please write the name of the txt file you want to save to. Do not include '.txt' in what you write"
        filename = (sg.popup_get_text(text, title="Please Enter Text", font=('Arial Bold', 15)))
        with open(f"{filename}.txt", 'w', encoding='utf-8') as file:
            file.write(f"{self.board_size}; {self.defaults}; {self.times_passed}; \
                {self.turn_num}; {self.handicap}; {self.position_played_log}\n")
            file.write(f"{self.player_black.name}; {self.player_black.color}; \
                {self.player_black.captured}; {self.player_black.komi}\n")
            file.write(f"{self.player_white.name}; {self.player_white.color}; \
                {self.player_white.captured}; {self.player_white.komi}\n")
            for row in range(self.board_size):
                print_row = ''
                for col in range(self.board_size):
                    print_row += self.board[row][col].stone_here_color
                file.write(print_row + '\n')
        sg.popup(f"Saved to {filename}.txt", line_width=42)

    def load_from_file(self, inputAlr=False, inputPath=''):  # change this to loading from json
        foundFile = False
        if inputAlr is False:
            while foundFile is False:
                path_filename = f"{input_value(30, str)}.txt"
                if os.path.isfile(path_filename):
                    foundFile = True
                # else:
                    # p("You have entered a filename that doesn't exist, please try inputing again. Don't write the .txt")
        else:
            path_filename = inputPath
        with open(path_filename, 'r', encoding='utf-8') as file:
            data_to_parse = [line.rstrip() for line in file]
            data_to_parse = [line.split('; ') for line in data_to_parse]

            self.board_size = int(data_to_parse[0][0])  # change it to a list assignment?
            self.defaults = data_to_parse[0][1]
            self.times_passed = int(data_to_parse[0][2])
            self.turn_num = int(data_to_parse[0][3])
            self.handicap = data_to_parse[0][4]
            self.position_played_log = list(ast.literal_eval(data_to_parse[0][5]))
            del data_to_parse[0]

            self.player_black.name = data_to_parse[0][0]
            self.player_black.color = data_to_parse[0][1]
            self.player_black.captured = int(data_to_parse[0][2])
            self.player_black.komi = float(data_to_parse[0][3])
            del data_to_parse[0]

            self.player_white.name = data_to_parse[0][0]
            self.player_white.color = data_to_parse[0][1]
            self.player_white.captured = int(data_to_parse[0][2])
            self.player_white.komi = float(data_to_parse[0][3])
            del data_to_parse[0]

            for idx in range(len(data_to_parse)):
                data_to_parse[idx] = data_to_parse[idx][0].split('  ')

            for xidx in range(self.board_size):
                for yidx in range(self.board_size):
                    if yidx == 0:
                        self.board[xidx][yidx].stone_here_color = f"{data_to_parse[xidx][yidx]} "
                    else:
                        self.board[xidx][yidx].stone_here_color = f" {data_to_parse[xidx][yidx]} "


def load_and_parse_file(file):
    with open(file, 'r', encoding='utf-8') as file:
        data_to_parse = [line.rstrip() for line in file]
        data_to_parse = [line.split('; ') for line in data_to_parse]
    return data_to_parse


def initializing_game(window, board_size, defaults=True, file_import_option=False,
                      from_file=False, fixes_handicap=False, choosen_file=None):
    GameBoard = GoBoard(board_size, defaults=True)
    if file_import_option:
        GameBoard.load_from_file(True, choosen_file)
    window.close()
    window2 = setup_board_window(GameBoard)
    GameBoard.play_game(window2, file_import_option, fixes_handicap)
