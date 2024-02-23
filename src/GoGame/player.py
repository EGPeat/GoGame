import GoGame.uifunctions as ui
import PySimpleGUI as sg
from typing import Optional, Tuple, Type


class Player():
    def __init__(self, name: Optional[str] = None, color: Optional[str] = None,
                 komi: float = 0, unicode_choice: Optional[tuple] = None):
        '''
        Initializes a Player object.
        Args:
            name: The name of the player.
            color: The color of the player.
            komi: The komi value for the player.
            unicode_choice: The Unicode choice for the player.
        '''
        self.name: Optional[str] = name
        self.color: Optional[str] = color
        self.komi: float = komi
        self.unicode: Tuple[int, int, int] = unicode_choice
        self.territory: int = 0

    @staticmethod
    def setup_player(defaults, nme, clr, uc) -> Type['Player']:
        '''
        Makes a Player instance.
        Args:
            defaults: A flag indicating whether to use default values.
            nme: The name of the player.
            clr: The color of the player.
            uc: The Unicode choice for the player.
        Returns a instance of the Player class.
        '''
        if defaults:
            if clr == "Black":
                player_assignment = Player(name=nme, color=clr, unicode_choice=uc)
            else:
                player_assignment = Player(name=nme, color=clr, komi=7.5, unicode_choice=uc)
        else:
            player_assignment = Player(color=clr, unicode_choice=uc)
            player_assignment.choose_name()
            player_assignment.choose_komi()
        return player_assignment

    @staticmethod
    def get_input(info, conversion_func):
        '''Gets user input, with error handling included.'''
        done = False
        while not done:
            try:
                user_input = ui.validation_gui(info, conversion_func)
                done = True
            except ValueError:
                ui.default_popup_no_button(info="Invalid input. Please try again", time=2)
        return user_input

    def choose_name(self) -> None:
        "Allows a player to choose their name, otherwise sets it to a default value."
        info: str = "Please Click Yes if you want to change your name"
        modify_name: str = sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))
        if modify_name == "No":
            self.name = "Player Two" if self.color == "White" else "Player One"
            return
        self.name = Player.get_input("Please enter a name you would like to use, but keep it less\
                                    than 30 characters:", lambda x: str(x)[:30])

    def choose_komi(self) -> None:
        "Allows a player to choose their komi, otherwise sets it to a default value."
        info: str = "Please Click Yes if you want to change your Komi"
        modify_komi: str = sg.popup_yes_no(info, title="Please Click", font=('Arial Bold', 15))
        if modify_komi == "No" and self.color == "White":
            self.komi = 7.5
            return
        elif modify_komi == "No":
            return
        self.komi = Player.get_input(f"Your color is {self.color}. Please enter Komi Value. 7.5 is normally done,\
                                    but only for white:", float)
