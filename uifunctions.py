import PySimpleGUI as sg


def p(input):
    print(input)


def pt(input):
    print(type(input))


# Starts the game, asking for user input regarding the size of the board.
def start_game():
    info = "Please enter in the size you wish to have your Go Board as.\nPlease\
        type (9) for a 9x9, (13) for a 13x13, or (17) for 17x17:"

    while True:
        try:
            size = sg.popup_get_text(info, title="Please Enter Text", font=('Arial Bold', 15))
            size = int(size)
            if size not in [9, 13, 17]:
                raise SyntaxError

            break
        except ValueError:
            info = "It seems you entered something that isn't a int. Please try again"
        except SyntaxError:
            info = "It seems you entered a number that isn't 9, 13, 17. Please try again"

    p(f"You have choosen a {size}x{size} board.")
    return size


# Validates that the input is of the correct type
def input_value(max_size=16, value_type=int, options=False):

    while True:
        try:
            if not options:
                info = value_type(input())
                if isinstance(info, str) and (len(info) > max_size):
                    raise IndexError
                elif isinstance(info, int) and (info > max_size):
                    raise IndexError
                return info
            else:
                info = input()
                if info.isnumeric():
                    info = int(info)
                    if info > max_size:
                        raise IndexError
                    return info
                elif isinstance(info, str) and (len(info) > max_size):
                    raise IndexError
                return info

        except ValueError:
            info = f"It seems you entered something that isn't a {value_type}. Please try again"
        except IndexError:
            info = "you put in something that is a larger int than is allowed, or a longer string than is allowed"


# Sets up the main window using PySimpleGUI
def setup_menu():
    layout = [
        [sg.Text(text='Welcome to Evan\'s Go Game ',
                 font=('Arial Bold', 20),
                 size=20,
                 expand_x=True,
                 justification='center')],
        [sg.Text(
            text='The default settings are a 9x9 board, 6.5 komi, and names for players of Player 1 and Player 2', key="Info",
            font=('Arial', 12),
            size=20,
            expand_x=True,
            justification='center')],
        [sg.Button("Choose File", font=('Arial Bold', 12)),
            sg.Button("New Game From Custom", font=('Arial Bold', 12)),
            sg.Button("New Game From Default", font=('Arial Bold', 12)),
            sg.Cancel("Exit Game", font=('Arial Bold', 12))]]
    window = sg.Window('Game Screen', layout, size=(700, 700))
    return window


# Sets up the window for playing the game using PySimpleGUI
def setup_board_window(game_board):
    text = f"Player 1 Name: {game_board.player_black.name}\nPlayer 1 Color: {game_board.player_black.color}\n\
    Player 1 Captured Pieces: {game_board.player_black.captured}\nPlayer 1 komi: {game_board.player_black.komi}\n\
    Player 2 Name: {game_board.player_white.name}\nPlayer 2 Color: {game_board.player_white.color}\n\
    Player 2 Captured Pieces: {game_board.player_white.captured}\nPlayer 2 komi: {game_board.player_white.komi}"
    layout2 = [
        [sg.Button("Pass Turn", font=('Arial Bold', 12)),
         sg.Button("Save Game", font=('Arial Bold', 12)),
         sg.Button("Press After Loading From File", font=('Arial Bold', 12)),
         sg.Button("Exit Game", font=('Arial Bold', 12))],

        [sg.Text(text='The default settings are a 9x9 board, 6.5 komi,\
                and names for players of Player 1 and Player 2', key="Info",
         font=('Arial', 12), size=20, expand_x=True, justification='center')],
        [[sg.Button('', size=(4, 2), key=(i, j), pad=(0, 0))
            for j in range(game_board.board_size)] for i in range(game_board.board_size)],

        [sg.Multiline(text,
                      font=('Arial Bold', 12),
                      size=10,
                      expand_x=True,
                      expand_y=True,
                      justification='center')]]
    window2 = sg.Window('Game Screen', layout2, size=(700, 700))

    return window2
