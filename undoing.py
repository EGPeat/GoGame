import config as cf
from typing import Tuple, Optional
from goclasses import BoardNode, GoBoard
import uifunctions as ui


def undo_checker(board: GoBoard) -> None:
    '''Calls the undo_turn function with appropriate parameters'''
    if board.mode == "Scoring":
        undo_turn(board, scoring=True)
    else:
        undo_turn(board)


def undo_turn(board: GoBoard, scoring: Optional[bool] = False) -> None:
    '''Undo the most recent turn, reverting the board to its state one turn ago.'''
    if undo_special_cases(board):
        return
    if not scoring:
        _, row, col = board.position_played_log.pop()
        board.board[row][col].stone_here_color = cf.rgb_grey
    else:
        board.position_played_log.pop()
    revive = board.killed_log.pop()

    if len(revive) > 0:
        unicode: Tuple[int, int, int] = revive[0][0]
    else:
        unicode: Tuple[int, int, int] = cf.rgb_grey
    for item in revive:
        if not scoring:
            unicode, row, col = item
        else:
            unicode, row, col, scoring = item
        place: BoardNode = board.board[row][col]
        place.stone_here_color = unicode
    ui.refresh_board_pygame(board)
    board.turn_num -= 1
    board.switch_player()


def undo_special_cases(board: GoBoard) -> bool:
    '''Handle special cases during undo, such as resuming scoring or handling consecutive passes.'''
    last_entry: str = board.position_played_log[-1]

    if last_entry == "Resumed" or last_entry == "Scoring":
        tmp: str = board.position_played_log.pop()
        move_back(board)
        board.turn_num -= 1
        board.mode_change = True

        if tmp == "Resumed":
            board.mode = "Scoring"
            board.times_passed = 2
        elif tmp == "Scoring":
            board.mode = "Playing"
        return True

    if last_entry[0] in {"Passed", "Scoring Passed"}:
        board.position_played_log.pop()
        move_back(board)
        board.turn_num -= 1
        board.times_passed = 0

        if board.position_played_log and board.position_played_log[-1][0] in {"Passed", "Scoring Passed"}:
            board.times_passed = 1

        board.switch_player()
        return True
    return False


def move_back(board: GoBoard) -> None:
    '''Move back to the previous killed state, updating board.killed_last_turn.'''
    if len(board.killed_log) > 0:
        board.killed_last_turn.clear()
        temp_list = board.killed_log.pop()
        for item in temp_list:
            temp_node = BoardNode(row_value=item[1], col_value=item[2])
            board.killed_last_turn.add(temp_node)
