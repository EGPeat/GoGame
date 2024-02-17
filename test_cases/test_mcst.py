from unittest.mock import patch, MagicMock, call
import sys
import pytest
sys.path.append("/users/5/a1895735/Documents/PythonProjects/GoGame/")
import botnormalgo as bot
import config as cf
from saving_loading import load_pkl
import mcst as mcst
import goclasses as go
import scoringboard as sb


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

    def test_play_turn_bot(self):
        the_board: sb.ScoringBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/scoreboardsaved.pkl")
        the_board.__class__ = sb.ScoringBoard
        the_board.ai_training_info = []
        the_board.ai_output_info = []
        the_board.make_turn_info()



    def test_init_collection(self):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/endgame.pkl")
        test_sb = sb.ScoringBoard(the_board)
        test_sb.dead_stones_make_strings()
        test_sb.dead_stones_make_mixed()
        test_sb.remove_safe_strings()
        MCST_collection = mcst.CollectionOfMCST(test_sb.board, test_sb.outer_string_black, test_sb.mixed_string_for_black,
                                                test_sb.outer_string_white, test_sb.mixed_string_for_white,
                                                5000, 30, (test_sb.whose_turn, test_sb.not_whose_turn))
        print(len(MCST_collection.black_MCSTS))
        assert len(MCST_collection.black_MCSTS) == len(MCST_collection.black_MCSTS_tuple_list)
        assert len(MCST_collection.white_MCSTS) == len(MCST_collection.white_MCSTS_tuple_list)

    def test_init_mcst(self):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/endgame.pkl")
        board_string = the_board.make_board_string()
        test_sb = sb.ScoringBoard(the_board)
        test_sb.dead_stones_make_strings()
        test_sb.dead_stones_make_mixed()
        test_sb.remove_safe_strings()
        test_mcst = mcst.MCST(test_sb.board, test_sb.outer_string_black[0], test_sb.mixed_string_for_black[0],
                              5000, 30, (test_sb.whose_turn, test_sb.not_whose_turn))
        test_mcst.print_board()
        mcst_list_string = test_mcst.make_board_string()
        mcst_lstring = ''.join(mcst_list_string)
        assert str(test_sb.outer_string_black[0]) == str(test_mcst.outer)
        assert mcst_lstring == board_string[1:]
        test_mcst.reload_board_string(mcst_list_string)
        mcst_list_string2 = test_mcst.make_board_string()
        assert mcst_list_string == mcst_list_string2
        assert test_mcst.root.player_black == test_mcst.root.not_whose_turn
        test_mcst.root.switch_player()
        assert test_mcst.root.player_white == test_mcst.root.not_whose_turn
        test_mcst.root.switch_player()
        test_mcst2 = mcst.MCST(test_sb.board, test_sb.outer_string_black[0], test_sb.mixed_string_for_black[0],
                               5000, 30, (test_sb.not_whose_turn, test_sb.whose_turn))
        assert test_mcst2.root.player_black == test_mcst2.root.whose_turn
        mcst_list_string2 = test_mcst2.make_board_string()
        test_mcst2.board[0][0].stone_here_color = cf.unicode_black
        mcst_list_string3 = test_mcst2.make_board_string()
        assert mcst_list_string2 != mcst_list_string3
        test_mcst2.load_board_string(test_mcst2.root)
        mcst_list_string4 = test_mcst2.make_board_string()
        assert mcst_list_string4 != mcst_list_string3

    def test_print_board(self):
        from goclasses import BoardNode
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/endgame.pkl")
        test_sb = sb.ScoringBoard(the_board)
        test_sb.dead_stones_make_strings()
        test_sb.dead_stones_make_mixed()
        test_sb.remove_safe_strings()
        test_mcst = mcst.MCST(test_sb.board, test_sb.outer_string_black[0], test_sb.mixed_string_for_black[0],
                              5000, 30, (test_sb.whose_turn, test_sb.not_whose_turn))
        sample_board = [
            [BoardNode(0, 0), BoardNode(1, 0), BoardNode(2, 0)],
            [BoardNode(1, 0), BoardNode(1, 1), BoardNode(2, 1)],
            [BoardNode(2, 0), BoardNode(2, 1), BoardNode(2, 2)]
        ]
        color_setup = [(0, 0), (0, 2), (2, 0), (2, 1), (2, 2)]
        for item in color_setup:
            sample_board[item[0]][item[1]].stone_here_color = cf.unicode_black
        color_setup_two = [(1, 0), (1, 1), (1, 2)]
        for item in color_setup_two:
            sample_board[item[0]][item[1]].stone_here_color = cf.unicode_white
        sample_board[0][1].stone_here_color = cf.unicode_none

        test_mcst.board = sample_board
        with patch('builtins.print') as mock_print:
            test_mcst.print_board()
        expected_output = [
            call('\u26AB⛔\u26AB'),
            call('\u26AA\u26AA\u26AA'),
            call('\u26AB\u26AB\u26AB'),
            call('\n\n')
        ]
        mock_print.assert_has_calls(expected_output)


    # Can easily do some tests for the kill_stones, fills_eyes, and other functions already tested elsewhere

#obj = TestClassPyTestMCST()
#obj.test_play_turn_bot()