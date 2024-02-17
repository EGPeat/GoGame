from unittest.mock import patch, MagicMock, call
import sys
import pytest
sys.path.append("/users/5/a1895735/Documents/PythonProjects/GoGame/")
import botnormalgo as bot
import config as cf
import neuralnetboard as nn
from saving_loading import load_pkl
import player as pl
import goclasses as go
from goclasses import play_piece_bot


class TestClassPyTestNeuralNetBoard:

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

    @patch("uifunctions.update_scoring")
    @patch("uifunctions.refresh_board_pygame")
    @patch("uifunctions.def_popup")
    @patch('builtins.print')
    def test_play_turn_bot(self, fake_print, mock_popup, mock_refresh, mock_update):
        the_board: nn.NNBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/test_eyes.pkl")
        the_board.__class__ = nn.NNBoard
        the_board.ai_training_info = []
        the_board.ai_output_info = []
        the_board.make_turn_info()
        the_board.print_board()
        calls = [
            call('⛔⛔⛔⛔⛔⛔⛔⛔⛔'),
            call('⚪⚪⚪⛔⛔⛔⛔⛔⛔'),
            call('⚫⚫⚪⚪⚪⛔⛔⛔⛔'),
            call('⚫⛔⚫⚫⚪⛔⚪⛔⛔'),
            call('⚫⚫⛔⚫⚪⛔⚪⚪⚪'),
            call('⚫⚫⚫⚫⚪⛔⚪⚪⚪')]
        fake_print.assert_has_calls(calls, any_order=True)

    def test_init_nnsb(self):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/startscoring.pkl")
        test_sb = nn.NNScoringBoard(the_board)
        assert isinstance(test_sb, nn.NNScoringBoard)
        assert isinstance(test_sb.parent, go.GoBoard)
        assert test_sb.parent == the_board
        assert test_sb.player_black == test_sb.parent.player_black

    #def test_init_board(self):
    #    test_board = nn.initializing_game(9, True)
    #    assert isinstance(test_board.player_black, pl.Player)
    #    assert test_board.board_size == 9
    #    assert test_board.nn == test_board.nn_bad