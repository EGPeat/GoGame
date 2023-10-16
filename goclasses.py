from uifunctions import p, pt,inputVal
from icecream import ic
from enum import Enum
import queue
class Player():
    def __init__(self, name=None, color=None,captured=0, komi=0):
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

    




unicodePrint ={
    "Black":u" \u26AB ",
    "White":u" \u26AA ",
    "None":	u" \U0001F7E9 "
}
unicodeBlack=unicodePrint["Black"]
unicodeWhite=unicodePrint["White"]
unicodeNone=unicodePrint["None"]

        

class Piece(): #should honestly be boardLocation or something like that.
    def __init__(self, rowVal=None, colVal=None):
        self.row=rowVal
        self.col=colVal
        #self.position=positionVal
        self.stoneHereColor=unicodeNone
        
    
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
        self.timesPassed=0
        self.turnNum=0
        self.positionPlayedLog=list()
        self.visitKill=set()
    def printBoard(self): #add in numbers on the side
        p(f"This is the board at turn {self.turnNum}")
        numRow='      '

        for col in range(self.boardSize):

            if(col<10):
                numRow+=f"0{col}  "
            else:    
                numRow+=f"{col}  "
        p(numRow)
        
        for row in range(self.boardSize):
            rowPrint=''
            if(row<10):
                rowPrint+=f"0{row}   "
            else:    
                rowPrint+=f"{row}   "

            #rowPrint=f'{row} '
            for col in range(self.boardSize):
                rowPrint+=self.board[row][col].stoneHereColor
            p(rowPrint)


    #This sets up the board variable of the GoBoard class, initializing as appropriate
    def setupBoard(self):

        #This creates a 2d array with objects of class Piece()
        boardAssign= [[Piece() for i in range(self.boardSize)] for j in range(self.boardSize)]

        #This assigns every Piece it's row/col values
        for row in range(self.boardSize):
            for col in range(self.boardSize):
                boardAssign[row][col].setupClassValue('row',row)
                boardAssign[row][col].setupClassValue('col',col)
 
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

    def playGame(self):
        
        self.setupBoard()

        while(self.timesPassed!=2):
            self.playTurn(self.playerBlack.color)
            self.playTurn(self.playerWhite.color)

        self.endOfGame()





    def playTurn(self,playerChoice):
        hasPlayed=False
        self.printBoard()
        while hasPlayed!=True:
            p("Enter the row for your move, or -1 to pass:")
            row=inputVal(int,self.boardSize-1)
            p("Enter the col for your move, or -1 to pass:")
            col=inputVal(int,self.boardSize-1)
            if((row+col)<0):
                print("skipped turn")
                self.timesPassed+=1
                return
            else:
                self.timesPassed=0
                hasPlayed=self.playPiece(row,col,playerChoice)

        return

    def playPiece(self, row,col,whichPlayer):
        piece = self.board[row][col]
        if (piece.stoneHereColor != unicodeNone):
            p("You tried to place where there is already a piece. Please try your turn again.")
            return False
        elif(self.turnNum>2 and self.koRuleBreak(piece)==True): 
            p("Place the piece there would break the ko rule. Please try your turn again.")
            return False 
        elif(self.killStones(piece,whichPlayer)==True):
            if whichPlayer=="Black":
                piece.stoneHereColor=unicodeBlack
            else:
                piece.stoneHereColor=unicodeWhite
            self.turnNum+=1
            self.positionPlayedLog.append((row,col))
            return True
        elif(self.suicide(piece,whichPlayer)==0): 
            p("Placing the piece there would commit suicide. Please try your turn again.")
            return False
        
        else:
            self.positionPlayedLog.append((row,col))

            if whichPlayer=="Black":
                piece.stoneHereColor=unicodeBlack
            else:
                piece.stoneHereColor=unicodeWhite

        self.turnNum+=1
        return True



    def koRuleBreak(self,piece): 
        row,col=self.positionPlayedLog[-2] 
        koSpot=self.board[row][col]
        if piece==koSpot:
            return True
        
        return False
    def checkNeighbors(self,piece): #test this
        neighbors=[(piece.row-1, piece.col),(piece.row+1, piece.col),(piece.row, piece.col-1),(piece.row, piece.col+1)]
        validNeighbors=[]
        for coordinate in neighbors:
            if 0 <= coordinate[0] < self.boardSize and 0 <= coordinate[1] < self.boardSize:
                validNeighbors.append(coordinate)
        return validNeighbors


    def suicide(self, piece,whichPlayer,visited=None): #test this
        if visited is None:
            visited=set()
        visited.add(piece)
        sQueue=queue.Queue()
        neighbors=self.checkNeighbors(piece)
        liberties=0


        for coordinate in neighbors:
            neighborPiece=self.board[coordinate[0]][coordinate[1]]
            if neighborPiece.stoneHereColor==unicodePrint["None"]:
                liberties+=1
            elif neighborPiece.stoneHereColor!=unicodePrint[whichPlayer]:
                pass
            elif neighborPiece not in visited:
                liberties += self.suicide(neighborPiece, whichPlayer, visited)
        self.visitKill=visited
        return liberties
                    
    def removeStones(self,whichPlayer): #take in the player who is gaining the pieces
        if whichPlayer=="Black":
            player=self.playerBlack
        else:
            player=self.playerWhite
        for position in self.visitKill:
            player.captured+=1
            position.stoneHereColor=unicodePrint["None"]
    def endOfGame(self):
        p("Your game has finished. Congrats.")
        p(f"Player Black: {self.playerBlack.name} captured {self.playerBlack.captured} and has a komi of {self.playerBlack.komi}")
        p(f"Player White: {self.playerWhite.name} captured {self.playerWhite.captured} and has a komi of {self.playerWhite.komi}")
        p(f"Player Black has a score of {self.playerBlack.komi+self.playerBlack.captured-self.playerWhite.captured}")
        p(f"Player Black has a score of {self.playerWhite.komi+self.playerWhite.captured-self.playerBlack.captured}")
        p("This code cannot calculate territory or dead stones, so please do that yourself")
    def killStones(self, piece,whichPlayer): #needs to return true if it does kill stones
        if whichPlayer=="Black":
            piece.stoneHereColor=unicodeBlack
        else:
            piece.stoneHereColor=unicodeWhite
        
        
        neighbors=self.checkNeighbors(piece)
        notWhichPlayer=''
        truthVal=False
        if whichPlayer=="Black":
            notWhichPlayer="White"
        else:
            notWhichPlayer="Black"
        for coordinate in neighbors:
            neighborPiece=self.board[coordinate[0]][coordinate[1]]
            if neighborPiece.stoneHereColor==unicodePrint[notWhichPlayer]:# no idea if it works
                if(self.suicide(neighborPiece,notWhichPlayer)==0):
                    p("you killed a piece you monster")
                    if whichPlayer=="Black":
                        player=self.playerBlack
                    else:
                        player=self.playerWhite


                    self.removeStones(whichPlayer)

                    truthVal=True
        if truthVal==False:
            piece.stoneHereColor=unicodeNone
        return truthVal

        

                   

