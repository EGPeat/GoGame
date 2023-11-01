import goclasses as go
import uifunctions as ui
import PySimpleGUI as sg


sg.theme('DarkAmber')

layout = [
    [sg.Text(text='Welcome to Evan\'s Go Game ',
             font=('Arial Bold', 20),
             size=20,
             expand_x=True,
             justification='center')],
    [sg.Text(text='The default settings are a 9x9 board, 6.5 komi, and names for players of Player 1 and Player 2', key="Info",
             font=('Arial', 12),
             size=20,
             expand_x=True,
             justification='center')],
    [sg.Button("Choose File", font=('Arial Bold', 12)),
        sg.Button("New Game From Custom", font=('Arial Bold', 12)),
        sg.Button("New Game From Default", font=('Arial Bold', 12)),
        sg.Cancel("Exit Game", font=('Arial Bold', 12))]]


def setupWin2():
    text = f"Player 1 Name: {GameBoard.playerBlack.name}\nPlayer 1 Color: {GameBoard.playerBlack.color}\n\
    Player 1 Captured Pieces: {GameBoard.playerBlack.captured}\nPlayer 1 komi: {GameBoard.playerBlack.komi}\n\
    Player 2 Name: {GameBoard.playerWhite.name}\nPlayer 2 Color: {GameBoard.playerWhite.color}\n\
    Player 2 Captured Pieces: {GameBoard.playerWhite.captured}\nPlayer 2 komi: {GameBoard.playerWhite.komi}"
    layout2 = [
        [sg.Button("Pass Turn", font=('Arial Bold', 12)),
         sg.Button("Save Game", font=('Arial Bold', 12)),
         sg.Button("Press After Loading From File", font=('Arial Bold', 12)),
         sg.Button("Exit Game", font=('Arial Bold', 12))],

        [sg.Text(text='The default settings are a 9x9 board, 6.5 komi, and names for players of Player 1 and Player 2', key="Info",
         font=('Arial', 12), size=20, expand_x=True, justification='center')],
        [[sg.Button('', size=(4, 2), key=(i, j), pad=(0, 0)) for j in range(GameBoard.boardSize)] for i in range(GameBoard.boardSize)],
        [sg.Multiline(text,
                      font=('Arial Bold', 12),
                      size=10,
                      expand_x=True,
                      expand_y=True,
                      justification='center')]]
    window2 = sg.Window('Game Screen', layout2, size=(700, 700))

    return window2


window = sg.Window('Game Screen', layout, size=(700, 700))

while True:
    event, values = window.read()

    if event == "Choose File":
        file = sg.popup_get_file('Select a file', title="File selector", font=('Arial Bold', 15))
        file = file.split("/")
        file = file[-1]
        sg.popup_no_buttons('You chose', file, non_blocking=True, font=('Arial Bold', 15))
        GameBoard = go.GoBoard(9, defaults=True)
        GameBoard.loadFromFile(True, file)
        window.close()
        window2 = setupWin2()
        GameBoard.playGame(window2, fromFile=True)

    elif event == "New Game From Custom":
        boardSize = ui.StartGame()
        GameBoard = go.GoBoard(boardSize, defaults=False)
        window.close()
        window2 = setupWin2()
        GameBoard.playGame(window2, fromFile=False, fixesHandicap=True)

    elif event == "New Game From Default":
        GameBoard = go.GoBoard(9, defaults=True)
        window.close()
        window2 = setupWin2()
        GameBoard.playGame(window2)

    if event in (sg.WIN_CLOSED, 'Exit Game'):
        break

window.close()
