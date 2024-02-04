from unittest.mock import patch
import sys
import pytest
sys.path.append("/users/5/a1895735/Documents/PythonProjects/GoGame/")
import config as cf
import goclasses as go
import remove_dead as dead
from saving_loading import load_pkl


class TestClassPyTestRemoveDead:

    @pytest.fixture
    def fixture_window(self):
        with patch('PySimpleGUI.Window', autospec=True) as mock:
            yield mock.return_value

    @pytest.fixture
    def fixture_go_board(self) -> go.GoBoard:
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/unittest_remove_dead.pkl")
        the_board.piece_string = [[(0, 1), (255, 255, 255)], [(1, 1), (255, 255, 255)], [(1, 0), (255, 255, 255)]]
        return the_board

    @patch("uifunctions.refresh_board_pygame")
    def test_remove_dead_undo_list(self, mock_pygame, fixture_go_board):
        fixture_go_board.board[0][1].stone_here_color = cf.unicode_diamond_black
        fixture_go_board.board[1][1].stone_here_color = cf.unicode_diamond_white
        fixture_go_board.board[1][0].stone_here_color = cf.unicode_diamond_black
        dead.remove_dead_undo_list(fixture_go_board, fixture_go_board.piece_string)
        assert fixture_go_board.board[0][1].stone_here_color == cf.unicode_black
        assert fixture_go_board.board[1][1].stone_here_color == cf.unicode_white
        assert fixture_go_board.board[1][0].stone_here_color == cf.unicode_black

    @patch("uifunctions.refresh_board_pygame")
    def test_remove_stones_and_update_score(self, mock_pygame, fixture_go_board):
        dead.remove_stones_and_update_score(fixture_go_board, fixture_go_board.piece_string)
        assert fixture_go_board.board[0][1].stone_here_color == cf.unicode_none
        assert fixture_go_board.board[1][1].stone_here_color == cf.unicode_none
        assert fixture_go_board.board[1][0].stone_here_color == cf.unicode_none

    """@patch("uifunctions.refresh_board_pygame")
    def test_remove_dead_found_piece_white(self, mock_pygame, mocker, fixture_go_board):
        mocker.patch("scoringboard.ScoringBoard.flood_fill", return_value=(set((
            fixture_go_board.board[0][1], fixture_go_board.board[1][1], fixture_go_board.board[1][0])), set()))
        mocker.patch('PySimpleGUI.popup_yes_no', return_value="Yes")
        dead.remove_dead_found_piece(fixture_go_board, fixture_go_board.piece_string)
        assert fixture_go_board.board[0][1].stone_here_color == cf.unicode_diamond_white
        assert fixture_go_board.board[1][1].stone_here_color == cf.unicode_diamond_white
        assert fixture_go_board.board[1][0].stone_here_color == cf.unicode_diamond_white

    @patch("uifunctions.refresh_board_pygame")
    def test_remove_dead_found_piece_black(self, mock_pygame, mocker, fixture_go_board):
        fixture_go_board.board[0][0].stone_here_color = cf.unicode_black  # Illegal placement normally
        tmp = set()
        tmp.add(fixture_go_board.board[0][0])
        mocker.patch("scoringboard.ScoringBoard.flood_fill", return_value=(tmp, set()))
        mocker.patch('PySimpleGUI.popup_yes_no', return_value="Yes")
        dead.remove_dead_found_piece(fixture_go_board, fixture_go_board.piece_string)
        assert fixture_go_board.board[0][0].stone_here_color == cf.unicode_diamond_black"""

    @patch("uifunctions.update_scoring")
    @patch("uifunctions.refresh_board_pygame")
    @patch("uifunctions.def_popup")
    def test_remove_dead(self, mock_popup, mock_refresh, mock_scoring, mocker, fixture_go_board: go.GoBoard, fixture_window):
        mocker.patch("goclasses.GoBoard.find_piece_click", return_value=((True, fixture_go_board.board[0][1])))
        mocker.patch("remove_dead.remove_dead_found_piece", return_value=("Yes", [
            [(0, 1), (255, 255, 255)], [(1, 1), (255, 255, 255)], [(1, 0), (255, 255, 255)]]))
        mocker.patch("remove_dead.remove_stones_and_update_score")
        fixture_go_board.window = fixture_window
        fixture_window.read.return_value = ("button_click", {"-GRAPH-": (40, 117.5)})
        dead.remove_dead(fixture_go_board)

    @patch("uifunctions.update_scoring")
    @patch("uifunctions.refresh_board_pygame")
    @patch("uifunctions.def_popup")
    def test_remove_dead_no(self, mock_popup, mock_refresh, mock_scoring, mocker, fixture_go_board: go.GoBoard, fixture_window):
        mocker.patch("goclasses.GoBoard.find_piece_click", return_value=((True, fixture_go_board.board[0][1])))
        mocker.patch("remove_dead.remove_dead_found_piece", return_value=("No", [
            [(0, 1), (255, 255, 255)], [(1, 1), (255, 255, 255)], [(1, 0), (255, 255, 255)]]))
        mocker.patch("remove_dead.remove_stones_and_update_score")
        fixture_go_board.window = fixture_window
        fixture_window.read.return_value = ("button_click", {"-GRAPH-": (40, 117.5)})
        dead.remove_dead(fixture_go_board)

    @patch("uifunctions.update_scoring")
    @patch("uifunctions.refresh_board_pygame")
    @patch("uifunctions.def_popup")
    def test_remove_dead_res(self, mock_popup, mock_refresh, mock_scoring, mocker, fixture_go_board: go.GoBoard, fixture_window):
        mocker.patch("goclasses.GoBoard.find_piece_click", return_value=((True, fixture_go_board.board[0][1]))
                     )
        mocker.patch("remove_dead.remove_dead_found_piece", return_value=("No", [
            [(0, 1), (255, 255, 255)], [(1, 1), (255, 255, 255)], [(1, 0), (255, 255, 255)]]))
        mocker.patch("remove_dead.remove_stones_and_update_score")
        fixture_go_board.window = fixture_window
        fixture_window.read.return_value = ("Res", {"-GRAPH-": (40, 117.5)})
        dead.remove_dead(fixture_go_board)

    @patch("uifunctions.update_scoring")
    @patch("uifunctions.refresh_board_pygame")
    @patch("uifunctions.def_popup")
    def test_remove_dead_empty(self, mock_popup, mock_ref, mock_scoring, mocker, fixture_go_board: go.GoBoard, fixture_window):
        mocker.patch("goclasses.GoBoard.find_piece_click", side_effect=[
            ((True, fixture_go_board.board[0][0])), ((True, fixture_go_board.board[0][1]))])
        mocker.patch("remove_dead.remove_dead_found_piece", return_value=("No", [
            [(0, 1), (255, 255, 255)], [(1, 1), (255, 255, 255)], [(1, 0), (255, 255, 255)]]))
        mocker.patch("remove_dead.remove_stones_and_update_score")

        fixture_go_board.window = fixture_window
        fixture_window.read.side_effect = [("Test", {"-GRAPH-": (40, 40)}), ("SomeOtherEvent", {"-GRAPH-": (40, 117.5)})]
        dead.remove_dead(fixture_go_board)
