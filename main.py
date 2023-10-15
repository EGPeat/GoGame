from uifunctions import p, pt
import goclasses as go
import uifunctions as ui
from icecream import ic
def setupICtestsDefault(defaultz=True):
    boardSize=ui.StartGameDefault()
    GameBoard=go.GoBoard(boardSize,defaults=defaultz)
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



boardSize=ui.StartGameDefault()

GameBoard=go.GoBoard(boardSize,defaults=True)

GameBoard.playGame()

#add in a way to print the board, modify the piece class to do 