from unittest.mock import patch
import pytest
import GoGame.config as cf
import GoGame.goclasses as go
import GoGame.remove_dead as dead
from GoGame.saving_loading import load_pkl


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

    @patch("GoGame.uifunctions.refresh_board_pygame")
    def test_remove_dead_undo_list(self, mock_pygame, fixture_go_board):
        fixture_go_board.board[0][1].stone_here_color = cf.rgb_peach
        fixture_go_board.board[1][1].stone_here_color = cf.rgb_lavender
        fixture_go_board.board[1][0].stone_here_color = cf.rgb_peach
        dead.remove_dead_undo_list(fixture_go_board, fixture_go_board.piece_string)
        assert fixture_go_board.board[0][1].stone_here_color == cf.rgb_black
        assert fixture_go_board.board[1][1].stone_here_color == cf.rgb_white
        assert fixture_go_board.board[1][0].stone_here_color == cf.rgb_black

    @patch("GoGame.uifunctions.refresh_board_pygame")
    def test_remove_stones_and_update_score(self, mock_pygame, fixture_go_board):
        dead.remove_stones_and_update_score(fixture_go_board, fixture_go_board.piece_string)
        assert fixture_go_board.board[0][1].stone_here_color == cf.rgb_grey
        assert fixture_go_board.board[1][1].stone_here_color == cf.rgb_grey
        assert fixture_go_board.board[1][0].stone_here_color == cf.rgb_grey

    @patch("GoGame.uifunctions.update_scoring")
    @patch("GoGame.uifunctions.refresh_board_pygame")
    @patch("GoGame.uifunctions.def_popup")
    def test_remove_dead(self, mock_popup, mock_refresh, mock_scoring, mocker, fixture_go_board: go.GoBoard, fixture_window):
        mocker.patch("GoGame.goclasses.GoBoard.find_piece_click", return_value=((True, fixture_go_board.board[0][1])))
        mocker.patch("GoGame.remove_dead.remove_dead_found_piece", return_value=("Yes", [
            [(0, 1), (255, 255, 255)], [(1, 1), (255, 255, 255)], [(1, 0), (255, 255, 255)]]))
        mocker.patch("GoGame.remove_dead.remove_stones_and_update_score")
        fixture_go_board.window = fixture_window
        fixture_window.read.return_value = ("button_click", {"-GRAPH-": (40, 117.5)})
        dead.remove_dead(fixture_go_board)

    @patch("GoGame.uifunctions.update_scoring")
    @patch("GoGame.uifunctions.refresh_board_pygame")
    @patch("GoGame.uifunctions.def_popup")
    def test_remove_dead_no(self, mock_popup, mock_refresh, mock_scoring, mocker, fixture_go_board: go.GoBoard, fixture_window):
        mocker.patch("GoGame.goclasses.GoBoard.find_piece_click", return_value=((True, fixture_go_board.board[0][1])))
        mocker.patch("GoGame.remove_dead.remove_dead_found_piece", return_value=("No", [
            [(0, 1), (255, 255, 255)], [(1, 1), (255, 255, 255)], [(1, 0), (255, 255, 255)]]))
        mocker.patch("GoGame.remove_dead.remove_stones_and_update_score")
        fixture_go_board.window = fixture_window
        fixture_window.read.return_value = ("button_click", {"-GRAPH-": (40, 117.5)})
        dead.remove_dead(fixture_go_board)

    @patch("GoGame.uifunctions.update_scoring")
    @patch("GoGame.uifunctions.refresh_board_pygame")
    @patch("GoGame.uifunctions.def_popup")
    def test_remove_dead_res(self, mock_popup, mock_refresh, mock_scoring, mocker, fixture_go_board: go.GoBoard, fixture_window):
        mocker.patch("GoGame.goclasses.GoBoard.find_piece_click", return_value=((True, fixture_go_board.board[0][1]))
                     )
        mocker.patch("GoGame.remove_dead.remove_dead_found_piece", return_value=("No", [
            [(0, 1), (255, 255, 255)], [(1, 1), (255, 255, 255)], [(1, 0), (255, 255, 255)]]))
        mocker.patch("GoGame.remove_dead.remove_stones_and_update_score")
        fixture_go_board.window = fixture_window
        fixture_window.read.return_value = ("Res", {"-GRAPH-": (40, 117.5)})
        dead.remove_dead(fixture_go_board)

    @patch("GoGame.uifunctions.update_scoring")
    @patch("GoGame.uifunctions.refresh_board_pygame")
    @patch("GoGame.uifunctions.def_popup")
    def test_remove_dead_empty(self, mock_popup, mock_ref, mock_scoring, mocker, fixture_go_board: go.GoBoard, fixture_window):
        mocker.patch("GoGame.goclasses.GoBoard.find_piece_click", side_effect=[
            ((True, fixture_go_board.board[0][0])), ((True, fixture_go_board.board[0][1]))])
        mocker.patch("GoGame.remove_dead.remove_dead_found_piece", return_value=("No", [
            [(0, 1), (255, 255, 255)], [(1, 1), (255, 255, 255)], [(1, 0), (255, 255, 255)]]))
        mocker.patch("GoGame.remove_dead.remove_stones_and_update_score")

        fixture_go_board.window = fixture_window
        fixture_window.read.side_effect = [("Test", {"-GRAPH-": (40, 40)}), ("SomeOtherEvent", {"-GRAPH-": (40, 117.5)})]
        dead.remove_dead(fixture_go_board)
