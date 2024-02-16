from unittest.mock import patch, MagicMock, call
import sys
import pytest
sys.path.append("/users/5/a1895735/Documents/PythonProjects/GoGame/")
import botnormalgo as bot
import config as cf
from saving_loading import load_pkl
import mcst as mcst
import scoringboard as sb


class TestClassPyTestMCST:
    def __init__(self) -> None:
        pass

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

    def test_play_turn_bot(self):
        the_board: sb.ScoringBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/scoreboardsaved.pkl")
        the_board.__class__ = sb.ScoringBoard
        print("bruh")

        print("bruh")
        the_board.ai_training_info = []
        the_board.ai_output_info = []
        the_board.make_turn_info()


    # Can easily do some tests for the kill_stones, fills_eyes, and other functions already tested elsewhere

#obj = TestClassPyTestMCST()
#obj.test_play_turn_bot()