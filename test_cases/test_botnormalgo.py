from unittest.mock import patch, MagicMock
import sys
import pytest
sys.path.append("/users/5/a1895735/Documents/PythonProjects/GoGame/")
import botnormalgo as bot
import config as cf
from saving_loading import load_pkl


class TestClassPyTestBotNormalGo:

    @pytest.fixture
    def mock_window(self):
        with patch('PySimpleGUI.Window', autospec=True) as mock:
            yield mock.return_value

    def test_read_window(self, mock_window):
        instance_under_test = bot.GoBoard()
        instance_under_test.window = mock_window
        mock_window.read.return_value = ("button_click", {"input_field": "user_input"})
        event, values = instance_under_test.read_window()
        assert event == "button_click"
        assert values == {"input_field": "user_input"}
        mock_window.read.assert_called_once()

    def test_switch_player(self):
        mock_goboard = MagicMock()
        mock_goboard.player_black = "Player Black"
        mock_goboard.player_white = "Player White"
        mock_goboard.whose_turn = mock_goboard.player_black
        mock_goboard.not_whose_turn = mock_goboard.player_white
        bot.GoBoard.switch_player(mock_goboard)
        assert mock_goboard.not_whose_turn == mock_goboard.player_black
        assert mock_goboard.whose_turn == mock_goboard.player_white

    @pytest.mark.parametrize("location, result", [
        ((7, 2), (True)),
        ((4, 4), (False)),
        ((1, 1), (False))
    ])
    def test_fills_eyes(self, location, result):
        the_board: bot.BotBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/test_eyes.pkl")
        the_board.__class__ = bot.BotBoard
        piece = the_board.board[location[0]][location[1]]
        output = the_board.fills_eye(piece)
        assert result == output

    @pytest.mark.parametrize("location, result", [
        ((7, 2), (False)),
        ((4, 4), (False)),
        ((1, 1), (False))
    ])
    def test_fills_eyes_two(self, location, result):
        the_board: bot.BotBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/test_eyes_free.pkl")
        the_board.__class__ = bot.BotBoard
        piece = the_board.board[location[0]][location[1]]
        output = the_board.fills_eye(piece)
        assert result == output

    @pytest.mark.parametrize("location", [
        ((0, 0)), ((0, 1)), ((3, 3)), ((8, 8)), ((5, 7)), ((6, 8))])
    @patch("uifunctions.refresh_board_pygame")
    @patch("uifunctions.def_popup")
    def test_play_pieces_botboard(self, mock_popup, mock_refresh, location):
        the_board: bot.BotBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/test_ko.pkl")
        the_board.__class__ = bot.BotBoard
        the_board.board[2][2].stone_here_color = cf.unicode_black
        successful = the_board.play_piece_bot(location[1], location[0])

        if location == (0, 0):
            assert successful is not True
        if location == (0, 1):
            assert successful is True
            assert the_board.board[0][0].stone_here_color == cf.unicode_none
        if location == (7, 5):
            assert successful is not True
        if location == (8, 8):
            assert successful is True
        if location == (6, 8):
            assert successful is not True

    @pytest.mark.parametrize("location", [
        ((2, 7)), ((1, 6))])
    @patch("uifunctions.refresh_board_pygame")
    @patch("uifunctions.def_popup")
    def test_play_pieces_botboard_fills_eye(self, mock_popup, mock_refresh, location):
        the_board: bot.BotBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/test_eyes.pkl")
        the_board.__class__ = bot.BotBoard
        successful = the_board.play_piece_bot(location[1], location[0])

        assert the_board.board[6][0].stone_here_color == cf.unicode_black
        assert the_board.board[6][2].stone_here_color == cf.unicode_black
        assert successful is False

    @pytest.mark.parametrize("location, result", [
        ((72), (-3, -3)),
        ((10), (1, 1))
    ])
    @patch("uifunctions.update_scoring")
    @patch("uifunctions.refresh_board_pygame")
    @patch("uifunctions.def_popup")
    def test_play_turn_bot(self, mock_popup, mock_refresh, mock_update, location, result, mocker):
        the_board: bot.BotBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/test_eyes.pkl")
        the_board.__class__ = bot.BotBoard
        mocker.patch("botnormalgo.randrange", return_value=location)
        the_board.play_turn_bot()
        assert [the_board.position_played_log[-1][1]] == [result[0]]
        assert [the_board.position_played_log[-1][2]] == [result[1]]
