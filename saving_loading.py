
import PySimpleGUI as sg
import pygame
from typing import Type
from goclasses import GoBoard


def move_to_pkl_directory():
    from os import chdir, getcwd, path
    wd = getcwd()
    full_path = path.join(wd, 'pklfiles')
    if not wd.endswith('pklfiles'):
        chdir(full_path)
        return full_path
    else:
        return wd


def save_pickle(board: GoBoard) -> None:
    '''Saves the game to a pkl in the correct pklfiles folder'''
    import pickle
    from os import path
    full_path = move_to_pkl_directory()
    filename: str = ''
    while len(filename) < 1:
        text: str = "Please write the name of the file you want to save to. Do not include the file extension."
        filename: str = (sg.popup_get_text(text, title="Please Enter Text", font=('Arial Bold', 15)))
        if filename is None:
            return
    filename = path.join(full_path, f"{filename}")
    with open(f"{filename}.pkl", "wb") as pkl_file:
        backup_window: sg.Window = board.window
        backup_screen: pygame.Surface = board.screen
        backup_backup_board: pygame.Surface = board.backup_board
        del board.window
        del board.screen
        del board.backup_board
        pickle.dump(board, pkl_file)
        board.window: sg.Window = backup_window
        board.screen: pygame.Surface = backup_screen
        board.backup_board: pygame.Surface = backup_backup_board
        del backup_window
        del backup_screen
        del backup_backup_board


def load_pkl(inputPath) -> Type['GoBoard']:
    '''Loads the current state of the game from a pkl file.'''
    import pickle
    with open(inputPath, 'rb') as file:
        friend: Type['GoBoard'] = pickle.load(file)
    return friend


def choose_file(window):
    from uifunctions import setup_board_window_pygame
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
