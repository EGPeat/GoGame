from unittest.mock import patch, MagicMock
import sys
import pytest
sys.path.append("/users/5/a1895735/Documents/PythonProjects/GoGame/")
import botnormalgo as bot
import config as cf
from saving_loading import load_pkl


class TestClassPyTestMCST:

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