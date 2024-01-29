
import PySimpleGUI as sg
import pygame
from typing import Type
from goclasses import GoBoard


def save_to_SGF(board: GoBoard, filename2: str) -> None:
    '''Saves the current game to a SGF file.'''
    with open(f"{filename2}.sgf", 'w', encoding='utf-8') as file:
        from datetime import date
        seqs = ["Dead Removed", "Break between handicaps and normal play", "Dead Removed",
                "Resumed", "Scoring", "Scoring Passed"]
        movement_string: str = ""
        today = date.today()
        header: str = f"(;\nFF[4]\nCA[UTF-8]\nGM[1]\nDT[{today}]\nGN[relaxed]\n\
        PC[https://github.com/EGPeat/GoGame]\n\
        PB[{board.player_black.name}]\n\
        PW[{board.player_white.name}]\n\
        BR[Unknown]\nWR[Unknown]\n\
        OT[Error: time control missing]\nRE[?]\n\
        SZ[{board.board_size}]\nKM[{board.player_white.komi}]\nRU[Japanese];"
        file.write(header)
        handicap_flag: bool = board.handicap[0]
        for idx, item in enumerate(board.position_played_log):
            if handicap_flag and idx < board.handicap[2]:
                color: str = 'B' if board.handicap[1] == "Black" else 'W'
                row: str = chr(97 + int(item[1]))
                col: str = chr(97 + int(item[2]))
                text: str = f";{color}[{col}{row}]\n"
                movement_string += text
            elif item[0] in seqs or item in seqs:
                pass
            elif item[0] == "Passed":
                if movement_string[-7] == "B" or movement_string[-5] == "B":
                    text2: str = ";W[]\n"
                else:
                    text2: str = ";B[]\n"
                movement_string += text2
            else:
                row: str = chr(97 + int(item[1]))
                col: str = chr(97 + int(item[2]))
                color: str = 'B' if item[0] == board.player_black.color else 'W'
                text: str = f";{color}[{col}{row}]\n"
                movement_string += text
        movement_string += ")"
        file.write(movement_string)


def save_pickle(board: GoBoard) -> None:
    '''Saves the game to a pkl in the correct pklfiles folder'''
    import pickle
    from os import chdir, getcwd, path
    wd = getcwd()
    full_path = path.join(wd, 'pklfiles')
    if not wd.endswith('pklfiles'):
        chdir(full_path)
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


def load_pkl(inputPath) -> Type['GoBoard']:
    '''Loads the current state of the game from a pkl file.'''
    import pickle
    with open(inputPath, 'rb') as file:
        friend = pickle.load(file)
    return friend
