import PySimpleGUI as sg
import os
import platform
import pygame
import config as cf
from typing import Tuple, List


def start_game() -> int:  # Refactor?
    '''Starts the game, asking for user input regarding the size of the board.'''
    info = "Please click the size you wish to have your Go Board as."

    layout = [[sg.Text(info)],
              [sg.Button("9x9", font=('Arial Bold', 16)),
              sg.Button("13x13", font=('Arial Bold', 16)),
              sg.Button("19x19", font=('Arial Bold', 16))]]
    window2 = sg.Window('Game Screen', layout, size=(200, 200), finalize=True)
    option, _ = window2.read()
    window2.close()
    if option == "9x9":
        return 9
    elif option == "13x13":
        return 13
    else:
        return 19


def handicap_person_gui() -> str:  # Refactor?
    '''Asks for user input regarding which player will get a handicap'''
    info = "Please enter some information regarding a handicap. Which player will get a handicap?"

    layout = [[sg.Text(info)],
              [sg.Button("Black", font=('Arial Bold', 16)),
              sg.Button("White", font=('Arial Bold', 16))],
              [sg.Button("I don't want a handicap", font=('Arial Bold', 16))]]
    window2 = sg.Window('Game Screen', layout, size=(200, 200), finalize=True)
    option, _ = window2.read()
    window2.close()
    return option


def handicap_number_gui(board_size: int) -> int:  # Refactor?
    '''Asks for user input regarding the handicap size'''
    info = "Please enter some information regarding a handicap. How large is the handicap?"
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
    option, _ = window2.read()
    window2.close()
    return int(option)


def setup_menu():
    '''Sets up the main window using PySimpleGUI'''
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
            sg.Button("New Hex Game", font=("Arial Bold", 12))],
        [sg.Button("Play Against AI", font=('Arial Bold', 12)),
         sg.Button("AI SelfPlay", font=('Arial Bold', 12)),
         sg.Button("AI Training", font=('Arial Bold', 12)),
         sg.Cancel("Exit Game", font=('Arial Bold', 12))]]  # need to add options for mp for different board sizes lol
    window = sg.Window('Game Screen', layout, size=(700, 700), finalize=True)
    return window


def setup_board_window_pygame(game_board):  # hardcoded values. Suboptimal
    '''Sets up the window for playing the game using PySimpleGUI'''
    # Many thanks to the following github demo from PySimpleGUI
    # https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_PyGame_Integration.py
    text = f"It is currently {game_board.whose_turn.color}'s turn. \n"
    text = text + f"Turn Number is {game_board.turn_num}\n\n\n\
    Player 1 Name: {game_board.player_black.name}\nPlayer 1 Color: Black\n\
    Player 1 komi: {game_board.player_black.komi}\n\n\nPlayer 2 Name: {game_board.player_white.name}\n\
    Player 2 Color: White\nPlayer 2 komi: {game_board.player_white.komi}"
    layout_buttons = [
        [sg.Button("Pass Turn", font=('Arial Bold', 12)),
         sg.Button("Save Game", font=('Arial Bold', 12)),
         sg.Button("Undo Turn", font=('Arial Bold', 12)),
         sg.Button("Quit Program", font=('Arial Bold', 12), key="Res"),
         sg.Button("Exit To Menu", font=('Arial Bold', 12), key="Exit Game")]
    ]
    layout_board = [[sg.Graph((700, 700), (0, 700), (700, 0), key='-GRAPH-', enable_events=True)]]
    layout_sidebar = [[sg.Multiline(text, font=('Arial Bold', 12), size=10, expand_x=True, expand_y=True,
                      key='Scoring', justification='center')]]
    full_layout = [[layout_buttons,
                    sg.Column(layout_sidebar, expand_x=True, expand_y=True),
                   sg.VSeparator(),
                   sg.Column(layout_board)]]

    window = sg.Window('Game Screen', full_layout, size=(1000, 900), resizable=True, finalize=True)
    graph = window['-GRAPH-']

    embed = graph.TKCanvas
    os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
    if platform.system() == "Linux":
        os.environ['SDL_VIDEODRIVER'] = "x11"
    elif platform.system() == "Windows":
        os.environ['SDL_VIDEODRIVER'] = 'windib'
    screen = pygame.display.set_mode((700, 700))
    game_board.screen = screen
    game_board.window = window
    pygame.display.init()
    while True:  # For some reason this is required
        _, _ = window.read(timeout=100)
        pygame.display.update()
        break
    screen.fill(pygame.Color(200, 162, 200))
    draw_gameboard(game_board, screen)
    pygame.display.update()
    return window


def validation_gui(info1, var_type):
    '''Makes sure the player enters a valid type of information.'''
    output = None
    while output is None:
        sg.popup(info1, line_width=42, auto_close=True, auto_close_duration=15)
        output = (sg.popup_get_text("Enter Information", title="Please Enter Text", font=('Arial Bold', 15)))
    output = var_type(output)
    return output


def update_scoring(self):
    '''Updates the scoring in the PySimpleGui window.'''
    text = f"It is currently {self.whose_turn.color}'s turn. \n"
    text = text + f"Turn Number is {self.turn_num}\n\n\nPlayer 1 Name: {self.player_black.name}\nPlayer 1 Color: Black\n\
    Player 1 komi: {self.player_black.komi}\n\n\nPlayer 2 Name: {self.player_white.name}\n\
    Player 2 Color: White\nPlayer 2 komi: {self.player_white.komi}"
    self.window['Scoring'].update(text)


def end_game_popup():
    info = "Please take turns clicking on stones that you believe are dead, and then the program will score.\
        \n Please pass twice once you are finished scoring."
    sg.popup(info, title="Scoring", line_width=200, auto_close=True, auto_close_duration=3)


def end_game_popup_two(self):  # Refactor?
    pb = self.player_black
    pw = self.player_white
    player_black_score = pb.komi + pb.territory + len(self.black_set)
    player_white_score = pw.komi + pw.territory + len(self.white_set)
    difference = player_black_score - player_white_score
    info = f"Your game has finished.\nPlayer Black: {pb.name} has {pb.territory} territory\
            , and played {len(self.black_set)} pieces and has a komi of {pb.komi}\
            \n Player White: {pw.name} has {pw.territory} territory, and played {len(self.white_set)} pieces\
              and has a komi of {pw.komi}\n Player Black has a score of {player_black_score}\n\
            Player White has a score of {player_white_score}, meaning "
    if difference > 0:
        info = info + f"Player Black won by {difference} points"
    else:
        info = info + f"Player White won by {difference * -1} points"
    sg.popup(info, title="Game has Concluded", line_width=200, auto_close=True, auto_close_duration=20)


def default_popup_no_button(info, time):
    '''Popup with some pre-defined default values'''
    sg.popup_no_buttons(info, non_blocking=True, font=('Arial Bold', 15),
                        auto_close=True, auto_close_duration=time)


def def_popup(info, time):
    '''Popup with some pre-defined default values'''
    sg.popup(info, line_width=42, auto_close=True, auto_close_duration=time)


def hex_ui_setup():
    '''Sets up the Hex UI using PySimpleGUI and Pygame integration.'''
    # Many thanks to the following github demo from PySimpleGUI
    # https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_PyGame_Integration.py
    text = "It is currently PLACEHOLDER turn. \n"
    layout_buttons = [
        [sg.Button("Pass Turn", font=('Arial Bold', 12)),
         sg.Button("Save Game", font=('Arial Bold', 12)),
         sg.Button("Undo Turn", font=('Arial Bold', 12)),
         sg.Button("Quit Program", font=('Arial Bold', 12), key="Res"),
         sg.Button("Exit To Menu", font=('Arial Bold', 12), key="Exit Game")]
    ]
    layout_board = [[sg.Graph((700, 700), (0, 700), (700, 0), key='-GRAPH-', enable_events=True)]]
    layout_sidebar = [[sg.Multiline(text, font=('Arial Bold', 12), size=10, expand_x=True, expand_y=True,
                      key='Scoring', justification='center')]]
    full_layout = [[layout_buttons,
                    sg.Column(layout_sidebar, expand_x=True, expand_y=True),
                   sg.VSeparator(),
                   sg.Column(layout_board)]]

    window = sg.Window('Game Screen', full_layout, size=(900, 700), resizable=True, finalize=True)
    graph = window['-GRAPH-']

    embed = graph.TKCanvas
    os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
    print(platform.system())
    print(platform.system_alias)
    if platform.system() == "Linux":
        os.environ['SDL_VIDEODRIVER'] = "x11"
    elif platform.system() == "Windows":
        os.environ['SDL_VIDEODRIVER'] = 'windib'
        _ = pygame.display.set_mode((700, 700))
        pygame.display.init()
        pygame.display.update()
        while True:
            _, _ = window.read(timeout=10)
            pygame.display.update()
            break
    return window


def draw_gameboard(game_board, screen, gameboard_surface=pygame.surface.Surface((700, 700))):
    '''Draws the gameboard using pygame'''
    workable_area: int = 620
    distance: float = workable_area / (game_board.board_size - 1)
    circle_radius: float = distance / 3
    game_board.pygame_board_vals = (workable_area, distance, circle_radius)
    gameboard_surface.fill(pygame.Color(200, 162, 200))
    draw_linez(game_board, distance, gameboard_surface)
    stars_pygame(game_board, gameboard_surface, circle_radius)
    screen.blit(gameboard_surface, (0, 0))
    game_board.backup_board = gameboard_surface


def draw_linez(game_board, distance, gameboard_surface):
    for xidx in range(game_board.board_size):
        x_val: float = 40 + xidx * distance
        x_val_previous: float = x_val - distance
        for yidx in range(game_board.board_size):
            y_val: float = 40 + yidx * distance
            y_val_previous: float = y_val - distance
            if xidx > 0:
                pygame.draw.line(gameboard_surface, (0, 0, 0), (x_val_previous, y_val), (x_val, y_val))
            if yidx > 0:
                pygame.draw.line(gameboard_surface, (0, 0, 0), (x_val, y_val_previous), (x_val, y_val))


def stars_pygame(self, window, circle_radius: float):
    # Refactor? Should add other stars...
    '''Draws the stars on the gameboard using pygame'''
    size: int = self.board_size
    lst9: List[Tuple[int, int]] = ((2, 2), (size - 3, 2), (size - 3, size - 3), (2, size - 3))
    lst_not_9: List[Tuple[int, int]] = ((3, 3), (size - 4, 3), (size - 4, size - 4), (3, size - 4))
    if size == 9:
        for item in lst9:
            node = self.board[item[0]][item[1]]
            pygame.draw.circle(window, (255, 165, 0), (node.screen_row, node.screen_col), circle_radius)
    else:
        for item in lst_not_9:
            node = self.board[item[0]][item[1]]
            pygame.draw.circle(window, (255, 165, 0), (node.screen_row, node.screen_col), circle_radius)


def switch_button_mode(board) -> None:
    '''Updates the button text in the PySimpleGui window'''
    if board.mode == "Scoring":
        board.window["Res"].update("Resume Game")
        board.times_passed = 0
    elif board.mode == "Playing":
        board.window["Res"].update("Quit Program")
    board.mode_change = False


def refresh_board_pygame(board) -> None:
    '''Refreshes the pygame screen to show the updated board'''
    board.screen.blit(board.backup_board, (0, 0))
    for board_row in board.board:
        for item in board_row:
            # Can do it better using if... in?
            if item.stone_here_color == cf.unicode_black or item.stone_here_color == cf.unicode_white:  # this is bad, fix
                pygame.draw.circle(board.screen, item.stone_here_color,
                                   (item.screen_row, item.screen_col), board.pygame_board_vals[2])
            elif item.stone_here_color == cf.unicode_diamond_black or item.stone_here_color == cf.unicode_diamond_white:
                pygame.draw.circle(board.screen, item.stone_here_color,
                                   (item.screen_row, item.screen_col), board.pygame_board_vals[2])
            elif item.stone_here_color == cf.unicode_triangle_black or item.stone_here_color == cf.unicode_triangle_white:
                pygame.draw.circle(board.screen, item.stone_here_color,
                                   (item.screen_row, item.screen_col), board.pygame_board_vals[2])
    pygame.display.update()


def close_window(board):  # Refactor? Why does linux not delete board.window
    '''Closes the pygame display and PySimpleGui window'''
    import platform
    if platform.system() == "Linux":
        board.window.close()
    elif platform.system() == "Windows":
        board.window.close()
        del board.window
        del board.backup_board
        pygame.display.quit()
