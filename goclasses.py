from uifunctions import p, pt
from icecream import ic
from enum import Enum
class Player():
    def __init__(self, name=None, color=None,captured=None, komi=0):
        self.name=name
        self.color=color
        self.captured=captured
        self.komi=komi
    #allows player input to choose their name
    def chooseName(self):
        p("Please Enter a name you would like to use, but keep it less than 30 characters:")
        while self.name==None:
            try:
                playerName=str(input())
                if len(playerName) >30:
                    raise SyntaxError
                self.name=playerName

                break
            except SyntaxError:
                p("It seems you entered a name longer than 30 characters. Please try again")
    #allows player input to choose komi value
    def chooseKomi(self):
        p(f"Your color is {self.color}")
        done=False
        p("Please enter Komi Value. 6.5 is normally done:")
        while self.komi==0 and done != True:
            try:
                komiVal=float(input())
                self.komi=komiVal
                break
            except ValueError:
                p("It seems you entered something that isn't a float. Please try again")


#enumerate to help us understand where the coordinates are/mean
class piecePosition(Enum):
    TopLeftCorner=1
    TopRightCorner=2
    BottomRightCorner=3
    BottomLeftCorner=4
    TopSide=5
    BottomSide=6
    LeftSide=7
    RightSide=8
    Interior=9

unicodePrint ={
    "Black":u" \u26AB ",
    "White":u" \u26AA "
}
unicodeBlack=unicodePrint["Black"]
unicodeWhite=unicodePrint["White"]

        

class Piece(): #should honestly be boardLocation or something like that.
    def __init__(self, rowVal=None, colVal=None, positionVal=piecePosition.Interior):
        self.row=rowVal
        self.col=colVal
        self.position=positionVal
        self.stoneHereColor=None #none for nothing played here
        self.positionPlayedLast=None #for ko 
    
    def printPiece(self):
        p('\n')
        ic(self.row)
        ic(self.col)
        ic(self.position)
    #Allows for updating a specific variable in the Piece class
    def setupClassValue(self,classValue,value):
        if hasattr(self,classValue):
            setattr(self,classValue,value)
        else:
            p("No attribute for that")



class GoBoard():
    def __init__(self,boardSize=17,defaults=True):
        #self.handicap
        self.boardSize=boardSize
        self.defaults=defaults
        self.board=self.setupBoard()
        self.playerBlack= self.setupPlayer(self.defaults,color="Black")
        self.playerWhite= self.setupPlayer(self.defaults,color="White")



    #This sets up the board variable of the GoBoard class, initializing as appropriate
    def setupBoard(self):

        #This creates a 2d array with objects of class Piece()
        boardAssign= [[Piece() for i in range(self.boardSize)] for j in range(self.boardSize)]

        #This assigns every Piece it's row/col values
        for row in range(self.boardSize):
            for col in range(self.boardSize):
                boardAssign[row][col].setupClassValue('row',row)
                boardAssign[row][col].setupClassValue('col',col)
 


        #This assigns every Pieces it's piece Position value
        #It starts with the top row and bottom row, and then does left and right column
        # It then does all interior pieces, finishing with the corner pieces
        for idxRow in range(2): 
            for idxCol in range(self.boardSize):

                if idxRow==0:
                    boardAssign[0][idxCol].setupClassValue('position',piecePosition.TopSide)
                else:
                    boardAssign[self.boardSize-1][idxCol].setupClassValue('position',piecePosition.BottomSide)

        for idxCol in range(2):
            for idxRow in range(self.boardSize):
                if idxCol==0:
                    boardAssign[idxRow][0].setupClassValue('position',piecePosition.LeftSide)
                else:
                    boardAssign[idxRow][self.boardSize-1].setupClassValue('position',piecePosition.RightSide)
        for idxRow in range(1,self.boardSize-1):
            for idxCol in range(1,self.boardSize-1):
                boardAssign[idxRow][idxCol].setupClassValue('position',piecePosition.Interior)
        boardAssign[0][0].setupClassValue('position',piecePosition.TopLeftCorner)
        boardAssign[0][self.boardSize-1].setupClassValue('position',piecePosition.TopRightCorner)
        boardAssign[self.boardSize-1][0].setupClassValue('position',piecePosition.BottomLeftCorner)
        boardAssign[self.boardSize-1][self.boardSize-1].setupClassValue('position',piecePosition.BottomRightCorner)



        
        for row in range(self.boardSize):
            rowVals = [boardAssign[row][col].position.name for col in range(self.boardSize)]
            ic(rowVals)

        return boardAssign





    #This sets up the Player class, assigning appropriate values to each player as needed
    def setupPlayer(self,defaults,color):
        if defaults:
            if color=="Black":
                playerAssign=Player(name="Player One",color="Black")
            else:
                playerAssign=Player(name="Player Two",color="White",komi=6.5)
        else:
            if color=="Black":
                playerAssign=Player(color="Black")
                playerAssign.chooseName()
                playerAssign.chooseKomi()
            else:
                playerAssign=Player(color="White")
                playerAssign.chooseName()
                playerAssign.chooseKomi()
        return playerAssign
