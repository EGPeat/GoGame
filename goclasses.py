from uifunctions import p, pt


class Player():
    def __init__(self, name=None, color=None,captured=None, komi=None):
        self.name=name
        self.color=color
        self.captured=captured
        self.komi=komi

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

class piecePosition(enumerate):
    TopLeftCorner=1
    TopRightCorner=2
    BottomRightCorner=3
    BottomLeftCorner=4
    TopSide=5
    BottomSide=6
    LeftSide=7
    RightSide=8

class CornerPiece():
    def __init__(self, row=None, col=None):
    #def __init__(self, row=None, col=None, position=None):
        self.row=row
        self.col=col
        #self.position=position
        self.connections=2

class EdgePiece():
    def __init__(self, row=None, col=None):
        self.row=row
        self.col=col
        #self.position=position
        self.connectioncount=3
        

class NormalPiece():
    def __init__(self, row=None, col=None):
        self.row=row
        self.col=col
        #self.position=position
        self.connections=4

class GoBoard():
    def setupBoard(self):
        for col in range(self.boardSize):
            print(col)
    
    def __init__(self,boardSize=17):
        self.boardSize=boardSize
        self.board=None
        #self.board=setupBoard()
        self.playerBlack= Player
        self.playerWhite= Player
        #need a function to initialize both names, etc

#    def changeKomi():
    
    
        
