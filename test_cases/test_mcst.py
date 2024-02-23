from unittest.mock import patch, call
import GoGame.config as cf
from GoGame.saving_loading import load_pkl
import GoGame.mcst as mcst
import GoGame.goclasses as go
import GoGame.scoringboard as sb
import random


class TestClassPyTestMCST:

    def setup_board(self, times=100):
        the_board: go.GoBoard = load_pkl(
            "test_cases/pklfilestesting/endgame.pkl")
        test_sb = sb.ScoringBoard(the_board)
        test_sb.dead_stones_make_strings()
        test_sb.dead_stones_make_mixed()
        test_sb.remove_safe_strings()
        random.seed(13092000)
        test_mcst = mcst.MCST(test_sb.board, test_sb.outer_string_black[0], test_sb.mixed_string_for_black[0],
                              times, 30, (test_sb.whose_turn, test_sb.not_whose_turn))
        return the_board, test_sb, test_mcst

    def test_init_collection(self):
        the_board: go.GoBoard = load_pkl(
            "test_cases/pklfilestesting/endgame.pkl")
        test_sb = sb.ScoringBoard(the_board)
        test_sb.dead_stones_make_strings()
        test_sb.dead_stones_make_mixed()
        test_sb.remove_safe_strings()
        MCST_collection = mcst.CollectionOfMCST(test_sb.board, test_sb.outer_string_black, test_sb.mixed_string_for_black,
                                                test_sb.outer_string_white, test_sb.mixed_string_for_white,
                                                100, 30, (test_sb.whose_turn, test_sb.not_whose_turn))
        assert len(MCST_collection.black_MCSTS) == len(MCST_collection.black_MCSTS_tuple_list)
        assert len(MCST_collection.white_MCSTS) == len(MCST_collection.white_MCSTS_tuple_list)

    def test_init_mcst(self):
        the_board, test_sb, test_mcst = self.setup_board()
        board_string = the_board.make_board_string()
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
        test_mcst2.board[0][0].stone_here_color = cf.rgb_black
        mcst_list_string3 = test_mcst2.make_board_string()
        assert mcst_list_string2 != mcst_list_string3
        test_mcst2.load_board_string(test_mcst2.root)
        mcst_list_string4 = test_mcst2.make_board_string()
        assert mcst_list_string4 != mcst_list_string3

    def test_print_board(self):
        from GoGame.goclasses import BoardNode
        the_board, _, test_mcst = self.setup_board()
        sample_board = [
            [BoardNode(0, 0), BoardNode(1, 0), BoardNode(2, 0)],
            [BoardNode(1, 0), BoardNode(1, 1), BoardNode(2, 1)],
            [BoardNode(2, 0), BoardNode(2, 1), BoardNode(2, 2)]
        ]
        color_setup = [(0, 0), (0, 2), (2, 0), (2, 1), (2, 2)]
        for item in color_setup:
            sample_board[item[0]][item[1]].stone_here_color = cf.rgb_black
        color_setup_two = [(1, 0), (1, 1), (1, 2)]
        for item in color_setup_two:
            sample_board[item[0]][item[1]].stone_here_color = cf.rgb_white
        sample_board[0][1].stone_here_color = cf.rgb_grey

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

    def test_playing_turn(self):
        _, test_sb, test_mcst = self.setup_board()
        spot_list = [(0, 6), (0, 7), (0, 8), (1, 8), (2, 7), (2, 8), (3, 8)]
        outcome_list = [True, False, False, False, True, False, True]
        for spot, outcome in zip(spot_list, outcome_list):
            board_node = test_mcst.board[spot[0]][spot[1]]
            output = test_mcst.test_piece_placement(board_node, test_mcst.root, False, False)
            assert output is outcome

    def test_generate_moves_children(self):
        the_board, test_sb, test_mcst = self.setup_board()
        node = test_mcst.root
        assert not node.children
        if not node.children:
            test_mcst.load_board_string(node)
            legal_moves = test_mcst.generate_moves(node)
            for move in legal_moves:
                test_mcst.generate_child(move, node, 0)
        assert len(node.children) == 4
        for child in node.children:
            assert child.whose_turn == node.not_whose_turn

    def test_select(self):
        _, test_sb, test_mcst = self.setup_board()
        test_mcst.select(test_mcst.root, 0)
        chosen_one_pass = test_mcst.select(test_mcst.root, 1)
        assert chosen_one_pass in test_mcst.root.children
        assert len(chosen_one_pass.children) == 4
        for child in chosen_one_pass.children:
            assert child.whose_turn == chosen_one_pass.not_whose_turn
        chosen_two = test_mcst.select(test_mcst.root, 2)
        assert chosen_two in chosen_one_pass.children
        assert len(chosen_two.children) == 3
        for child in chosen_two.children:
            assert child.whose_turn == chosen_two.not_whose_turn

    def test_expand(self):
        _, test_sb, test_mcst = self.setup_board()
        chose_root = test_mcst.select(test_mcst.root, 0)
        test_mcst.expand(chose_root, 0)
        chose_child = test_mcst.select(test_mcst.root, 1)
        test_mcst.expand(chose_child, 1)
        for child in test_mcst.root.children:
            if child.children:
                assert child == test_mcst.root.move_choices['Pass']
                assert len(child.children) == 4

    def test_simulate_full(self):
        _, test_sb, test_mcst = self.setup_board()
        node = test_mcst.select(test_mcst.root, 0)
        test_mcst.expand(node, 0)
        random.seed(777)
        result: int = test_mcst.simulate(node)
        assert result == 0

    def test_eye_alive(self):
        _, test_sb, test_mcst = self.setup_board()
        for item in test_sb.mixed_string_for_white:
            if len(item.member_set) == 17:
                mixed_str = item
        test_mcst = mcst.MCST(test_sb.board, test_sb.outer_string_white[0], mixed_str,
                              100, 30, (test_sb.whose_turn, test_sb.not_whose_turn))
        node = test_mcst.select(test_mcst.root, 0)
        test_mcst.expand(node, 0)
        test_mcst.board[1][8].stone_here_color = cf.rgb_black
        life_check = test_mcst.check_inner_life()
        assert life_check is True

    def test_run_mcst(self):
        random.seed(777)
        _, test_sb, test_mcst = self.setup_board(500)
        winner = test_mcst.run_mcst()
        assert winner == 0

    def test_total_setup(self):
        the_board: go.GoBoard = load_pkl(
            "test_cases/pklfilestesting/endgame.pkl")
        test_sb = sb.ScoringBoard(the_board)
        test_sb.dead_stones_make_strings()
        test_sb.dead_stones_make_mixed()
        test_sb.remove_safe_strings()
        MCST_collection = mcst.CollectionOfMCST(test_sb.board, test_sb.outer_string_black, test_sb.mixed_string_for_black,
                                                test_sb.outer_string_white, test_sb.mixed_string_for_white,
                                                100, 30, (test_sb.whose_turn, test_sb.not_whose_turn))
        random.seed(777)
        MCST_collection.running_tests()
        black_total = 0
        white_total = 0
        for item in MCST_collection.black_MCSTS_final:
            if item[3] is True:
                black_total += 1
        for item in MCST_collection.white_MCSTS_final:
            if item[3] is True:
                white_total += 1
        assert white_total == 3
        assert black_total == 0
