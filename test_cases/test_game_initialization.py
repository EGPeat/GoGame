import unittest
from unittest.mock import patch, MagicMock
import sys
import pytest
sys.path.append("/users/5/a1895735/Documents/PythonProjects/GoGame/")
import goclasses as go
import game_initialization as start
from botnormalgo import BotBoard


class TestClassPyTestGameInit:
    @pytest.mark.parametrize("input, output, popup", [(False, True, "Yes"), (False, False, "No")])
    def test_handicap_choices(self, input, output, mocker, popup):
        mocker.patch('PySimpleGUI.popup_yes_no', return_value=popup)
        answer = start.initialize_handicap_choice(input)
        assert (answer == output)

    @pytest.mark.parametrize("input, output", [(True, False)])
    def test_handicap_choices_defaults(self, input, output):
        answer = start.initialize_handicap_choice(input)
        assert (answer == output)

    @pytest.mark.parametrize("vs_bot, output", [(True, BotBoard), (False, go.GoBoard)])
    def test_initialize_player_choice_default(self, vs_bot, output):
        board_size = 9
        defaults = True
        answer = start.initialize_player_choice(board_size, defaults, vs_bot)
        assert (isinstance(answer, output) is True)

    @pytest.mark.parametrize("vs_bot, popup",
                             [(True, "Yes"), (False, "Yes"),
                              (True, "No"), (False, "No")])
    def test_initialize_player_choice_not_default(self, vs_bot, mocker, popup):
        defaults = False
        mocker.patch('PySimpleGUI.popup_yes_no', return_value=popup)
        mocker.patch('game_initialization.choose_board_type')
        start.initialize_player_choice(9, defaults, vs_bot)
        if popup == "No":
            start.choose_board_type.assert_called_once_with(vs_bot, 9, True)
        else:
            start.choose_board_type.assert_called_once_with(vs_bot, 9, defaults)


class TestClassGameInit(unittest.TestCase):
    def test_choose_board_type_go_board(self):
        self.assertIsInstance(start.choose_board_type(True, 9, True), BotBoard)

    def test_choose_board_type_bot_board(self):
        self.assertIsInstance(start.choose_board_type(False, 9, True), go.GoBoard)

    @patch("game_initialization.initialize_player_choice")
    @patch("game_initialization.ui.setup_board_window_pygame")
    @patch("game_initialization.request_handicap_info")
    def test_initializing_game_with_defaults(self, mock_request_handicap_info, mock_setup_board, mock_initialize_player_choice):
        window_mock = MagicMock()
        board_size = 9

        start.initializing_game(window_mock, board_size)

        mock_initialize_player_choice.assert_called_once_with(board_size, True, False)
        mock_setup_board.assert_called_once_with(mock_initialize_player_choice.return_value)
        mock_request_handicap_info.assert_not_called()
        mock_initialize_player_choice.return_value.play_game.assert_called_once_with(fixes_handicap=False)

    @patch("game_initialization.initialize_player_choice")
    @patch("game_initialization.ui.setup_board_window_pygame")
    @patch("game_initialization.request_handicap_info", return_value=True)
    def test_initializing_game_not_defaults(self, mock_request_handicap_info, mock_setup_board, mock_initialize_player_choice):
        window_mock = MagicMock()
        board_size = 9

        start.initializing_game(window_mock, board_size, defaults=False)

        mock_initialize_player_choice.assert_called_once_with(board_size, False, False)
        mock_setup_board.assert_called_once_with(mock_initialize_player_choice.return_value)
        mock_request_handicap_info.assert_called_once()
        mock_initialize_player_choice.return_value.play_game.assert_called_once_with(fixes_handicap=True)
