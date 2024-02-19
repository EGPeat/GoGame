import PySimpleGUI as sg
import uifunctions as ui
from goclasses import GoBoard
from typing import Optional


def normal_turn_options(board: GoBoard, event, text: Optional[str] = None) -> None:
    '''
    Handles various game options based on the given event.
    Options include (Pass Turn, Res, WIN_CLOSED, Save Game, Undo Turn, Exit Game).
    When in scoring mode, Res stands for Resume Game, otherwise it means Quit Program.
    '''
    if event in (sg.WIN_CLOSED, "Res"):
        quit()
    if event == "Pass Turn":
        ui.def_popup("Skipped turn", 0.5)
        board.times_passed += 1
        board.turn_num += 1
        board.position_played_log.append((text, -3, -3))
        board.killed_log.append([])
        board.switch_player()
    elif event == "Save Game":
        from saving_loading import save_pickle
        save_pickle(board)
    elif event == "Undo Turn":
        if board.turn_num == 0:
            ui.def_popup("You can't undo when nothing has happened.", 2)
        elif board.turn_num >= 1:
            from undoing import undo_checker
            undo_checker(board)
            return
    elif event == "Exit Game":
        from main import play_game_main
        ui.close_window(board)
        play_game_main()
        quit()
    else:
        raise ValueError


def remove_dead_turn_options(board: GoBoard, event) -> bool:
    '''Handles events related to removing dead stones during scoring. Only returns True if the player clicked a piece.'''
    if event == "Pass Turn":
        normal_turn_options(board, event, text="Scoring Passed")
        return False
    elif event == "Save Game":
        from saving_loading import save_pickle
        save_pickle(board)
        return False
    elif event == "Res":
        board.mode = "Playing"
        board.mode_change = True
        board.resuming_scoring_buffer("Resumed")
        return False
    elif event == "Undo Turn":
        normal_turn_options(board, event)
        return False
    elif event == "Exit Game":
        normal_turn_options(board, event)
    elif event == sg.WIN_CLOSED:
        quit()
    else:
        return True
