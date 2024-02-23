from unittest.mock import patch
import GoGame.config as cf
import GoGame.goclasses as go
import GoGame.undoing as undo
from GoGame.saving_loading import load_pkl


class TestClassPyTestUndoing:

    def test_move_back(self):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/unittest_undo_kill_log.pkl")
        undo.move_back(the_board)
        assert len(the_board.killed_log) == 3
        assert len(the_board.killed_log[-1]) == 1
        assert len(the_board.killed_last_turn) == 0
        undo.move_back(the_board)
        tmp_node: go.BoardNode = the_board.killed_last_turn.pop()
        assert tmp_node.row == 0
        assert tmp_node.col == 0
        assert the_board.turn_num == 4

    @patch("GoGame.uifunctions.refresh_board_pygame")
    @patch("GoGame.undoing.undo_special_cases", return_value=False)
    def test_undo_turn(self, mock_refresh, mock_special):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/unittest_undo_kill_log.pkl")
        assert the_board.board[1][1].stone_here_color == cf.rgb_white
        assert the_board.whose_turn == the_board.player_black
        assert the_board.turn_num == 4
        undo.undo_checker(the_board)
        assert the_board.board[1][1].stone_here_color == cf.rgb_grey
        assert the_board.whose_turn == the_board.player_white
        assert the_board.turn_num == 3
        undo.undo_checker(the_board)
        assert the_board.board[0][0].stone_here_color == cf.rgb_white

    @patch("GoGame.uifunctions.refresh_board_pygame")
    @patch("GoGame.undoing.undo_special_cases", return_value=False)
    def test_undo_turn_scoring(self, mock_refresh, mock_special):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/unittest_undo_kill_log.pkl")
        the_board.mode = "Scoring"
        assert the_board.board[1][1].stone_here_color == cf.rgb_white
        assert the_board.whose_turn == the_board.player_black
        assert the_board.turn_num == 4
        undo.undo_checker(the_board)
        assert the_board.board[1][1].stone_here_color == cf.rgb_white
        assert the_board.whose_turn == the_board.player_white
        assert the_board.turn_num == 3

    @patch("GoGame.uifunctions.refresh_board_pygame")
    def test_undo_special_conditions(self, mock_refresh):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/test_undo.pkl")
        for _ in range(9):
            undo.undo_checker(the_board)
