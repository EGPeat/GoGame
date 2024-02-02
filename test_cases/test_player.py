from unittest.mock import patch
import sys
import pytest
sys.path.append("/users/5/a1895735/Documents/PythonProjects/GoGame/")
import player
import config as cf


class TestClassPyTestPlayer:

    @patch("player.Player.choose_name")
    @patch("player.Player.choose_komi")
    def test_setup_player(self, mock_choose_name, mock_choose_komi):
        answer = player.Player.setup_player(defaults=False, nme="Temp", clr="Black", uc=cf.unicode_black)
        assert isinstance(answer, player.Player)

    @pytest.mark.parametrize("typed_texts", [["aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa", "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"]])
    def test_choose_name_yes(self, typed_texts, mocker):
        mocker.patch('PySimpleGUI.popup_get_text', side_effect=typed_texts)
        mocker.patch('PySimpleGUI.popup_yes_no', return_value="Yes")
        playa = player.Player(color="Black")
        with patch('PySimpleGUI.popup') as _:
            player.Player.choose_name(playa)
        assert playa.name == typed_texts[-1]

    @pytest.mark.parametrize("color, final_name", [("Black", "Player One"), ("White", "Player Two")])
    def test_choose_name_no(self, color, final_name, mocker):
        mocker.patch('PySimpleGUI.popup_yes_no', return_value="No")
        playa = player.Player(color=color)
        playa.color == color
        with patch('PySimpleGUI.popup') as _:
            player.Player.choose_name(playa)
        assert playa.name == final_name

    @pytest.mark.parametrize("typed_texts", [["a", ' ', 'None', "5"]])
    def test_choose_komi_yes(self, typed_texts, mocker):
        mocker.patch('PySimpleGUI.popup_get_text', side_effect=typed_texts)
        mocker.patch('PySimpleGUI.popup_yes_no', return_value="Yes")
        playa = player.Player(color="Black")
        with patch('PySimpleGUI.popup') as _:
            player.Player.choose_komi(playa)
        assert playa.komi == 5

    @pytest.mark.parametrize("color, final_komi", [("Black", 0), ("White", 6.5)])
    def test_choose_komi_no(self, color, final_komi, mocker):
        mocker.patch('PySimpleGUI.popup_yes_no', return_value="No")
        playa = player.Player(color=color)
        playa.color == color
        with patch('PySimpleGUI.popup') as _:
            player.Player.choose_komi(playa)
        assert playa.komi == final_komi
