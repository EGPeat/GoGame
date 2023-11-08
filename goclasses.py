from uifunctions import p, input_value
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
                playerName = str(sg.popup_get_text(info, title="Please Enter Text", font=('Arial Bold', 15)))
                if len(playerName) > 30:
                    raise SyntaxError
                self.name = playerName

                break
            except SyntaxError:
                info = "It seems you entered a name longer than 30 characters. Please try again"

    def choose_komi(self):
        done = False
        info = f"Your color is {self.color}. Please enter Komi Value. 6.5 is normally done:"
        while self.komi == 0 and done is not True:
            try:
                komiVal = float(sg.popup_get_text(info, title="Please Enter Text", font=('Arial Bold', 15)))
                self.komi = komiVal
                break
            except ValueError:
                info = "It seems you entered something that isn't a float. Please try again"


unicodePrint = {
    "Black": u" \u26AB ",
    "White": u" \u26AA ",
    "None": u" \U0001F7E9 "
}
unicodeBlack = unicodePrint["Black"]
unicodeWhite = unicodePrint["White"]
unicodeNone = unicodePrint["None"]


class BoardNode():
    def __init__(self, rowVal=None, colVal=None):
        self.row = rowVal
        self.col = colVal
        self.stoneHereColor = unicodeNone

    # Allows for updating a specific variable in the BoardNode class
    def change_boardnode_value(self, classValue, value):
        if hasattr(self, classValue):
            setattr(self, classValue, value)
        else:
            p("No attribute for that")


class GoBoard():
    def __init__(self, boardSize=17, defaults=True):
        self.boardSize = boardSize
        self.defaults = defaults
        self.board = self.setup_board()
        self.playerBlack = self.setup_player(self.defaults, color="Black")
        self.playerWhite = self.setup_player(self.defaults, color="White")
        self.timesPassed = 0
        self.turnNum = 0
        self.positionPlayedLog = list()  # (-1,-1) shows the boundary between a handicap and normal play
        self.visitKill = set()
        self.handicap = self.default_handicap()

    def print_board(self):
        p(f"This is the board at turn {self.turnNum}")
        numRow = '      '

        for col in range(self.boardSize):

            if (col < 10):
                numRow += f"0{col}  "
            else:
                numRow += f"{col}  "
        p(numRow)

        for row in range(self.boardSize):
            rowPrint = ''
            if (row < 10):
                rowPrint += f"0{row}   "
            else:
                rowPrint += f"{row}   "

            # rowPrint=f'{row} '
            for col in range(self.boardSize):
                rowPrint += self.board[row][col].stoneHereColor
            p(rowPrint)

    # This sets up the board variable of the GoBoard class, initializing as appropriate
    def setup_board(self):
        boardAssign = [[BoardNode() for i in range(self.boardSize)] for j in range(self.boardSize)]

        for row in range(self.boardSize):
            for col in range(self.boardSize):
                boardAssign[row][col].change_boardnode_value('row', row)
                boardAssign[row][col].change_boardnode_value('col', col)

        return boardAssign

    # This sets up the Player class, assigning appropriate values to each player as needed
    def setup_player(self, defaults, color):
        if defaults:
            if color == "Black":
                playerAssign = Player(name="Player One", color="Black")
            else:
                playerAssign = Player(name="Player Two", color="White", komi=6.5)
        else:
            if color == "Black":
                playerAssign = Player(color="Black")
                playerAssign.choose_name()
                playerAssign.choose_komi()
            else:
                playerAssign = Player(color="White")
                playerAssign.choose_name()
                playerAssign.choose_komi()
        return playerAssign

    def default_handicap(self):
        return (False, "None", 0)

    def custom_handicap(self, defaults, window):
        if defaults is True:
            return (False, "None", 0)
        done = False
        handicapPoints9 = [(2, 6), (6, 2), (6, 6), (2, 2), (4, 4)]
        handicapPoints13 = [(3, 9), (9, 3), (9, 9), (3, 3), (6, 6), (6, 3), (6, 9), (3, 6), (9, 6)]
        handicapPoints17 = [(3, 13), (13, 3), (13, 13), (3, 3), (8, 8), (8, 3), (8, 13), (3, 8), (13, 8)]
        info = "Please enter some information regarding a handicap.\n\
          For the 100s place write 1 if there should be no handicap, or 2 if there should \n\
          For the 10s place, write 1 for Black getting the handicap, or 2 for white getting it\n\
          For the 1s place, please enter the number of stones the handicap should be\n\
          An example would be 212, meaning there is a handicap, black has it, and black gets 2 stones\n\
          Warning. If you have choosen a 9x9 board, you can have only a 5 piece handicap max"

        while done is not True:
            try:
                sg.popup(info, line_width=42)
                handicapInfo = int(sg.popup_get_text("Enter number", title="Please Enter Text", font=('Arial Bold', 15)))

                if handicapInfo % 10 > 5 and self.boardSize == 9:
                    raise ValueError
                done = True
            except ValueError:
                p("It seems you entered something that isn't correct. Please try again")
        if handicapInfo < 200:
            return (False, 0, 0)  # Handicap, player, number of pieces
        handicapInfo %= 100
        if handicapInfo < 20:
            player = "Black"
        else:
            player = "White"
        handicapInfo %= 10
        choosenList = handicapPoints17
        if self.boardSize == 9:
            choosenList = handicapPoints9
        elif self.boardSize == 13:
            choosenList = handicapPoints13
        for idx in range(handicapInfo):
            row, col = choosenList[idx]
            event, values = window.read()
            if player == "Black":
                window[event].update('\u26AB')
            if player == "White":
                window[event].update('\u26AA')

            self.play_piece(event[0], event[1], player, window)
        self.positionPlayedLog.append(("Break between handicaps and normal play", -1, -1))
        self.turnNum = 0
        return (True, player, handicapInfo)

    def play_game(self, window, fromFile=False, fixesHandicap=False):

        if fixesHandicap is True:
            self.handicap = self.custom_handicap(False, window)
        if fromFile is not True:
            self.setup_board()
        else:
            if self.positionPlayedLog[-1][0] == "Black":
                self.play_turn(window, self.playerWhite.color)

        if self.handicap[0] is True and self.handicap[1] == "Black" and self.turnNum == 0:
            self.play_turn(window, self.playerWhite.color)

        while (self.timesPassed <= 1):
            self.play_turn(window, self.playerBlack.color)
            if self.timesPassed == 2:
                break
            self.play_turn(window, self.playerWhite.color)

        self.end_of_game(window)

    def play_turn(self, window, playerChoice):
        truthVal = False
        while not truthVal:
            event, values = window.read()
            if event == "Press After Loading From File":
                for xidx in range(self.boardSize):
                    for yidx in range(self.boardSize):
                        if not self.board[xidx][yidx].stoneHereColor == " \U0001F7E9 ":
                            window[(xidx, yidx)].update(self.board[xidx][yidx].stoneHereColor)
                event, values = window.read()
            elif event == "Pass Turn":
                sg.popup("skipped turn", line_width=42)
                self.timesPassed += 1
                self.turnNum += 1
                self.positionPlayedLog.append((f"{playerChoice} passed", -2, -2))
                return
            elif event == "Save Game":
                self.save_to_file()
                event, values = window.read()
                if event == "Exit Game":
                    quit()
            elif event == "Exit Game":
                quit()
            else:
                row = int(event[0])
                col = int(event[1])

                self.timesPassed = 0
                truthVal = self.play_piece(row, col, playerChoice, window)
                if truthVal and playerChoice == "Black":
                    window[event].update('\u26AB')
                if truthVal and playerChoice == "White":
                    window[event].update('\u26AA')

        return

    def play_piece(self, row, col, whichPlayer, window):
        piece = self.board[row][col]
        if (piece.stoneHereColor != unicodeNone):
            sg.popup("You tried to place where there is already a piece. Please try your turn again.", line_width=42)
            return False
        elif (self.turnNum > 2 and self.ko_rule_break(piece) is True):
            sg.popup("Place the piece there would break the ko rule. Please try your turn again.", line_width=42)
            return False
        elif (self.kill_stones(piece, whichPlayer, window) is True):
            if whichPlayer == "Black":
                piece.stoneHereColor = unicodeBlack
            else:
                piece.stoneHereColor = unicodeWhite
            self.turnNum += 1
            self.positionPlayedLog.append((whichPlayer, row, col))
            return True
        elif (self.suicide(piece, whichPlayer) == 0):
            sg.popup("Placing the piece there would commit suicide. Please try your turn again.", line_width=42)
            return False

        else:
            self.positionPlayedLog.append((whichPlayer, row, col))

            if whichPlayer == "Black":
                piece.stoneHereColor = unicodeBlack
            else:
                piece.stoneHereColor = unicodeWhite

        self.turnNum += 1
        return True

    def ko_rule_break(self, piece):
        player, row, col = self.positionPlayedLog[-2]
        if row < 0:
            return False
        koSpot = self.board[row][col]
        if piece == koSpot:
            return True

        return False

    def check_neighbors(self, piece):
        neighbors = [(piece.row - 1, piece.col), (piece.row + 1, piece.col),
                     (piece.row, piece.col - 1), (piece.row, piece.col + 1)]
        validNeighbors = []
        for coordinate in neighbors:
            if 0 <= coordinate[0] < self.boardSize and 0 <= coordinate[1] < self.boardSize:
                validNeighbors.append(coordinate)
        return validNeighbors

    def suicide(self, piece, whichPlayer, visited=None):
        if visited is None:
            visited = set()
        visited.add(piece)
        neighbors = self.check_neighbors(piece)
        liberties = 0

        for coordinate in neighbors:
            neighboring_piece = self.board[coordinate[0]][coordinate[1]]
            if neighboring_piece.stoneHereColor == unicodePrint["None"]:
                liberties += 1
            elif neighboring_piece.stoneHereColor != unicodePrint[whichPlayer]:
                pass
            elif neighboring_piece not in visited:
                liberties += self.suicide(neighboring_piece, whichPlayer, visited)
        self.visitKill = visited
        return liberties

    def remove_stones(self, player_player, window):  # take in the player who is gaining the pieces
        if player_player == "Black":
            player = self.playerBlack
        else:
            player = self.playerWhite
        for position in self.visitKill:
            player.captured += 1
            position.stoneHereColor = unicodePrint["None"]
            window[(position.row, position.col)].update(' ')

    def end_of_game(self, window):
        info = f"Your game has finished. Congrats.\nPlayer Black: {self.playerBlack.name} captured \
            {self.playerBlack.captured} and has a komi of {self.playerBlack.komi}\n\
            Player White: {self.playerWhite.name} captured {self.playerWhite.captured} and has a komi of {self.playerWhite.komi}\
                \n Player Black has a score of {self.playerBlack.komi+self.playerBlack.captured-self.playerWhite.captured}\n\
            Player Black has a score of {self.playerWhite.komi+self.playerWhite.captured-self.playerBlack.captured}\n\
            This code cannot calculate territory or dead stones, so please\
                do that yourself\nPlease save your game to a file or exit the program."
        sg.popup(info, line_width=200)
        event, values = window.read()
        truthVal = False
        while not truthVal:
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

    def kill_stones(self, piece, whichPlayer, window):  # needs to return true if it does kill stones
        if whichPlayer == "Black":
            piece.stoneHereColor = unicodeBlack
        else:
            piece.stoneHereColor = unicodeWhite

        neighbors = self.check_neighbors(piece)
        notWhichPlayer = ''
        truthVal = False
        if whichPlayer == "Black":
            notWhichPlayer = "White"
        else:
            notWhichPlayer = "Black"
        for coordinate in neighbors:
            neighboring_piece = self.board[coordinate[0]][coordinate[1]]
            if neighboring_piece.stoneHereColor == unicodePrint[notWhichPlayer]:
                if (self.suicide(neighboring_piece, notWhichPlayer) == 0):
                    self.remove_stones(whichPlayer, window)
                    truthVal = True
        if truthVal is False:
            piece.stoneHereColor = unicodeNone
        return truthVal

    def save_to_file(self):  # Change this to json
        text = "Please write the name of the txt file you want to save to. Do not include '.txt' in what you write"
        filename = (sg.popup_get_text(text, title="Please Enter Text", font=('Arial Bold', 15)))
        with open(f"{filename}.txt", 'w', encoding='utf-8') as file:
            file.write(f"{self.boardSize}; {self.defaults}; {self.timesPassed}; \
                {self.turnNum}; {self.handicap}; {self.positionPlayedLog}\n")
            file.write(f"{self.playerBlack.name}; {self.playerBlack.color}; \
                {self.playerBlack.captured}; {self.playerBlack.komi}\n")
            file.write(f"{self.playerWhite.name}; {self.playerWhite.color}; \
                {self.playerWhite.captured}; {self.playerWhite.komi}\n")
            for row in range(self.boardSize):
                rowPrint = ''
                for col in range(self.boardSize):
                    rowPrint += self.board[row][col].stoneHereColor
                file.write(rowPrint + '\n')
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

            self.boardSize = int(data_to_parse[0][0])  # change it to a list assignment?
            self.defaults = data_to_parse[0][1]
            self.timesPassed = int(data_to_parse[0][2])
            self.turnNum = int(data_to_parse[0][3])
            self.handicap = data_to_parse[0][4]
            self.positionPlayedLog = list(ast.literal_eval(data_to_parse[0][5]))
            del data_to_parse[0]

            self.playerBlack.name = data_to_parse[0][0]
            self.playerBlack.color = data_to_parse[0][1]
            self.playerBlack.captured = int(data_to_parse[0][2])
            self.playerBlack.komi = float(data_to_parse[0][3])
            del data_to_parse[0]

            self.playerWhite.name = data_to_parse[0][0]
            self.playerWhite.color = data_to_parse[0][1]
            self.playerWhite.captured = int(data_to_parse[0][2])
            self.playerWhite.komi = float(data_to_parse[0][3])
            del data_to_parse[0]

            for idx in range(len(data_to_parse)):
                data_to_parse[idx] = data_to_parse[idx][0].split('  ')

            for xidx in range(self.boardSize):
                for yidx in range(self.boardSize):
                    if yidx == 0:
                        self.board[xidx][yidx].stoneHereColor = f"{data_to_parse[xidx][yidx]} "
                    else:
                        self.board[xidx][yidx].stoneHereColor = f" {data_to_parse[xidx][yidx]} "
