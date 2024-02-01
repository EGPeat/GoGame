from unittest.mock import patch
import sys
import pytest
sys.path.append("/users/5/a1895735/Documents/PythonProjects/GoGame/")
import handicap as hand


class TestClassPyTestGameInit:
    @pytest.mark.parametrize("size, output", [(9, [(2, 6), (6, 2), (6, 6), (2, 2), (4, 4)]),
                                              (13, [(3, 9), (9, 3), (9, 9), (3, 3), (6, 6), (6, 3), (6, 9), (3, 6), (9, 6)]),
                                              (19, [(3, 13), (13, 3), (13, 13), (3, 3), (8, 8), (8, 3), (8, 13), (3, 8), (13, 8)])
                                              ])
    @patch("goclasses.GoBoard")
    def test_choose_handicap_list(self, mock_goboard, size, output):
        mock_goboard.board_size = size
        handicap_instance = hand.Handicap(mock_goboard)
        answer = handicap_instance.choose_handicap_list()
        assert answer == output

    @pytest.mark.parametrize("person, output", [("Black", True), ("White", True), ("I don't want a handicap", False)])
    @patch("goclasses.GoBoard")
    def test_handicap_person(self, mock_goboard, mocker, person, output):
        mocker.patch("uifunctions.handicap_person_gui", return_value=(person))
        # mocker.patch('PySimpleGUI.Window.read', return_value=(person, {}))
        handicap_instance = hand.Handicap(mock_goboard)
        answer = handicap_instance.handicap_person()
        assert answer == output
