from uifunctions import p, inputVal
from icecream import ic
import os.path
import ast


class Player():
    def __init__(self, name=None, color=None, captured=0, komi=0):
        self.name = name
        self.color = color
        self.captured = captured
        self.komi = komi

    # allows player input to choose their name
    def chooseName(self):
        p("Please Enter a name you would like to use, but keep it less than 30 characters:")
        while self.name is None:
            try:
                playerName = str(input())
                if len(playerName) > 30:
                    raise SyntaxError
                self.name = playerName

                break
            except SyntaxError:
                p("It seems you entered a name longer than 30 characters. Please try again")

    # allows player input to choose komi value
    def chooseKomi(self):
        p(f"Your color is {self.color}")
        done = False
        p("Please enter Komi Value. 6.5 is normally done:")
        while self.komi == 0 and done is not True:
            try:
                komiVal = float(input())
                self.komi = komiVal
                break
            except ValueError:
                p("It seems you entered something that isn't a float. Please try again")


unicodePrint = {
    "Black": u" \u26AB ",
    "White": u" \u26AA ",
    "None": u" \U0001F7E9 "
}
unicodeBlack = unicodePrint["Black"]
unicodeWhite = unicodePrint["White"]
unicodeNone = unicodePrint["None"]


class Piece():  # should honestly be boardLocation or something like that.
    def __init__(self, rowVal=None, colVal=None):
        self.row = rowVal
        self.col = colVal
        self.stoneHereColor = unicodeNone

    def printPiece(self):
        p('\n')
        ic(self.row)
        ic(self.col)
        ic(self.stoneHereColor)

    # Allows for updating a specific variable in the Piece class
    def setupClassValue(self, classValue, value):
        if hasattr(self, classValue):
            setattr(self, classValue, value)
        else:
            p("No attribute for that")


class GoBoard():
    def __init__(self, boardSize=17, defaults=True):
        self.boardSize = boardSize
        self.defaults = defaults
        self.board = self.setupBoard()
        self.playerBlack = self.setupPlayer(self.defaults, color="Black")
        self.playerWhite = self.setupPlayer(self.defaults, color="White")
        self.timesPassed = 0
        self.turnNum = 0
        self.positionPlayedLog = list()  # (-1,-1) shows the boundary between a handicap and normal play
        self.visitKill = set()
        self.handicap = self.chooseHandicap(self.defaults)

    def printBoard(self):
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
    def setupBoard(self):

        # This creates a 2d array with objects of class Piece()
        boardAssign = [[Piece() for i in range(self.boardSize)] for j in range(self.boardSize)]

        # This assigns every Piece it's row/col values
        for row in range(self.boardSize):
            for col in range(self.boardSize):
                boardAssign[row][col].setupClassValue('row', row)
                boardAssign[row][col].setupClassValue('col', col)

        return boardAssign

    # This sets up the Player class, assigning appropriate values to each player as needed
    def setupPlayer(self, defaults, color):
        if defaults:
            if color == "Black":
                playerAssign = Player(name="Player One", color="Black")
            else:
                playerAssign = Player(name="Player Two", color="White", komi=6.5)
        else:
            if color == "Black":
                playerAssign = Player(color="Black")
                playerAssign.chooseName()
                playerAssign.chooseKomi()
            else:
                playerAssign = Player(color="White")
                playerAssign.chooseName()
                playerAssign.chooseKomi()
        return playerAssign

    def chooseHandicap(self, defaults):
        if defaults is True:
            return (False, "None", 0)
        done = False
        handicapPoints9 = [(2, 6), (6, 2), (6, 6), (2, 2), (4, 4)]
        handicapPoints13 = [(3, 9), (9, 3), (9, 9), (3, 3), (6, 6), (6, 3), (6, 9), (3, 6), (9, 6)]
        handicapPoints17 = [(3, 13), (13, 3), (13, 13), (3, 3), (8, 8), (8, 3), (8, 13), (3, 8), (13, 8)]
        p("Please enter some information regarding a handicap.\n\
          For the 100s place write 1 if there should be no handicap, or 2 if there should \n\
          For the 10s place, write 1 for Black getting the handicap, or 2 for white getting it\n\
          For the 1s place, please enter the number of stones the handicap should be\n\
          An example would be 212, meaning there is a handicap, black has it, and black gets 2 stones\n\
          Warning. If you have choosen a 9x9 board, you can have only a 5 piece handicap max")
        while done is not True:
            try:
                handicapInfo = int(input())

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
            self.playPiece(row, col, player)
        self.positionPlayedLog.append(("Break between handicaps and normal play", -1, -1))
        self.turnNum = 0
        return (True, player, handicapInfo)

    def playGame(self, fromFile=False):
        if fromFile is not True:
            self.setupBoard()
        else:
            if self.positionPlayedLog[-1][0] == "Black":
                self.playTurn(self.playerWhite.color)
        if self.handicap[0] is True and self.handicap[1] == "Black" and self.turnNum == 0:
            self.playTurn(self.playerWhite.color)

        while (self.timesPassed <= 1):
            self.playTurn(self.playerBlack.color)
            ic(self.timesPassed)
            if self.timesPassed == 2:
                break
            self.playTurn(self.playerWhite.color)
            ic(self.timesPassed)

        self.endOfGame()

    def playTurn(self, playerChoice):
        self.printBoard()

        p("Enter the row for your move, or (p) to pass, or (s) to save your board:")
        row = inputVal(self.boardSize - 1, int, True)
        if isinstance(row, str):
            if (row.lower() == 'p'):
                print("skipped turn")
                self.timesPassed += 1
                self.turnNum += 1
                self.positionPlayedLog.append((f"{playerChoice} passed", -2, -2))
                return
            elif (row.lower() == 's'):
                self.saveToFile()
                return
        p("Enter the col for your move:")
        col = inputVal(self.boardSize - 1, int, True)

        self.timesPassed = 0
        self.playPiece(row, col, playerChoice)
        return

    def playPiece(self, row, col, whichPlayer):
        piece = self.board[row][col]
        if (piece.stoneHereColor != unicodeNone):
            p("You tried to place where there is already a piece. Please try your turn again.")
            return False
        elif (self.turnNum > 2 and self.koRuleBreak(piece) is True):
            p("Place the piece there would break the ko rule. Please try your turn again.")
            return False
        elif (self.killStones(piece, whichPlayer) is True):
            if whichPlayer == "Black":
                piece.stoneHereColor = unicodeBlack
            else:
                piece.stoneHereColor = unicodeWhite
            self.turnNum += 1
            self.positionPlayedLog.append((whichPlayer, row, col))
            return True
        elif (self.suicide(piece, whichPlayer) == 0):
            p("Placing the piece there would commit suicide. Please try your turn again.")
            return False

        else:
            self.positionPlayedLog.append((whichPlayer, row, col))

            if whichPlayer == "Black":
                piece.stoneHereColor = unicodeBlack
            else:
                piece.stoneHereColor = unicodeWhite

        self.turnNum += 1
        return True

    def koRuleBreak(self, piece):
        player, row, col = self.positionPlayedLog[-2]
        if row < 0:  # this is required to allow passes to work
            return False
        koSpot = self.board[row][col]
        if piece == koSpot:
            return True

        return False

    def checkNeighbors(self, piece):
        neighbors = [(piece.row - 1, piece.col), (piece.row + 1, piece.col), (piece.row, piece.col - 1), (piece.row, piece.col + 1)]
        validNeighbors = []
        for coordinate in neighbors:
            if 0 <= coordinate[0] < self.boardSize and 0 <= coordinate[1] < self.boardSize:
                validNeighbors.append(coordinate)
        return validNeighbors

    def suicide(self, piece, whichPlayer, visited=None):
        if visited is None:
            visited = set()
        visited.add(piece)
        neighbors = self.checkNeighbors(piece)
        liberties = 0

        for coordinate in neighbors:
            neighborPiece = self.board[coordinate[0]][coordinate[1]]
            if neighborPiece.stoneHereColor == unicodePrint["None"]:
                liberties += 1
            elif neighborPiece.stoneHereColor != unicodePrint[whichPlayer]:
                pass
            elif neighborPiece not in visited:
                liberties += self.suicide(neighborPiece, whichPlayer, visited)
        self.visitKill = visited
        return liberties

    def removeStones(self, whichPlayer):  # take in the player who is gaining the pieces
        if whichPlayer == "Black":
            player = self.playerBlack
        else:
            player = self.playerWhite
        for position in self.visitKill:
            player.captured += 1
            position.stoneHereColor = unicodePrint["None"]

    def endOfGame(self):
        p("Your game has finished. Congrats.")
        p(f"Player Black: {self.playerBlack.name} captured {self.playerBlack.captured} and has a komi of {self.playerBlack.komi}")
        p(f"Player White: {self.playerWhite.name} captured {self.playerWhite.captured} and has a komi of {self.playerWhite.komi}")
        p(f"Player Black has a score of {self.playerBlack.komi+self.playerBlack.captured-self.playerWhite.captured}")
        p(f"Player Black has a score of {self.playerWhite.komi+self.playerWhite.captured-self.playerBlack.captured}")
        p("This code cannot calculate territory or dead stones, so please do that yourself")
        p("Would you like to save your game to a file? Type Y for yes, or N for no")
        desire = inputVal(1, str)
        if desire.upper() == "Y":
            self.saveToFile()

    def killStones(self, piece, whichPlayer):  # needs to return true if it does kill stones
        if whichPlayer == "Black":
            piece.stoneHereColor = unicodeBlack
        else:
            piece.stoneHereColor = unicodeWhite

        neighbors = self.checkNeighbors(piece)
        notWhichPlayer = ''
        truthVal = False
        if whichPlayer == "Black":
            notWhichPlayer = "White"
        else:
            notWhichPlayer = "Black"
        for coordinate in neighbors:
            neighborPiece = self.board[coordinate[0]][coordinate[1]]
            if neighborPiece.stoneHereColor == unicodePrint[notWhichPlayer]:
                if (self.suicide(neighborPiece, notWhichPlayer) == 0):
                    p("you killed a piece you monster")
                    # if whichPlayer == "Black":
                    # player = self.playerBlack
                    # else:
                    # player = self.playerWhite

                    self.removeStones(whichPlayer)
                    truthVal = True
        if truthVal is False:
            piece.stoneHereColor = unicodeNone
        return truthVal

    def saveToFile(self):
        p("Please write the name of the txt file you want to save to. Do not include '.txt' in what you write")
        filename = inputVal(30, str)
        with open(f"{filename}.txt", 'w', encoding='utf-8') as file:
            file.write(f"{self.boardSize}; {self.defaults}; {self.timesPassed}; {self.turnNum}; {self.handicap}; {self.positionPlayedLog}\n")
            file.write(f"{self.playerBlack.name}; {self.playerBlack.color}; {self.playerBlack.captured}; {self.playerBlack.komi}\n")
            file.write(f"{self.playerWhite.name}; {self.playerWhite.color}; {self.playerWhite.captured}; {self.playerWhite.komi}\n")
            for row in range(self.boardSize):
                rowPrint = ''
                for col in range(self.boardSize):
                    rowPrint += self.board[row][col].stoneHereColor
                file.write(rowPrint + '\n')

    def loadFromFile(self):  # make function to read out all the moves made
        p("Please write the name of the txt file you want to read from.")
        foundFile = False
        while foundFile is False:
            path_filename = f"{inputVal(30, str)}.txt"
            if os.path.isfile(path_filename):
                foundFile = True
            else:
                p("You have entered a filename that doesn't exist, please try inputing again. Don't write the .txt")

        with open(path_filename, 'r', encoding='utf-8') as file:
            data_to_parse = [line.rstrip() for line in file]
            data_to_parse = [line.split('; ') for line in data_to_parse]

            self.boardSize = int(data_to_parse[0][0])  # change it to a list assignment? like items in list 1 equals items in list 2
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
