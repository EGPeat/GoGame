import sys
sys.path.append("/users/5/a1895735/Documents/PythonProjects/GoGame/")
import config as cf
from saving_loading import load_pkl
import scoringboard as sb
from scoringboard import flood_fill, flood_fill_two_colors
import goclasses as go


class TestClassPyTestScoringBoard:

    def test_init_sb(self):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/startscoring.pkl")
        test_sb = sb.ScoringBoard(the_board)
        assert isinstance(test_sb, sb.ScoringBoard)
        assert isinstance(test_sb.parent, go.GoBoard)
        assert test_sb.parent == the_board
        assert test_sb.player_black == test_sb.parent.player_black

    def test_pieces_into_sets(self):
        the_board: sb.ScoringBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/startscoring.pkl")
        the_board.__class__ = sb.ScoringBoard
        the_board.pieces_into_sets()
        assert len(the_board.white_set) == 16
        assert len(the_board.black_set) == 12
        assert len(the_board.empty_space_set) == 53
        assert the_board.board[8][0] in the_board.black_set
        assert the_board.board[7][2] in the_board.empty_space_set
        assert the_board.board[8][8] in the_board.white_set

    def test_making_go_board_strings(self):
        the_board: sb.ScoringBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/startscoring.pkl")
        the_board.__class__ = sb.ScoringBoard
        the_board.pieces_into_sets()
        the_board.making_go_board_strings(the_board.black_set, cf.rgb_black, False)
        the_board.making_go_board_strings(the_board.white_set, cf.rgb_white, False)
        the_board.making_go_board_strings(the_board.empty_space_set, cf.rgb_grey, False)

        assert str(the_board.black_strings[0]) == "this is a board string of color (0, 0, 0) and with len of 12 and values [(5, 0), (5, 1), (6, 0), (6, 2), (6, 3), (7, 0), (7, 1), (7, 3), (8, 0), (8, 1), (8, 2), (8, 3)]\
             and a xmin and xmax of (5, 8), and a ymin and ymax of (0, 3)"
        assert len(the_board.black_strings) == 1
        assert len(the_board.white_strings) == 2
        assert len(the_board.empty_strings) == 3
        empty_list_output = [
            "this is a board string of color (120, 120, 120) and with len of 1 and values [(6, 1)]\
             and a xmin and xmax of (6, 6), and a ymin and ymax of (1, 1)",
            "this is a board string of color (120, 120, 120) and with len of 1 and values [(7, 2)]\
             and a xmin and xmax of (7, 7), and a ymin and ymax of (2, 2)"]
        white_list_output = [
            "this is a board string of color (255, 255, 255) and with len of 9 and values [(4, 0), (4, 1), (4, 2), (5, 2), (5, 3), (5, 4), (6, 4), (7, 4), (8, 4)]\
             and a xmin and xmax of (4, 8), and a ymin and ymax of (0, 4)",
            "this is a board string of color (255, 255, 255) and with len of 7 and values [(6, 6), (7, 6), (7, 7), (7, 8), (8, 6), (8, 7), (8, 8)]\
             and a xmin and xmax of (6, 8), and a ymin and ymax of (6, 8)"]
        for idx in range(len(the_board.empty_strings)):
            item = the_board.empty_strings[idx]
            if len(item.member_set) == 51:
                the_board.empty_strings.pop(idx)
                break
        assert str(the_board.empty_strings[0]) in empty_list_output
        if str(the_board.empty_strings[0]) == empty_list_output[0]:
            empty_list_output.pop(0)
        else:
            empty_list_output.pop(1)
        assert str(the_board.empty_strings[1]) in empty_list_output
        assert str(the_board.white_strings[0]) in white_list_output
        if str(the_board.white_strings[0]) == white_list_output[0]:
            white_list_output.pop(0)
        else:
            white_list_output.pop(1)
        assert str(the_board.white_strings[1]) in white_list_output

    def test_flood_fill_two(self):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/endgame.pkl")
        test_sb = sb.ScoringBoard(the_board)
        piece = test_sb.board[8][8]
        string_good = "this is a board string of color Mixed and with len of 4 and values [(7, 7), (7, 8), (8, 7), (8, 8)]\
             and a xmin and xmax of (7, 8), and a ymin and ymax of (7, 8)"
        string_bad = "this is a board string of color Mixed and with len of 2 and values [(7, 8), (8, 8)]\
             and a xmin and xmax of (7, 8), and a ymin and ymax of (8, 8)"
        string_weird = "this is a board string of color Mixed and with len of 3 and values [(7, 8), (8, 7), (8, 8)]\
             and a xmin and xmax of (7, 8), and a ymin and ymax of (7, 8)"
        piece_flood = flood_fill_two_colors(piece, cf.rgb_grey)
        piece_string = go.BoardString("Mixed", piece_flood[0])
        assert str(piece_string) == string_bad
        piece_flood = flood_fill_two_colors(piece, cf.rgb_black)
        piece_string = go.BoardString("Mixed", piece_flood[0])
        assert str(piece_string) == string_good
        piece = test_sb.board[8][7]
        piece_flood = flood_fill_two_colors(piece, cf.rgb_black)
        piece_string = go.BoardString("Mixed", piece_flood[0])
        assert str(piece_string) == string_good
        piece_flood = flood_fill_two_colors(piece, cf.rgb_grey)
        piece_string = go.BoardString("Mixed", piece_flood[0])
        assert str(piece_string) == string_weird
        # The string_weird is due to if neighbor.stone_here_color == cf.unicode_none
        # and elif neighbor.stone_here_color == second_color
        # So the flood_fill accepts the original piece, but then only accepts unicode_none, thus leaving out (7, 7)

    def test_flood_fill_startscoring(self):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/startscoring.pkl")
        test_sb = sb.ScoringBoard(the_board)
        piece = test_sb.board[8][6]
        string_good = "this is a board string of color White and with len of 7 and values [(6, 6), (7, 6), (7, 7), (7, 8), (8, 6), (8, 7), (8, 8)]\
             and a xmin and xmax of (6, 8), and a ymin and ymax of (6, 8)"

        piece_flood = flood_fill(piece)
        piece_string = go.BoardString("White", piece_flood[0])
        assert str(piece_string) == string_good

    def test_flood_fill_endgame(self):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/endgame.pkl")
        test_sb = sb.ScoringBoard(the_board)
        piece = test_sb.board[2][8]
        string_good = "this is a board string of color White and with len of 2 and values [(1, 8), (2, 8)]\
             and a xmin and xmax of (1, 2), and a ymin and ymax of (8, 8)"

        piece_flood = flood_fill(piece)
        piece_string = go.BoardString("White", piece_flood[0])
        assert str(piece_string) == string_good

    def test_flood_fill_outer(self):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/endgame.pkl")
        test_sb = sb.ScoringBoard(the_board)
        piece = test_sb.board[8][8]
        piece_outer = test_sb.board[8][6]
        piece_flood_outer = flood_fill(piece_outer)
        piece_outer_string = go.BoardString("Outer", piece_flood_outer[0])
        string_good = "this is a board string of color White and with len of 4 and values [(7, 7), (7, 8), (8, 7), (8, 8)]\
             and a xmin and xmax of (7, 8), and a ymin and ymax of (7, 8)"
        string_outer = "this is a board string of color Outer and with len of 8 and values [(6, 7), (6, 8), (7, 6), (7, 7), (7, 8), (8, 6), (8, 7), (8, 8)]\
             and a xmin and xmax of (6, 8), and a ymin and ymax of (6, 8)"
        piece_flood = test_sb.flood_fill_with_outer(piece, piece_outer_string)
        piece_string = go.BoardString("White", piece_flood[0])
        piece_outer_string_two = go.BoardString("Outer", piece_flood[1])
        assert str(piece_string) == string_good
        assert str(piece_outer_string_two) == string_outer

    def test_find_neighbor_get_string_helper_startscoring(self):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/startscoring.pkl")
        test_sb = sb.ScoringBoard(the_board)
        test_sb.pieces_into_sets()
        test_sb.making_go_board_strings(test_sb.black_set, cf.rgb_black, False)
        test_sb.making_go_board_strings(test_sb.white_set, cf.rgb_white, False)
        test_sb.making_go_board_strings(test_sb.empty_space_set, cf.rgb_grey, False)
        piece = test_sb.board[6][1]
        neighbor = test_sb.board[6][2]
        output = test_sb.find_neighbor_get_string_helper(piece, neighbor, cf.rgb_white, test_sb.black_strings)
        assert output[0] is True
        assert str(output[1]) == "this is a board string of color (0, 0, 0) and with len of 12 and values [(5, 0), (5, 1), (6, 0), (6, 2), (6, 3), (7, 0), (7, 1), (7, 3), (8, 0), (8, 1), (8, 2), (8, 3)]\
             and a xmin and xmax of (5, 8), and a ymin and ymax of (0, 3)"
        piece = test_sb.board[5][0]
        neighbor = test_sb.board[4][0]
        output = test_sb.find_neighbor_get_string_helper(piece, neighbor, cf.rgb_black, test_sb.white_strings)
        assert output[0] is True
        assert str(output[1]) == "this is a board string of color (255, 255, 255) and with len of 9 and values [(4, 0), (4, 1), (4, 2), (5, 2), (5, 3), (5, 4), (6, 4), (7, 4), (8, 4)]\
             and a xmin and xmax of (4, 8), and a ymin and ymax of (0, 4)"
        piece = test_sb.board[0][3]
        neighbor = test_sb.board[0][4]
        output = test_sb.find_neighbor_get_string_helper(piece, neighbor, cf.rgb_black, test_sb.white_strings)
        assert output[0] is False
        assert str(output[1]) == "-1"

    def test_find_neighbor_get_string_helper_endgame(self):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/endgame.pkl")
        test_sb = sb.ScoringBoard(the_board)
        test_sb.pieces_into_sets()
        test_sb.making_go_board_strings(test_sb.black_set, cf.rgb_black, False)
        test_sb.making_go_board_strings(test_sb.white_set, cf.rgb_white, False)
        test_sb.making_go_board_strings(test_sb.empty_space_set, cf.rgb_grey, False)
        piece = test_sb.board[0][6]
        neighbor = test_sb.board[1][6]
        output = test_sb.find_neighbor_get_string_helper(piece, neighbor, cf.rgb_white, test_sb.black_strings)
        assert output[0] is True
        assert str(output[1]) == "this is a board string of color (0, 0, 0) and with len of 10 and values [(0, 5), (1, 5), (1, 6), (1, 7), (2, 6), (3, 6), (3, 7), (4, 7), (4, 8), (5, 8)]\
             and a xmin and xmax of (0, 5), and a ymin and ymax of (5, 8)"
        piece = test_sb.board[1][1]
        neighbor = test_sb.board[1][0]
        output = test_sb.find_neighbor_get_string_helper(piece, neighbor, cf.rgb_white, test_sb.black_strings)
        assert output[0] is False
        assert str(output[1]) == "-1"
        piece = test_sb.board[0][8]
        neighbor = test_sb.board[1][8]
        output = test_sb.find_neighbor_get_string_helper(piece, neighbor, cf.rgb_black, test_sb.white_strings)
        assert output[0] is True
        assert str(output[1]) == "this is a board string of color (255, 255, 255) and with len of 3 and values [(0, 7), (1, 8), (2, 8)]\
             and a xmin and xmax of (0, 2), and a ymin and ymax of (7, 8)"
        piece = test_sb.board[1][8]
        neighbor = test_sb.board[1][7]
        output = test_sb.find_neighbor_get_string_helper(piece, neighbor, cf.rgb_white, test_sb.black_strings)
        assert output[0] is True
        assert str(output[1]) == "this is a board string of color (0, 0, 0) and with len of 10 and values [(0, 5), (1, 5), (1, 6), (1, 7), (2, 6), (3, 6), (3, 7), (4, 7), (4, 8), (5, 8)]\
             and a xmin and xmax of (0, 5), and a ymin and ymax of (5, 8)"

    def test_find_neighbor_get_string_startscoring(self):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/startscoring.pkl")
        test_sb = sb.ScoringBoard(the_board)
        test_sb.pieces_into_sets()
        test_sb.making_go_board_strings(test_sb.black_set, cf.rgb_black, False)
        test_sb.making_go_board_strings(test_sb.white_set, cf.rgb_white, False)
        test_sb.making_go_board_strings(test_sb.empty_space_set, cf.rgb_grey, False)
        piece = test_sb.board[6][1]
        output = test_sb.find_neighbor_get_string(piece, cf.rgb_black)
        assert output[0] is True
        assert str(output[1]) == "this is a board string of color (0, 0, 0) and with len of 12 and values [(5, 0), (5, 1), (6, 0), (6, 2), (6, 3), (7, 0), (7, 1), (7, 3), (8, 0), (8, 1), (8, 2), (8, 3)]\
             and a xmin and xmax of (5, 8), and a ymin and ymax of (0, 3)"
        piece = test_sb.board[6][1]
        output = test_sb.find_neighbor_get_string(piece, cf.rgb_white)
        assert output[0] is True
        assert str(output[1]) == "this is a board string of color (255, 255, 255) and with len of 9 and values [(4, 0), (4, 1), (4, 2), (5, 2), (5, 3), (5, 4), (6, 4), (7, 4), (8, 4)]\
             and a xmin and xmax of (4, 8), and a ymin and ymax of (0, 4)"
        piece = test_sb.board[0][0]
        output = test_sb.find_neighbor_get_string(piece, cf.rgb_white)
        assert output[0] is False
        assert str(output[1]) == "-1"

    def test_find_neighbor_get_string_endgame(self):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/endgame.pkl")
        test_sb = sb.ScoringBoard(the_board)
        test_sb.pieces_into_sets()
        test_sb.making_go_board_strings(test_sb.black_set, cf.rgb_black, False)
        test_sb.making_go_board_strings(test_sb.white_set, cf.rgb_white, False)
        test_sb.making_go_board_strings(test_sb.empty_space_set, cf.rgb_grey, False)
        piece = test_sb.board[0][6]
        output = test_sb.find_neighbor_get_string(piece, cf.rgb_black)
        assert output[0] is True
        assert str(output[1]) == "this is a board string of color (0, 0, 0) and with len of 10 and values [(0, 5), (1, 5), (1, 6), (1, 7), (2, 6), (3, 6), (3, 7), (4, 7), (4, 8), (5, 8)]\
             and a xmin and xmax of (0, 5), and a ymin and ymax of (5, 8)"
        piece = test_sb.board[0][0]
        output = test_sb.find_neighbor_get_string(piece, cf.rgb_black)
        assert output[0] is False
        assert str(output[1]) == "-1"
        piece = test_sb.board[0][8]
        output = test_sb.find_neighbor_get_string(piece, cf.rgb_white)
        assert output[0] is True
        assert str(output[1]) == "this is a board string of color (255, 255, 255) and with len of 3 and values [(0, 7), (1, 8), (2, 8)]\
             and a xmin and xmax of (0, 2), and a ymin and ymax of (7, 8)"
        piece = test_sb.board[0][8]
        output = test_sb.find_neighbor_get_string(piece, cf.rgb_black)
        assert output[0] is True
        assert str(output[1]) == "this is a board string of color (0, 0, 0) and with len of 10 and values [(0, 5), (1, 5), (1, 6), (1, 7), (2, 6), (3, 6), (3, 7), (4, 7), (4, 8), (5, 8)]\
             and a xmin and xmax of (0, 5), and a ymin and ymax of (5, 8)"

    def test_dealing_with_dead_stones_startscoring(self):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/startscoring.pkl")
        test_sb = sb.ScoringBoard(the_board)
        test_sb.dead_stones_make_strings()
        test_sb.dead_stones_make_mixed()
        test_sb.remove_safe_strings()
        assert len(test_sb.outer_string_white[0].member_set) == 9
        assert len(test_sb.mixed_string_for_white[0].member_set) == 14

    def test_dealing_with_dead_stones_fullgame(self):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/fullgame.pkl")
        test_sb = sb.ScoringBoard(the_board)
        test_sb.dead_stones_make_strings()
        locations = [(0, 6), (1, 6), (3, 6), (3, 5), (0, 10)]
        piece = test_sb.board[0][10]
        sucesss, original_string = test_sb.find_neighbor_get_string(piece, cf.rgb_black)
        for item in locations:
            piece = test_sb.board[item[0]][item[1]]
            sucesss, original_string = test_sb.find_neighbor_get_string(piece, cf.rgb_black)
            assert sucesss is True
            truth, connected, disconn = test_sb.finding_correct_mixed_string(piece, cf.rgb_black, original_string,
                                                                             test_sb.black_strings)
            assert test_sb.board[3][5] in connected.member_set
            assert truth is True
            assert len(connected.member_set) == 26
            assert len(disconn.member_set) == 94

        locations = [(0, 17), (0, 18), (1, 17), (1, 18), (2, 17), (2, 18), (3, 17), (3, 18), (4, 16), (6, 14), (1, 14), (0, 15)]
        for item in locations:
            piece = test_sb.board[item[0]][item[1]]
            sucesss, original_string = test_sb.find_neighbor_get_string(piece, cf.rgb_black)
            assert sucesss is True
            truth, connected, disconn = test_sb.finding_correct_mixed_string(piece, cf.rgb_black,
                                                                             original_string, test_sb.black_strings)
            assert test_sb.board[2][15] in connected.member_set
            assert truth is True
            assert len(connected.member_set) == 43
            assert len(disconn.member_set) == 94

        piece = test_sb.board[10][18]
        sucesss, original_string = test_sb.find_neighbor_get_string(piece, cf.rgb_black)
        assert sucesss is True
        truth, connected, disconn = test_sb.finding_correct_mixed_string(piece, cf.rgb_black, original_string,
                                                                         test_sb.black_strings)
        assert truth is True
        assert len(connected.member_set) == 30
        assert len(disconn.member_set) == 94

    def test_counting_territory_fullgame(self):
        the_board: go.GoBoard = load_pkl(
            "/users/5/a1895735/Documents/PythonProjects/GoGame/test_cases/pklfilestesting/fullgamechinese.pkl")
        test_sb = sb.ScoringBoard(the_board)
        test_sb.counting_territory()
        pb = test_sb.player_black
        pw = test_sb.player_white
        pb.black_set_len = len(test_sb.black_set)
        pw.white_set_len = len(test_sb.white_set)
        player_black_score = pb.komi + pb.territory + len(test_sb.black_set)
        player_white_score = pw.komi + pw.territory + len(test_sb.white_set)
        difference = player_black_score - player_white_score
        assert difference == -3.5
