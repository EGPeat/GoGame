import unittest
from unittest.mock import patch, MagicMock
import sys
sys.path.append("/users/5/a1895735/Documents/PythonProjects/GoGame/")
import goclasses as go
import game_initialization as start
# pytest --collect-only


class TestClassGoClasses(unittest.TestCase):

    def test_choose_board_type_go_board(self):
        from botnormalgo import BotBoard
        self.assertIsInstance(go.choose_board_type(True, False), BotBoard)

    def test_choose_board_type_bot_board(self):
        self.assertIsInstance(go.choose_board_type(False, False), go.GoBoard)

    @patch("goclasses.initialize_player_choice")
    @patch("goclasses.ui.setup_board_window_pygame")
    @patch("goclasses.request_handicap_info")
    def test_initializing_game_with_defaults(self, mock_request_handicap_info, mock_setup_board, mock_initialize_player_choice):
        window_mock = MagicMock()
        board_size = 9

        start.initializing_game(window_mock, board_size)

        mock_initialize_player_choice.assert_called_once_with(board_size, True, False)
        mock_setup_board.assert_called_once_with(mock_initialize_player_choice.return_value)
        mock_request_handicap_info.assert_not_called()
        mock_initialize_player_choice.return_value.play_game.assert_called_once_with(fixes_handicap=False)

    @patch("goclasses.initialize_player_choice")
    @patch("goclasses.ui.setup_board_window_pygame")
    @patch("goclasses.request_handicap_info", return_value=True)
    def test_initializing_game_without_defaults(self, mock_request_handicap_info, mock_setup_board, mock_initialize_player_choice):
        window_mock = MagicMock()
        board_size = 9

        start.initializing_game(window_mock, board_size, defaults=False)

        mock_initialize_player_choice.assert_called_once_with(board_size, False, False)
        mock_setup_board.assert_called_once_with(mock_initialize_player_choice.return_value)
        mock_request_handicap_info.assert_called_once()
        mock_initialize_player_choice.return_value.play_game.assert_called_once_with(fixes_handicap=True)

    def test_setup_board(self):
        # Create an instance of your class
        your_instance = go.GoBoard(board_size=9)  # Replace with the actual constructor parameters

        # Call the method you want to test
        board = your_instance.setup_board()

        # Assertions to check if the board is set up correctly
        self.assertEqual(len(board), your_instance.board_size)
        for row in board:
            self.assertEqual(len(row), your_instance.board_size)
            for item in row:
                self.assertIsInstance(item, go.BoardNode)
                self.assertIsInstance(item.screen_row, float)
                self.assertIsInstance(item.screen_col, float)
                self.assertGreaterEqual(item.screen_row, 0)
                self.assertGreaterEqual(item.screen_col, 0)

                # Check if connections are set up correctly
                for neighbor in item.connections:
                    self.assertIsInstance(neighbor, go.BoardNode)
