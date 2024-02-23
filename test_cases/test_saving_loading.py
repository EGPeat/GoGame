from unittest.mock import patch, MagicMock, Mock
import pytest
import GoGame.saving_loading as save
cur_dir = "/users/5/a1895735/Documents/PythonProjects/GoGame/"


class TestClassPyTestSavingLoading:

    @pytest.mark.parametrize("savename", [("forunittesting2"), ((None), ("forunittesting2"))])
    @patch('pickle.dump')
    def test_save_pickle(self, mock_pickle, savename):
        from os import remove, path
        board_mock = Mock()
        initial_window_mock_window = board_mock.window = Mock()
        initial__board_mock_screen = board_mock.screen = Mock()
        initial_board_mock_backup_board = board_mock.backup_board = Mock()

        with patch('PySimpleGUI.popup_get_text', side_effect=savename):
            save.save_pickle(board_mock)
        dir = save.move_to_pkl_directory()
        full_path = path.join(dir, 'f.pkl')
        if path.isfile(full_path):
            remove(full_path)
        assert board_mock.window == initial_window_mock_window
        assert board_mock.screen == initial__board_mock_screen
        assert board_mock.backup_board == initial_board_mock_backup_board

    @patch("os.getcwd", return_value=f'{cur_dir}')
    @patch("os.chdir")
    def test_move_to_pkl_directory_normal(self, mock_chdir, mock_getcwd):
        file = save.move_to_pkl_directory()
        mock_chdir.assert_called_once_with(f'{cur_dir}pklfiles')
        file = file.split("/")
        file = file[-1]
        assert file == 'pklfiles'

    def test_load_pkl(self):
        input_path = f'{cur_dir}test_cases/pklfilestesting/for_unit_testing.pkl'
        result = save.load_pkl(input_path)
        assert len(result.killed_last_turn) == 1
        assert result.position_played_log == [('Black', 0, 1), ('White', 0, 0), ('Black', 1, 0)]
        assert result.killed_log == [[], [], [((255, 255, 255), 0, 0)]]

    @patch('PySimpleGUI.popup_get_file', return_value=f'{cur_dir}test_cases/pklfilestesting/for_unit_testing.pkl')
    @patch('PySimpleGUI.popup_no_buttons')
    @patch('GoGame.saving_loading.load_pkl', return_value=MagicMock())
    @patch("GoGame.uifunctions.setup_board_window_pygame")
    def test_choose_file(self, mock_setup_board, mock_load_pkl, mock_no_buttons, mock_get_file):
        window_mock = Mock()
        window_mock.close = Mock()
        save.choose_file(window_mock)

        mock_no_buttons.assert_called_once_with('You chose', 'for_unit_testing.pkl', non_blocking=True, font=('Arial Bold', 15),
                                                auto_close=True, auto_close_duration=3)
        mock_load_pkl.assert_called_once_with('for_unit_testing.pkl')
        window_mock.close.assert_called_once()

    @patch('PySimpleGUI.popup_get_file', return_value=None)
    @patch('PySimpleGUI.popup_no_buttons')
    @patch('GoGame.saving_loading.load_pkl', return_value=MagicMock())
    @patch("GoGame.uifunctions.setup_board_window_pygame")
    def test_choose_file_none(self, mock_setup_board, mock_load_pkl, mock_no_buttons, mock_get_file):
        window_mock = Mock()
        window_mock.close = Mock()
        save.choose_file(window_mock)
        mock_no_buttons.assert_not_called()
        mock_load_pkl.assert_not_called()
        window_mock.assert_not_called()
