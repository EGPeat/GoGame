import PySimpleGUI as sg
import pygame
from typing import Union
from GoGame.goclasses import GoBoard


def move_to_pkl_directory() -> str:
    "Finds the current directory, then moves into it's pklfiles subdirectory, if it is not already there. Returns the file_path."
    from os import chdir, getcwd, path
    wd = getcwd()
    full_path = path.join(wd, 'pklfiles')
    if not wd.endswith('pklfiles'):
        chdir(full_path)
        return full_path
    else:
        return wd


def save_pickle(board: GoBoard) -> None:
    '''Saves the game to a pkl in the correct pklfiles folder. Does not allow overwriting a filename.'''
    import pickle
    filename = save_pickle_name_choice()
    if filename is None or filename == "" or filename.strip() == "":
        return
    with open(f"{filename}", "wb") as pkl_file:
        backup_window: sg.Window = board.window
        backup_screen: pygame.Surface = board.screen
        backup_backup_board: pygame.Surface = board.backup_board
        del board.window
        del board.screen
        del board.backup_board
        pickle.dump(board, pkl_file)
        board.window = backup_window
        board.screen = backup_screen
        board.backup_board = backup_backup_board
        del backup_window
        del backup_screen
        del backup_backup_board


def save_pickle_name_choice() -> Union[None, str]:
    """Asks the user for a filename, checks that that filename is not already in use.
    Returns the filename as a string (or returns nothing)."""
    from os import path
    from time import sleep
    from GoGame.uifunctions import default_popup_no_button
    full_path = move_to_pkl_directory()
    filename: str = ''
    while len(filename) < 1:
        text: str = "Please write the name of the file you want to save to. Do not include the file extension."
        filename: str = (sg.popup_get_text(text, title="Please Enter Text", font=('Arial Bold', 15)))
        if filename is None:
            return
        filename = path.join(full_path, f"{filename}.pkl")
        if path.isfile(filename):
            filename = ''
            text: str = "That file already exists, please enter a different choice for filename."
            default_popup_no_button(text, 2)
            sleep(2)
    return filename


def load_pkl(inputPath):
    '''Loads the current state of the game from a pkl file. Returns a GoBoard or BotBoard.'''
    import pickle
    with open(inputPath, 'rb') as file:
        friend = pickle.load(file)
    return friend


def choose_file(window) -> None:
    "Allows the user to choose a pickle file to load their game from."
    from GoGame.uifunctions import setup_board_window_pygame
    move_to_pkl_directory()
    file = sg.popup_get_file('Select a file', title="File selector", font=('Arial Bold', 15))
    if file is None or file == "":
        return
    file = file.split("/")
    file = file[-1]
    sg.popup_no_buttons('You chose', file, non_blocking=True, font=('Arial Bold', 15),
                        auto_close=True, auto_close_duration=3)
    friend = load_pkl(file)
    setup_board_window_pygame(friend)
    window.close()
    friend.play_game(from_file=True, fixes_handicap=False)
    return
