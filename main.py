from uifunctions import p, inputVal
import goclasses as go
import uifunctions as ui
from icecream import ic


def setupICtestsDefault(defaultz=True):
    boardSize = ui.StartGameDefault()
    GameBoard = go.GoBoard(boardSize, defaults=defaultz)
    ic(GameBoard.boardSize)
    ic(GameBoard.defaults)
    ic(GameBoard.playerBlack)
    ic(GameBoard.playerWhite)
    ic(GameBoard.board)
    ic(GameBoard.playerBlack.name)
    ic(GameBoard.playerBlack.color)
    ic(GameBoard.playerBlack.komi)

    ic(GameBoard.playerWhite.name)
    ic(GameBoard.playerWhite.color)
    ic(GameBoard.playerWhite.komi)


def setupICtestsNoDefault():
    setupICtestsDefault(False)


p("Please choose between loading a saved game, or making a new game.\nPlease type L for load, or N for new")
load_choice = inputVal(str, 1)
if load_choice.upper() == "L":
    GameBoard = go.GoBoard(9, defaults=True)
    GameBoard.loadFromFile()
    GameBoard.playGame()

elif load_choice.upper() == "N":
    p("The default settings are a 9x9 board, 6.5 komi, and names for players of Player 1 and Player 2")
    p("Please type d for a default values, or type p for manual values")
    choice = inputVal(str, 1)

    if choice == 'd':
        boardSize = ui.StartGameDefault()
        GameBoard = go.GoBoard(boardSize, defaults=True)
    else:
        boardSize = ui.StartGame()
        GameBoard = go.GoBoard(boardSize, defaults=False)
    GameBoard.playGame()
