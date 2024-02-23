from unittest.mock import patch, MagicMock
import pytest
import GoGame.uifunctions as ui
import GoGame.config as cf
import PySimpleGUI as sg
import GoGame.goclasses as go
import pygame
import os


class TestClassPyTestUI:
    @pytest.fixture
    def mock_window(self):
        with patch('PySimpleGUI.Window', autospec=True) as mock:
            yield mock.return_value

    @pytest.fixture
    def setup_game_fixture(self):
        game = go.GoBoard()
        game.whose_turn = MagicMock(color='Black')
        game.turn_num = 5
        game.player_black = MagicMock(name='Player1', color='Black', komi=6.5)
        game.player_white = MagicMock(name='Player2', color='White', komi=6.5)
        game.window = MagicMock()
        return game

    @patch('PySimpleGUI.Window.read', return_value=('9x9', {}))
    def test_start_game_9x9(self, _):
        if os.getenv("DISPLAY") is not None:
            result = ui.start_game()
            assert result == 9
        else:
            pass

    @patch('PySimpleGUI.Window.read', return_value=('13x13', {}))
    def test_start_game_13x13(self, _):
        if os.getenv("DISPLAY") is not None:
            result = ui.start_game()
            assert result == 13

    @patch('PySimpleGUI.Window.read', return_value=('19x19', {}))
    def test_start_game_19x19(self, _):
        if os.getenv("DISPLAY") is not None:
            result = ui.start_game()
            assert result == 19

    @patch('PySimpleGUI.Window.read', return_value=('Black', {}))
    def test_handicap_person_gui_black(self, _):
        if os.getenv("DISPLAY") is not None:
            result = ui.handicap_person_gui()
            assert result == 'Black'

    @patch('PySimpleGUI.Window.read', return_value=('White', {}))
    def test_handicap_person_gui_white(self, _):
        if os.getenv("DISPLAY") is not None:
            result = ui.handicap_person_gui()
            assert result == 'White'

    @patch('PySimpleGUI.Window.read', return_value=("I don't want a handicap", {}))
    def test_handicap_person_gui_no_handicap(self, _):
        if os.getenv("DISPLAY") is not None:
            result = ui.handicap_person_gui()
            assert result == "I don't want a handicap"

    def test_setup_menu(self):
        if os.getenv("DISPLAY") is not None:
            window = ui.setup_menu()
            text = "The default settings are a 9x9 board, 7.5 komi, and names for players of Player 1 and Player 2"
            assert window["Info"].get() == text
            window.close()

    @patch("GoGame.goclasses.GoBoard")
    @patch("platform.system")
    def test_setup_board_window_pygame_linux(self, mock_sys, mock_board):
        if os.getenv("DISPLAY") is not None:
            mock_sys.return_value = 'Linux'
            answer = ui.setup_board_window_pygame(mock_board)
            assert isinstance(answer, sg.Window)

    @patch('PySimpleGUI.popup')
    def test_scoring_mode_popup(self, mock_popup):
        ui.scoring_mode_popup()
        expected_info = "Please take turns clicking on stones that you believe are dead, and then the program will score.\
        \n Please pass twice once you are finished scoring."
        mock_popup.assert_called_once_with(expected_info, title="Scoring", line_width=200, auto_close=True, auto_close_duration=3)

    def test_update_scoring(self, setup_game_fixture):
        game = setup_game_fixture
        game.player_black.komi = 6.5
        game.player_white.komi = 6.5
        game.player_black.name = "Player1"
        game.player_white.name = "Player2"
        game.player_black.territory = 20
        game.player_white.territory = 15
        ui.update_scoring(game)
        assert game.window['Scoring'].update.called
        assert 'It is currently Black\'s turn.' in game.window['Scoring'].update.call_args[0][0]

    @patch("PySimpleGUI.popup_no_buttons")
    def test_default_popup_no_button(self, mock_popup_no_buttons):
        ui.default_popup_no_button("Some information", 10)

        mock_popup_no_buttons.assert_called_with(
            "Some information",
            non_blocking=True,
            font=('Arial Bold', 15),
            auto_close=True,
            auto_close_duration=10
        )

    @patch("PySimpleGUI.popup")
    def test_def_popup(self, mock_popup):
        ui.def_popup("Some information", 15)

        mock_popup.assert_called_with(
            "Some information",
            line_width=42,
            auto_close=True,
            auto_close_duration=15
        )

    @patch("PySimpleGUI.popup")
    def test_end_game_popup_winner(self, mock_popup):
        game = MagicMock()
        game.player_black.name = "Player1"
        game.player_white.name = "Player2"
        game.player_black.komi = 6.5
        game.player_white.komi = 6.5
        game.player_black.territory = 20
        game.player_white.territory = 15
        game.player_black.black_set_len = 0
        game.player_white.white_set_len = 0

        ui.end_game_popup(game)

        mock_popup.assert_called_with(
            "Your game has finished.\nPlayer Black: Player1 has 20 territory\
            , and played 0 pieces and has a komi of 6.5\
            \n Player White: Player2 has 15 territory, and played 0 pieces\
              and has a komi of 6.5\n Player Black has a score of 26.5\n\
            Player White has a score of 21.5, meaning Player Black won by 5.0 points",
            title="Game has Concluded",
            line_width=200,
            auto_close=True,
            auto_close_duration=20
        )

    @patch("PySimpleGUI.popup")
    def test_end_game_popup_loser(self, mock_popup):
        game = MagicMock()
        game.player_black.name = "Player1"
        game.player_white.name = "Player2"
        game.player_black.komi = 6.5
        game.player_white.komi = 6.5
        game.player_black.territory = 15
        game.player_white.territory = 20
        game.player_black.black_set_len = 0
        game.player_white.white_set_len = 0
        ui.end_game_popup(game)

        mock_popup.assert_called_with(
            "Your game has finished.\nPlayer Black: Player1 has 15 territory\
            , and played 0 pieces and has a komi of 6.5\
            \n Player White: Player2 has 20 territory, and played 0 pieces\
              and has a komi of 6.5\n Player Black has a score of 21.5\n\
            Player White has a score of 26.5, meaning Player White won by 5.0 points",
            title="Game has Concluded",
            line_width=200,
            auto_close=True,
            auto_close_duration=20
        )

    @pytest.mark.parametrize("b_size", [(9), (13), (19)])
    @patch("pygame.draw.line")
    @patch("pygame.draw.circle")
    def test_draw_gameboard(self, mock_draw_circle, mock_draw_line, b_size):
        game_board = MagicMock()
        game_board.board_size = b_size
        game_board.star_points_count = 4
        screen = MagicMock()
        gameboard_surface = pygame.Surface((700, 700))

        ui.draw_gameboard(game_board, screen, gameboard_surface)
        assert mock_draw_line.call_count == 2 * (game_board.board_size - 1) * game_board.board_size
        assert mock_draw_circle.call_count == game_board.star_points_count

    @patch("PySimpleGUI.Window")
    def test_switch_button_mode_scoring(self, mock_window):
        board = MagicMock()
        board.mode = "Scoring"
        board.window = mock_window
        board.times_passed = 0

        ui.switch_button_mode(board)

        mock_window.__getitem__.assert_called_with("Res")
        mock_window.__getitem__.return_value.update.assert_called_with("Resume Game")
        assert board.times_passed == 0
        assert not board.mode_change

    @patch("PySimpleGUI.Window")
    def test_switch_button_mode_playing(self, mock_window):
        board = MagicMock()
        board.mode = "Playing"
        board.window = mock_window

        ui.switch_button_mode(board)

        mock_window.__getitem__.assert_called_with("Res")
        mock_window.__getitem__.return_value.update.assert_called_with("Quit Program")
        assert not board.mode_change

    @pytest.mark.parametrize("the_type", [(cf.rgb_black), (cf.rgb_peach)])
    @patch("pygame.draw.circle")
    def test_refresh_board_pygame(self, mock_draw_circle, the_type):
        if os.getenv("DISPLAY") is not None:
            board = MagicMock()
            board.backup_board = MagicMock()
            board.screen = MagicMock()
            board.pygame_board_vals = [700, 620 / 8, 620 / 24]
            board.board_size = 9

            board.board = [[MagicMock(stone_here_color=the_type, screen_row=50, screen_col=50)
                            for _ in range(9)] for _ in range(9)]

            ui.refresh_board_pygame(board)
            assert mock_draw_circle.call_count == board.board_size ** 2

    @patch("PySimpleGUI.Window")
    @patch("pygame.display.quit")
    def test_close_window_linux(self, mock_display_quit, mock_window):
        with patch("platform.system", return_value="Linux"):
            board = MagicMock()
            board.window = mock_window
            board.backup_board = MagicMock()

            ui.close_window(board)
            mock_window.close.assert_called_once_with()
            assert not mock_display_quit.called
