from unittest.mock import patch
import GoGame.uifunctions as ui
import PySimpleGUI as sg
import GoGame.main as mn


class TestClassPyTestMain:

    @patch("PySimpleGUI.Window")
    @patch("GoGame.uifunctions.setup_menu")
    def test_play_game_main_EXIT(self, mock_window, mock_setup_menu, mocker):
        mock_window.return_value.read.return_value = ('Exit Game', None)
        mn.play_game_main()
        mock_window.assert_called_once()
        mock_window.return_value.close.assert_called_once_with()
        window = ui.setup_menu()
        event, _ = window.read()
        assert event == 'Exit Game'

    @patch("PySimpleGUI.Window")
    @patch("GoGame.uifunctions.setup_menu")
    def test_play_game_main_WIN_CLOSED(self, mock_window, mock_setup_menu, mocker):
        mock_window.return_value.read.return_value = (sg.WIN_CLOSED, None)
        mn.play_game_main()
        mock_window.assert_called_once()
        mock_window.return_value.close.assert_called_once_with()
        window = ui.setup_menu()
        event, _ = window.read()
        assert event == sg.WIN_CLOSED

    @patch("GoGame.game_initialization.initializing_game")
    @patch("PySimpleGUI.Window")
    @patch("GoGame.uifunctions.setup_menu")
    def test_play_game_main_PLAY_AI(self, mock_window, mock_game_init, mock_setup_menu, mocker):
        mock_window.return_value.read.side_effect = [("Play Against AI", None),
                                                     ("Exit Game", None), ("Play Against AI", None)]
        mn.play_game_main()
        mock_window.assert_called_once()
        mock_window.return_value.close.assert_called_once_with()
        window = ui.setup_menu()
        event, _ = window.read()
        assert event == "Play Against AI"

    @patch("GoGame.game_initialization.initializing_game")
    @patch("PySimpleGUI.Window")
    @patch("GoGame.uifunctions.setup_menu")
    def test_play_game_main_DEFAULT(self, mock_window, mock_game_init, mock_setup_menu, mocker):
        mock_window.return_value.read.side_effect = [("New Game From Default", None),
                                                     ("Exit Game", None), ("New Game From Default", None)]
        mn.play_game_main()
        mock_window.assert_called_once()
        mock_window.return_value.close.assert_called_once_with()
        window = ui.setup_menu()
        event, _ = window.read()
        assert event == "New Game From Default"

    @patch("GoGame.uifunctions.start_game")
    @patch("GoGame.game_initialization.initializing_game")
    @patch("PySimpleGUI.Window")
    @patch("GoGame.uifunctions.setup_menu")
    def test_play_game_main_CUSTOM(self, mock_window, mock_game_init, mock_setup_menu, mock_ui, mocker):
        mock_window.return_value.read.side_effect = [("New Game From Custom", None),
                                                     ("Exit Game", None), ("New Game From Custom", None)]
        mn.play_game_main()
        mock_window.assert_called_once()
        mock_window.return_value.close.assert_called_once_with()
        window = ui.setup_menu()
        event, _ = window.read()
        assert event == "New Game From Custom"

    @patch("GoGame.saving_loading.choose_file")
    @patch("PySimpleGUI.Window")
    @patch("GoGame.uifunctions.setup_menu")
    def test_play_game_main_CHOOSE_FILE(self, mock_window, mock_setup_menu, mock_choose, mocker):
        mock_window.return_value.read.return_value = ("Choose File", None)
        mn.play_game_main()
        mock_window.assert_called_once()
        mock_window.return_value.close.assert_called_once_with()
        window = ui.setup_menu()
        event, _ = window.read()
        assert event == "Choose File"
