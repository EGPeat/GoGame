import PySimpleGUI as sg


def p(input):
    print(input)


def pt(input):
    print(type(input))


# Starts the game, asking for user input regarding the size of the board.
def start_game():
    info = "Please click the size you wish to have your Go Board as."

    layout = [[sg.Text(info)],
              [sg.Button("9x9", font=('Arial Bold', 16)),
              sg.Button("13x13", font=('Arial Bold', 16)),
              sg.Button("17x17", font=('Arial Bold', 16))]]
    window2 = sg.Window('Game Screen', layout, size=(200, 200), finalize=True)
    option, option2 = window2.read()
    window2.close()
    if option == "9x9":
        return 9
    elif option == "13x13":
        return 13
    else:
        return 17


def handicap_person_gui():
    info = "Please enter some information regarding a handicap. Which player will get a handicap?"

    layout = [[sg.Text(info)],
              [sg.Button("Black", font=('Arial Bold', 16)),
              sg.Button("White", font=('Arial Bold', 16))],
              [sg.Button("I don't want a handicap", font=('Arial Bold', 16))]]
    window2 = sg.Window('Game Screen', layout, size=(200, 200), finalize=True)
    option, option2 = window2.read()
    window2.close()
    return option


def handicap_number_gui(board_size):
    info = "Please enter some information regarding a handicap. Which player will get a handicap?"
    deflt = ('Arial Bold', 16)
    layout = [[sg.Text(info)],
              [sg.Button("1", font=deflt), sg.Button("2", font=deflt), sg.Button("3", font=deflt)],
              [sg.Button("4", font=deflt), sg.Button("5", font=deflt), sg.Button("6", font=deflt)],
              [sg.Button("7", font=deflt), sg.Button("8", font=deflt), sg.Button("9", font=deflt)]]
    layout2 = [[sg.Text(info)],
               [sg.Button("1", font=deflt), sg.Button("2", font=deflt), sg.Button("3", font=deflt)],
               [sg.Button("4", font=deflt), sg.Button("5", font=deflt)]]
    if board_size == 9:
        window2 = sg.Window('Game Screen', layout2, size=(200, 200), finalize=True)
    else:
        window2 = sg.Window('Game Screen', layout, size=(200, 200), finalize=True)
    option, option2 = window2.read()
    window2.close()
    return int(option)


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
    window = sg.Window('Game Screen', layout, size=(700, 700), finalize=True)
    return window


# Sets up the window for playing the game using PySimpleGUI
def setup_board_window(game_board):
    if game_board.turn_num % 2 == 1:
        text = "It is currently White's turn.\n"
    else:
        text = "It is currently Black's turn.\n"

    text = text + f"Turn Number is {game_board.turn_num}\nPlayer 1 Name: {game_board.player_black.name}\nPlayer 1 Color: Black\n\
    Player 1 Captured Pieces: {game_board.player_black.captured}\nPlayer 1 komi: {game_board.player_black.komi}\n\
    Player 2 Name: {game_board.player_white.name}\nPlayer 2 Color: White\n\
    Player 2 Captured Pieces: {game_board.player_white.captured}\nPlayer 2 komi: {game_board.player_white.komi}"
    layout2 = [
        [sg.Button("Pass Turn", font=('Arial Bold', 12)),
         sg.Button("Save Game", font=('Arial Bold', 12)),
         sg.Button("Undo Turn", font=('Arial Bold', 12)),
         # sg.Button("Press After Loading From File", font=('Arial Bold', 12)),
         sg.Button("Exit Game", font=('Arial Bold', 12))],
        [[sg.Button('', size=(4, 2), key=(i, j), pad=(0, 0))
            for j in range(game_board.board_size)] for i in range(game_board.board_size)],  # This does NOT size correctly

        [sg.Multiline(text,
                      font=('Arial Bold', 12),
                      size=10,
                      expand_x=True,
                      expand_y=True,
                      key='Scoring',
                      justification='center')]]
    window2 = sg.Window('Game Screen', layout2, size=(700, 700), finalize=True)

    return window2


def validation_gui(info1, var_type):
    output = None
    while output is None:
        sg.popup(info1, line_width=42, auto_close=True, auto_close_duration=15)
        output = (sg.popup_get_text("Enter Information", title="Please Enter Text", font=('Arial Bold', 15)))
    output = var_type(output)
    return output


def update_scoring(self, window, choosen_player):
    if choosen_player == self.player_black:
        text = "It is currently White's turn.\n"
    else:
        text = "It is currently Black's turn.\n"
    text = text + f"Turn Number is {self.turn_num}\nPlayer 1 Name: {self.player_black.name}\nPlayer 1 Color: Black\n\
    Player 1 Captured Pieces: {self.player_black.captured}\nPlayer 1 komi: {self.player_black.komi}\n\
    Player 2 Name: {self.player_white.name}\nPlayer 2 Color: White\n\
    Player 2 Captured Pieces: {self.player_white.captured}\nPlayer 2 komi: {self.player_white.komi}"
    window['Scoring'].update(text)


def end_game_popup(self):
    info = f"Your game has finished. Congrats.\nPlayer Black: {self.player_black.name} captured \
            {self.player_black.captured} and has a komi of {self.player_black.komi}\n Player White: {self.player_white.name}\
            captured {self.player_white.captured} and has a komi of {self.player_white.komi}\
            \n Player Black has a score of {self.player_black.komi+self.player_black.captured-self.player_white.captured}\n\
            Player Black has a score of {self.player_white.komi+self.player_white.captured-self.player_black.captured}\n\
            This code cannot calculate territory or dead stones, so please\
            do that yourself\nPlease save your game to a file or exit the program."
    sg.popup(info, title="Game has Concluded", line_width=200, auto_close=True, auto_close_duration=20)
