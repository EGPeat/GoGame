from unittest.mock import patch, MagicMock
import sys
import pytest
sys.path.append("/users/5/a1895735/Documents/PythonProjects/GoGame/")
import handicap as hand


class TestClassPyTestHandicap:
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
        handicap_instance = hand.Handicap(mock_goboard)
        answer = handicap_instance.handicap_person()
        assert answer == output

    @patch("goclasses.GoBoard")
    def test_custom_handicap_defaults(self, mock_goboard):
        handicap_instance = hand.Handicap(mock_goboard)
        answer = hand.Handicap.custom_handicap(handicap_instance, defaults=True)
        assert answer == (False, "None", 0)

    @patch("handicap.Handicap.choose_handicap_list")
    @patch("goclasses.GoBoard")
    def test_custom_handicap_decided_not(self, mock_goboard, mock_handicap_list, mocker):
        handicap_instance = hand.Handicap(mock_goboard)
        mocker.patch('PySimpleGUI.popup_yes_no', return_value="No")
        mocker.patch('handicap.Handicap.handicap_person', return_value=False)
        answer = hand.Handicap.custom_handicap(handicap_instance, defaults=False)
        assert answer == (False, "None", 0)

    @patch("handicap.Handicap.play_automatic_handicap")
    @patch("handicap.Handicap.choose_handicap_list")
    @patch("goclasses.GoBoard")
    def test_custom_handicap_automatic(self, mock_goboard, mock_handicap_list, mock_auto_handicap, mocker):
        handicap_instance = hand.Handicap(mock_goboard)
        mock_goboard.board_size = 9
        mock_goboard.not_whose_turn.color = "Black"
        mocker.patch('PySimpleGUI.popup_yes_no', return_value="No")
        mocker.patch('handicap.Handicap.handicap_person', return_value=True)
        mocker.patch('uifunctions.handicap_number_gui', return_value=5)
        answer = hand.Handicap.custom_handicap(handicap_instance, defaults=False)
        assert answer == (True, mock_goboard.not_whose_turn.color, 5)

    @patch("handicap.Handicap.manual_handicap_placement")
    @patch("handicap.Handicap.play_automatic_handicap")
    @patch("handicap.Handicap.choose_handicap_list")
    @patch("goclasses.GoBoard")
    def test_custom_handicap_manual(self, mock_goboard, mock_handicap_list, mock_auto_handicap, mock_manual_handicap, mocker):
        handicap_instance = hand.Handicap(mock_goboard)
        mock_goboard.board_size = 9
        mock_goboard.not_whose_turn.color = "Black"
        mocker.patch('PySimpleGUI.popup_yes_no', return_value="Yes")
        mocker.patch('handicap.Handicap.handicap_person', return_value=True)
        mocker.patch('uifunctions.handicap_number_gui', return_value=5)
        answer = hand.Handicap.custom_handicap(handicap_instance, defaults=False)
        assert answer == (True, mock_goboard.not_whose_turn.color, 5)

    @pytest.mark.parametrize("amount", [(1), (2), (3), (4), (5)])
    @patch("pygame.draw.circle")
    @patch("goclasses.GoBoard")
    @patch("goclasses.GoBoard.play_piece")
    @patch("uifunctions.refresh_board_pygame")
    @patch("goclasses.GoBoard.switch_player")
    def test_automatic_placement(self, mock_switch_player, mock_refresh, mock_play_piece, mock_goboard, mock_draw_circle, amount):
        handicap_spots = [(2, 6), (6, 2), (6, 6), (2, 2), (4, 4)]
        mock_goboard.board_size = 9
        mock_goboard.whose_turn.color = "Black"
        mock_goboard.whose_turn.unicode = hand.cf.unicode_black
        handicap_instance = hand.Handicap(mock_goboard)
        handicap_instance.play_automatic_handicap(amount, handicap_spots)
        assert mock_draw_circle.call_count == amount
        for idx in range(amount):
            row = handicap_spots[idx][0]
            col = handicap_spots[idx][1]
            mock_goboard.play_piece.assert_any_call(row, col)
            mock_refresh.assert_called_with(mock_goboard)
            mock_draw_circle.assert_called_with(
                mock_goboard.screen, mock_goboard.whose_turn.unicode,
                (mock_goboard.board[row][col].screen_row, mock_goboard.board[row][col].screen_col),
                mock_goboard.pygame_board_vals[2])

    def test_validate_handicap_placement_valid(self):
        self.go_board = MagicMock()
        self.your_instance = hand.Handicap(self.go_board)
        self.go_board.read_window.return_value = ('some_event', {'-GRAPH-': (2, 3)})
        empty_piece = MagicMock()
        empty_piece.stone_here_color = hand.cf.unicode_none
        self.go_board.find_piece_click.return_value = (True, empty_piece)

        result = self.your_instance.validate_handicap_placement()
        assert result == empty_piece

    @patch("handicap.Handicap.handle_special_events")
    def test_handle_special_events_no_special_event(self, mock_handle_special_events):
        go_board = MagicMock()
        mock_handle_special_events.return_value = "Normal Event"

        result = hand.Handicap(go_board)
        answer = result.handle_special_events("Normal Event")

        assert answer == "Normal Event"

    @patch("goclasses.GoBoard.read_window", side_effect=[('Pass Turn', 4), ('Normal Event', 5)])
    @patch("uifunctions.def_popup")
    def test_handle_special_events_with_special_event(self, ui_popup, mock_read_window):
        self.go_board = MagicMock()
        special_event = "Pass Turn"
        answer = hand.Handicap(self.go_board)
        self.go_board.read_window.side_effect = [('Pass Turn', 4), ('Normal Event', 5)]
        result = answer.handle_special_events(special_event)
        print(f"Values returned by read_window: {mock_read_window.call_args_list}")
        assert result == 'Normal Event'

    @patch("turn_options.normal_turn_options")
    def test_handle_exit_or_resume_exit_game(self, mock_normal_turn_options):
        go_board = MagicMock()
        exit_event = "Exit Game"
        with patch("handicap.Handicap.handle_special_events", return_value=None):
            answer = hand.Handicap(go_board)
            answer.handle_exit_or_resume(exit_event)

        mock_normal_turn_options.assert_called_once_with(go_board, exit_event)

    @pytest.mark.parametrize("handicap_info, times_passed, play_piece_return, expected_calls", [
        (3, 0, True, 3),
        (2, 1, False, 2),
        (4, 0, True, 4),
    ])
    @patch("uifunctions.def_popup")
    @patch("handicap.Handicap.validate_handicap_placement")
    @patch("pygame.display.update")
    @patch("pygame.surface.Surface")
    @patch("pygame.draw.circle")
    def test_manual_handicap_placement(
            self, mock_draw_circle, mock_surface, mock_update, mock_popup, mock_validate_handicap_placement,
            handicap_info, times_passed, play_piece_return, expected_calls
    ):
        mock_piece = MagicMock(
            row=2,
            col=3,
            screen_row=20,
            screen_col=30,
            stone_here_color="SomeColor"
        )
        mock_go_board = MagicMock(
            screen=mock_surface.return_value,
            times_passed=times_passed,
            whose_turn=MagicMock(unicode="SomeUnicode"),
            pygame_board_vals=[700, 620 / 8, 620 / 24],
            play_piece=MagicMock(return_value=play_piece_return),
        )
        mock_validate_handicap_placement.return_value = mock_piece
        handicap_instance = hand.Handicap(mock_go_board)
        handicap_instance.manual_handicap_placement(handicap_info)
        assert mock_go_board.play_piece.call_count == expected_calls
        mock_go_board.switch_player.assert_called_once()
