from unittest.mock import patch
import sys
import pytest
sys.path.append("/users/5/a1895735/Documents/PythonProjects/GoGame/")
import uifunctions as ui


class TestClassPyTestUI:
    @pytest.fixture
    def mock_window(self):
        with patch('PySimpleGUI.Window', autospec=True) as mock:
            yield mock.return_value

    @patch('PySimpleGUI.Window.read', return_value=('9x9', {}))
    def test_start_game_9x9(self, _):
        result = ui.start_game()
        assert result == 9

    @patch('PySimpleGUI.Window.read', return_value=('13x13', {}))
    def test_start_game_13x13(self, _):
        result = ui.start_game()
        assert result == 13

    @patch('PySimpleGUI.Window.read', return_value=('19x19', {}))
    def test_start_game_19x19(self, _):
        result = ui.start_game()
        assert result == 19

    @patch('PySimpleGUI.Window.read', return_value=('Black', {}))
    def test_handicap_person_gui_black(self, _):
        result = ui.handicap_person_gui()
        assert result == 'Black'

    @patch('PySimpleGUI.Window.read', return_value=('White', {}))
    def test_handicap_person_gui_white(self, _):
        result = ui.handicap_person_gui()
        assert result == 'White'

    @patch('PySimpleGUI.Window.read', return_value=("I don't want a handicap", {}))
    def test_handicap_person_gui_no_handicap(self, _):
        result = ui.handicap_person_gui()
        assert result == "I don't want a handicap"
