import uifunctions as ui
import PySimpleGUI as sg
from typing import Optional


def choose_board_type(vs_bot: Optional[bool] = False, *args):
    '''
    This function is used in the initialization of the game...
    It chooses the correct type of board (GoBoard, BotBoard) based on a set of inputs.
    Parameters:
        vs_bot: If True, play against an AI opponent.
    '''
    if vs_bot:
        from botnormalgo import BotBoard
        return BotBoard(*args)
    else:
        from goclasses import GoBoard
        return GoBoard(*args)


def initializing_game(window, board_size: int, defaults: Optional[bool] = True,
                      vs_bot: Optional[bool] = False) -> None:
    '''
    Initialize a new game based on user preferences.
    Parameters:
        window: The pySimpleGui window for user interactions.
        board_size: The size of the game board.
        defaults: If True, use default settings;
            otherwise, allow the user to modify player names and komi.
        vs_bot: If True, play against an AI opponent.
    '''

    game_board = initialize_player_choice(board_size, defaults, vs_bot)
    window.close()
    ui.setup_board_window_pygame(game_board)
    handicap_info = False
    if not defaults:
        if request_handicap_info():
            handicap_info = True
    game_board.play_game(fixes_handicap=handicap_info)


def request_handicap_info() -> str:
    info: str = "Click yes if you want to modify the handicap"
    return sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))


def initialize_player_choice(board_size: int, defaults: Optional[bool] = True,
                             vs_bot: Optional[bool] = False):
    info: str = "Click yes if you want to modify the player names and komi"
    if not defaults:
        modify_player: str = (sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15)))
        if modify_player == "No":
            defaults = True
    return choose_board_type(vs_bot, board_size, defaults)
