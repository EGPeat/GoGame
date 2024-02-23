from unittest.mock import patch, MagicMock, call
import pytest
import PySimpleGUI as sg
import GoGame.turn_options as topt


class TestClassPyTestTurnOptions:

    @pytest.fixture
    def mock_gboard(self):
        with patch("GoGame.goclasses.GoBoard") as mock_goboard:
            mock_goboard.times_passed = 0
            mock_goboard.turn_num = 0
            mock_goboard.position_played_log.append(("text", -4, -4))
            mock_goboard.killed_log = ["Testing"]
            mock_goboard.player_black = MagicMock()
            mock_goboard.player_white = MagicMock()
            mock_goboard.whose_turn = mock_goboard.player_black
            mock_goboard.not_whose_turn = mock_goboard.player_white
            return mock_goboard

    def test_normal_turn_options_quit(self, mock_gboard):
        with pytest.raises(SystemExit):
            topt.normal_turn_options(mock_gboard, sg.WIN_CLOSED, "Quitting Game")

    def test_normal_turn_options_res(self, mock_gboard):
        with pytest.raises(SystemExit):
            topt.normal_turn_options(mock_gboard, "Res", "Quitting Game")

    @patch("GoGame.goclasses.GoBoard.switch_player")
    @patch("GoGame.uifunctions.def_popup")
    def test_normal_turn_options_pass(self, mock_popup, mock_switch_player, mock_gboard):
        topt.normal_turn_options(mock_gboard, "Pass Turn", "Passing")
        assert mock_gboard.turn_num == 1
        assert mock_gboard.times_passed == 1
        expected_calls = [call.append(('text', -4, -4)), call.append(('Passing', -3, -3))]
        mock_gboard.position_played_log.assert_has_calls(expected_calls, any_order=True)
        assert mock_gboard.killed_log == ["Testing", []]

    @patch("GoGame.main.play_game_main")
    @patch("GoGame.uifunctions.close_window")
    def test_normal_turn_options_exit_game(self, mock_pgm, mock_close_window, mock_gboard):
        with pytest.raises(SystemExit):
            topt.normal_turn_options(mock_gboard, "Exit Game", "Exit Game Test")
            mock_gboard.close.assert_called_once()
            mock_pgm.assert_called_once()

    def test_normal_turn_options_bad_input(self, mock_gboard):
        with pytest.raises(ValueError):
            topt.normal_turn_options(mock_gboard, "Bad Input", "Quitting Game")

    @patch("GoGame.saving_loading.save_pickle")
    def test_normal_turn_options_save_game(self, mock_pickle, mock_gboard):
        topt.normal_turn_options(mock_gboard, "Save Game", "Save Game Test")
        mock_pickle.assert_called_once_with(mock_gboard)

    @patch("GoGame.uifunctions.def_popup")
    def test_normal_turn_options_undo_turn_zero(self, mock_popup, mock_gboard):
        topt.normal_turn_options(mock_gboard, "Undo Turn", "Undo Turn Test")
        mock_popup.assert_called_once()

    @patch("GoGame.undoing.undo_checker")
    def test_normal_turn_options_undo_turn_one(self, mock_undo, mock_gboard):
        mock_gboard.turn_num = 1
        topt.normal_turn_options(mock_gboard, "Undo Turn", "Undo Turn Test")
        mock_undo.assert_called_once()

    @patch("GoGame.goclasses.GoBoard.switch_player")
    @patch("GoGame.uifunctions.def_popup")
    def test_remove_dead_turn_option_pass(self, mock_popup, mock_switch_player, mock_gboard):
        topt.remove_dead_turn_options(mock_gboard, "Pass Turn")
        assert mock_gboard.turn_num == 1
        assert mock_gboard.times_passed == 1
        expected_calls = [call.append(('text', -4, -4)), call.append(('Scoring Passed', -3, -3))]
        mock_gboard.position_played_log.assert_has_calls(expected_calls, any_order=True)
        assert mock_gboard.killed_log == ["Testing", []]

    @patch("GoGame.uifunctions.def_popup")
    def test_remove_dead_turn_options_undo_turn_zero(self, mock_popup, mock_gboard):
        topt.remove_dead_turn_options(mock_gboard, "Undo Turn")
        mock_popup.assert_called_once()

    @patch("GoGame.undoing.undo_checker")
    def test_remove_dead_turn_options_undo_turn_one(self, mock_undo, mock_gboard):
        mock_gboard.turn_num = 1
        topt.remove_dead_turn_options(mock_gboard, "Undo Turn")
        mock_undo.assert_called_once()

    @patch("GoGame.saving_loading.save_pickle")
    def test_remove_dead_turn_options_save_game(self, mock_pickle, mock_gboard):
        topt.remove_dead_turn_options(mock_gboard, "Save Game")
        mock_pickle.assert_called_once_with(mock_gboard)

    def test_remove_dead_turn_options_bad_input(self, mock_gboard):
        answer = topt.remove_dead_turn_options(mock_gboard, "Bad Input")
        assert answer is True

    @patch("GoGame.main.play_game_main")
    @patch("GoGame.uifunctions.close_window")
    def test_return_dead_turn_options_exit_game(self, mock_pgm, mock_close_window, mock_gboard):
        with pytest.raises(SystemExit):
            topt.remove_dead_turn_options(mock_gboard, "Exit Game")
            mock_gboard.close.assert_called_once()
            mock_pgm.assert_called_once()

    def test_return_dead_turn_options_quit(self, mock_gboard):
        with pytest.raises(SystemExit):
            topt.remove_dead_turn_options(mock_gboard, sg.WIN_CLOSED)

    @patch("GoGame.goclasses.GoBoard.resuming_scoring_buffer")
    def test_return_dead_turn_options_pass(self, mock_scoring_buffer, mock_gboard):
        mock_gboard.mode = "Scoring"
        mock_gboard.mode_change = False
        topt.remove_dead_turn_options(mock_gboard, "Res")
        assert mock_gboard.mode == "Playing"
        assert mock_gboard.mode_change is True
        mock_gboard.resuming_scoring_buffer.assert_called_once()
