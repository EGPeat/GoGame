import uifunctions as ui
import PySimpleGUI as sg
from time import sleep
from typing import Optional


class Player():
    def __init__(self, name: Optional[str] = None, color: Optional[str] = None,
                 captured: int = 0, komi: float = 0, unicode_choice: Optional[tuple] = None):
        self.name: Optional[str] = name
        self.color: Optional[str] = color
        self.captured: int = captured
        self.komi: float = komi
        self.unicode: Optional[tuple] = unicode_choice
        self.territory: int = 0

    @staticmethod
    # This sets up the Player class, assigning appropriate values to each player as needed
    def setup_player(defaults, nme, clr, uc):
        if defaults:
            if clr == "Black":
                player_assignment = Player(name=nme, color=clr, unicode_choice=uc)
            else:
                player_assignment = Player(name=nme, color=clr, komi=6.5, unicode_choice=uc)
        else:
            player_assignment = Player(color=clr, unicode_choice=uc)
            player_assignment.choose_name()
            player_assignment.choose_komi()
        return player_assignment

    def choose_name(self) -> None:  # feels like i could somehow combine choose_name and choose_komi...
        info: str = "Please Click Yes if you want to change your name"
        modify_name: str = sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))
        if modify_name == "No":
            self.name = "Player Two" if self.color == "White" else "Player One"
            return
        self.name = self._get_input("Please enter a name you would like to use, but keep it less\
                                    than 30 characters:", lambda x: str(x)[:30])

    def choose_komi(self) -> None:
        info: str = "Please Click Yes if you want to change your Komi"
        modify_komi: str = sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))
        if modify_komi == "No" and self.color == "White":
            self.komi = 7.5
            return
        elif modify_komi == "No":
            return
        self.komi = self._get_input(f"Your color is {self.color}. Please enter Komi Value. 6.5 is normally done,\
                                    but only for white:", float)

    def _get_input(self, info, conversion_func):
        done = False
        while not done:
            try:
                user_input = ui.validation_gui(info, conversion_func)
                done = True
            except ValueError:
                ui.default_popup_no_button(info="Invalid input. Please try again", time=2)
                sleep(1.3)
        return user_input
