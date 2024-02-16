from unittest.mock import patch, MagicMock
import sys
import pytest
sys.path.append("/users/5/a1895735/Documents/PythonProjects/GoGame/")
import PySimpleGUI as sg
import goclasses as go
from player import Player
import config as cf
from saving_loading import load_pkl


class TestClassPyTestGoClasses:

    @pytest.fixture
    def mock_window(self):
        with patch('PySimpleGUI.Window', autospec=True) as mock:
            yield mock.return_value

    def test_read_window(self, mock_window):
        theboard = go.GoBoard()
        theboard.window = mock_window
        mock_window.read.return_value = ("button_click", {"input_field": "user_input"})
        event, values = theboard.read_window()
        assert event == "button_click"
        assert values == {"input_field": "user_input"}
        mock_window.read.assert_called_once()

    def test_switch_player(self):
        mock_goboard = MagicMock()
        mock_goboard.player_black = "Player Black"
        mock_goboard.player_white = "Player White"
        mock_goboard.whose_turn = mock_goboard.player_black
        mock_goboard.not_whose_turn = mock_goboard.player_white
        go.GoBoard.switch_player(mock_goboard)
        assert mock_goboard.not_whose_turn == mock_goboard.player_black
        assert mock_goboard.whose_turn == mock_goboard.player_white

    def test_switch_player_white(self):
        mock_goboard = MagicMock()
        mock_goboard.player_black = "Player Black"
        mock_goboard.player_white = "Player White"
        mock_goboard.whose_turn = mock_goboard.player_white
        mock_goboard.not_whose_turn = mock_goboard.player_black
        go.GoBoard.switch_player(mock_goboard)
        assert mock_goboard.not_whose_turn == mock_goboard.player_white
        assert mock_goboard.whose_turn == mock_goboard.player_black

    def test_switch_player_obj(self):
        mock_goboard = MagicMock()
        mock_goboard.player_black = Player.setup_player(True, "Player One", "Black", go.cf.unicode_black)
        mock_goboard.player_white = Player.setup_player(True, "Player Two", "White", go.cf.unicode_white)
        mock_goboard.whose_turn = mock_goboard.player_black
        mock_goboard.not_whose_turn = mock_goboard.player_white
        go.GoBoard.switch_player(mock_goboard)
        assert mock_goboard.not_whose_turn == mock_goboard.player_black
        assert mock_goboard.whose_turn == mock_goboard.player_white

    """def test_make_board_string_correct(self):
        go_board = go.GoBoard(9, True)
        go_board.board[0][1].stone_here_color = cf.unicode_black
        answer = go_board.make_board_string()
        print(answer)
        assert answer == '1010000000000000000000000000000000000000000000000000000000000000000000000000000000'"""

    def test_make_board_string_incorrect(self):
        go_board = go.GoBoard(9, True)
        go_board.board[0][1].stone_here_color = cf.unicode_black
        go_board.board[0][3].stone_here_color = cf.unicode_white
        answer = go_board.make_board_string()
        print(answer)
        assert answer == '1000000000100000000000000000200000000000000000000000000000000000000000000000000000'

    def test_print_board_node_incorrect(self):
        go_board = go.GoBoard(9, True)
        go_board.board[0][1].stone_here_color = cf.unicode_black
        go_board.board[0][3].stone_here_color = cf.unicode_white
        go_board.board[0][5].stone_here_color = cf.unicode_black
        go_board.board[0][7].stone_here_color = cf.unicode_white
        answer = []
        correct = ["This is a BoardNode with coordinates of (0,0) and a stone of (120, 120, 120)",
                   "This is a BoardNode with coordinates of (0,1) and a stone of (0, 0, 0)",
                   "This is a BoardNode with coordinates of (0,2) and a stone of (120, 120, 120)",
                   "This is a BoardNode with coordinates of (0,3) and a stone of (255, 255, 255)",
                   "This is a BoardNode with coordinates of (0,4) and a stone of (120, 120, 120)",
                   "This is a BoardNode with coordinates of (0,5) and a stone of (0, 0, 0)",
                   "This is a BoardNode with coordinates of (0,6) and a stone of (120, 120, 120)",
                   "This is a BoardNode with coordinates of (0,7) and a stone of (255, 255, 255)",
                   "This is a BoardNode with coordinates of (0,8) and a stone of (120, 120, 120)"]
        for idx in range(9):
            answer.append(str(go_board.board[0][idx]))
        assert answer == correct

    @pytest.mark.parametrize("ret_val", [("Exit Game"), (sg.WIN_CLOSED)])
    @patch("main.play_game_main")
    @patch("uifunctions.refresh_board_pygame")
    @patch("uifunctions.close_window")
    def test_allow_view_endgame(self, mock_close_window, mock_pygame, mock_pgm, ret_val, mocker):
        with pytest.raises(SystemExit):
            go_board = go.GoBoard(9, True)
            mocker.patch("goclasses.GoBoard.read_window", return_value=((ret_val), 5))
            go_board.play_game_view_endgame()
            assert go_board.quit.call_count == 1

    @pytest.mark.parametrize("location, result, who", [
        ((0, 1), (0, 0), ("Black")),
        ((3, 3), (3, 4), ("White"))
    ])
    def test_kill_stones_mocked_self_death(self, location, result, who):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/test_killing.pkl")
        if who != "White":  # This is to allow black to capture/kill
            the_board.switch_player()
        the_board.board[2][2].stone_here_color = cf.unicode_black
        the_piece = the_board.board[location[0]][location[1]]
        the_board.kill_stones(the_piece)
        assert the_board.board[result[1]][result[0]].stone_here_color == cf.unicode_none

    @pytest.mark.parametrize("location", [
        ((0, 0)), ((1, 0)), ((3, 3)), ((8, 8)), ((7, 5)), ((8, 6))])
    @patch("uifunctions.refresh_board_pygame")
    @patch("uifunctions.def_popup")
    def test_play_pieces(self, mock_popup, mock_refresh, location):  # This ordering makes no sense. Definitely a x/y problem
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/test_ko.pkl")
        the_board.board[2][2].stone_here_color = cf.unicode_black
        successful = the_board.play_piece(location[1], location[0])

        if location == (0, 0):
            assert successful is not True
        if location == (1, 0):
            assert successful is True
            assert the_board.board[0][0].stone_here_color == cf.unicode_none
        if location == (5, 7):  # This part is definitely not correct
            assert successful is not True
        if location == (8, 8):
            assert successful is True
        if location == (8, 6):
            assert successful is not True

    @pytest.mark.parametrize("location", [
        ((40, 40)), ((60, 40)), ((80, 40)), ((40, 60))])
    def test_find_piece_click(self, location):
        the_board = go.GoBoard(9)
        the_board.pygame_board_vals = [700, 620 / 8, 620 / 24]
        answer = the_board.find_piece_click((location[0], location[1]))
        if location == (40, 40):
            assert answer[0] is True
            assert answer[1].row == 0
            assert answer[1].col == 0
        if location == (70, 40):
            assert answer[0] is False
        if location == (100, 40):
            assert answer[0] is False
        if location == (40, 70):
            assert answer[0] is False

    @patch("uifunctions.refresh_board_pygame")
    @patch("uifunctions.def_popup")
    @patch("uifunctions.update_scoring")
    @patch("goclasses.GoBoard.read_window", return_value=(("Pass Turn"), (5)))
    def test_play_turn_pass(self, mock_read, mock_update, mock_popup, mock_refresh):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/test_ko.pkl")
        the_board.board[2][2].stone_here_color = cf.unicode_black
        the_board.play_turn()

    @patch("uifunctions.refresh_board_pygame")
    @patch("uifunctions.def_popup")
    @patch("uifunctions.update_scoring")
    @patch("pygame.draw.circle")
    @patch("pygame.display.update")
    def test_play_turn_normal(self, mock_display, mock_draw_circle, mock_update, mock_popup, mock_refresh, mocker):
        the_board: go.GoBoard = go.GoBoard(9)
        the_board.pygame_board_vals = [700, 620 / 8, 620 / 24]
        mocker.patch("goclasses.GoBoard.read_window", return_value=('-GRAPH-', {'-GRAPH-': (2, 3)}))
        mocker.patch("goclasses.GoBoard.find_piece_click", return_value=((True, the_board.board[8][8])))
        the_board.play_turn()

    @patch("uifunctions.refresh_board_pygame")
    @patch("uifunctions.def_popup")
    @patch("uifunctions.update_scoring")
    @patch("pygame.draw.circle")
    @patch("pygame.display.update")
    def test_play_turn_capture(self, mock_display, mock_draw_circle, mock_update, mock_popup, mock_refresh, mocker, mock_window):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/test_ko.pkl")
        the_board.screen = mock_window
        the_board.pygame_board_vals = [700, 620 / 8, 620 / 24]
        mocker.patch("goclasses.GoBoard.read_window", return_value=('-GRAPH-', {'-GRAPH-': (0, 1)}))
        mocker.patch("goclasses.GoBoard.find_piece_click", return_value=((True, the_board.board[0][1])))
        the_board.play_turn()

    @pytest.mark.parametrize("location, result", [
        ((0, 0), (1, [(1, 1)])),
        ((0, 1), (2, [(1, 0), (1, 2)])),
        ((1, 1), (4, [(2, 2), (0, 0), (2, 0), (0, 2)]))
    ])
    def test_diagonal_setup(self, location, result):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/test_ko.pkl")
        piece = the_board.board[location[0]][location[1]]
        result_set = the_board.diagonals_setup(piece)
        neighbors = set()
        for idx in range(result[0]):
            neighbors.add(the_board.board[result[1][idx][0]][result[1][idx][1]])
        assert len(result_set) == result[0]
        assert result_set == neighbors
