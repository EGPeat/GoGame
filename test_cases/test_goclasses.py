from unittest.mock import patch, MagicMock
import unittest
import sys
import pytest
sys.path.append("/users/5/a1895735/Documents/PythonProjects/GoGame/")
import uifunctions as ui
import PySimpleGUI as sg
import goclasses as go
import pygame
from player import Player


class TestClassPyTestGoClasses:

    @pytest.fixture
    def mock_window(self):
        with patch('PySimpleGUI.Window', autospec=True) as mock:
            yield mock.return_value

    def test_read_window(self, mock_window):
        instance_under_test = go.GoBoard()
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
        mock_goboard.player_black: Player = Player.setup_player(True, "Player One", "Black", go.cf.unicode_black)
        mock_goboard.player_white: Player = Player.setup_player(True, "Player Two", "White", go.cf.unicode_white)
        mock_goboard.whose_turn = mock_goboard.player_black
        mock_goboard.not_whose_turn = mock_goboard.player_white
        go.GoBoard.switch_player(mock_goboard)
        assert mock_goboard.not_whose_turn == mock_goboard.player_black
        assert mock_goboard.whose_turn == mock_goboard.player_white
