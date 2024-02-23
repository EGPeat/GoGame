from unittest.mock import patch, call
import GoGame.neuralnetboard as nn
from GoGame.saving_loading import load_pkl
import GoGame.goclasses as go


class TestClassPyTestNeuralNetBoard:

    @patch("GoGame.uifunctions.update_scoring")
    @patch("GoGame.uifunctions.refresh_board_pygame")
    @patch("GoGame.uifunctions.def_popup")
    @patch('builtins.print')
    def test_print_board_NNB(self, fake_print, mock_popup, mock_refresh, mock_update):
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

    # def test_init_board(self):
    #    test_board = nn.initializing_game(9, True)
    #    assert isinstance(test_board.player_black, pl.Player)
    #    assert test_board.board_size == 9
    #    assert test_board.nn == test_board.nn_bad
