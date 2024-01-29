from goclasses import GoBoard, BoardNode
import uifunctions as ui
import PySimpleGUI as sg
from typing import Tuple, List, Set
import config as cf


def remove_dead(board: GoBoard) -> None:
    '''
    This function waits for player input to select dead stones, and then processes the removal of those stones.
    '''
    board.killed_last_turn.clear()
    ui.update_scoring(board)
    truth_value: bool = False
    while not truth_value:
        event, values = board.window.read()
        from turn_options import remove_dead_turn_options
        else_choice: bool = remove_dead_turn_options(board, event)
        if not else_choice:
            return
        row, col = values['-GRAPH-']
        found_piece, piece = board.find_piece_click([row, col])
        if found_piece and piece.stone_here_color == cf.unicode_none:
            ui.def_popup("You can't remove empty areas", 1)
        elif found_piece:
            other_user_agrees, piece_string = remove_dead_found_piece(board, piece)
            if other_user_agrees == "No":
                remove_dead_undo_list(board, piece_string)
                return

            remove_stones_and_update_score(board, piece_string)
            break
    board.switch_player()
    return


def remove_dead_found_piece(board: GoBoard, piece: BoardNode) -> Tuple[str, List[Tuple[Tuple[int, int], Tuple[int, int, int]]]]:
    '''
    Helper function for remove_dead().
    Uses floodfill to find all connected Nodes of the same color as the variable piece.
    Gets the agreement (or disagreement) of the other player.
    '''
    from scoringboard import ScoringBoard
    series: Tuple[Set[BoardNode], Set[BoardNode]] = ScoringBoard.flood_fill(piece)  # !
    piece_string: List[Tuple[Tuple[int, int], Tuple[int, int, int]]] = list()
    for item in series[0]:
        if item.stone_here_color == board.player_black.unicode:
            piece_string.append(((item.row, item.col), item.stone_here_color))
            item.stone_here_color = cf.unicode_diamond_black

        else:
            piece_string.append(((item.row, item.col), item.stone_here_color))
            item.stone_here_color = cf.unicode_diamond_white
    ui.refresh_board_pygame(board)
    info: str = "Other player, please click yes if you are ok with these changes"
    other_user_agrees: str = sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))
    return other_user_agrees, piece_string


def remove_dead_undo_list(board: GoBoard, piece_string: List[Tuple[Tuple[int, int], Tuple[int, int, int]]]) -> None:
    '''Undoes the removal of dead stones and revert the board to its previous state.'''
    for tpl in piece_string:
        item: BoardNode = board.board[tpl[0][0]][tpl[0][1]]
        if item.stone_here_color == cf.unicode_diamond_black:
            item.stone_here_color = board.player_black.unicode
        elif item.stone_here_color == cf.unicode_diamond_white:
            item.stone_here_color = board.player_white.unicode
    ui.refresh_board_pygame(board)


def remove_stones_and_update_score(board: GoBoard, piece_string: List[Tuple[Tuple[int, int], Tuple[int, int, int]]]) -> None:
    '''
    Helper function for remove_dead().
    Removes stones marked as dead during scoring and update player scores.
    '''
    for tpl in piece_string:
        item: BoardNode = board.board[tpl[0][0]][tpl[0][1]]
        item.stone_here_color = cf.unicode_none

    ui.refresh_board_pygame(board)
    temp_list: List[Tuple[Tuple[int, int, int], int, int, str]] = list()
    for item in piece_string:
        temp_list.append((item[1], item[0][0], item[0][1], "Scoring"))

    board.killed_log.append(temp_list)
    board.position_played_log.append("Dead Removed")
    board.turn_num += 1
