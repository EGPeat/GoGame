import goclasses as go
import uifunctions as ui
import PySimpleGUI as sg
import pygametest as pygt
from server import start_home_server
import threading
# To do:
# Add AI to game
# server thing doesnt handle me quitting rn
# server thing for multiplayer for removing dead stones/etc
# Typechecking setting in VSCode...
# Go back and fix the x and y mixup
# Fix up the issue regarding the MCST and edge cases regarding eyes (talk to professor)


def play_game_main():
    window = ui.setup_menu()

    while True:
        event, _ = window.read()

        if event == "Choose File":
            from os import chdir, getcwd, path
            wd = getcwd()
            full_path = path.join(wd, 'pklfiles')
            if not wd.endswith('pklfiles'):
                chdir(full_path)
            file = sg.popup_get_file('Select a file', title="File selector", font=('Arial Bold', 15))
            if file is None or file == "":
                continue
            file = file.split("/")
            file = file[-1]
            sg.popup_no_buttons('You chose', file, non_blocking=True, font=('Arial Bold', 15),
                                auto_close=True, auto_close_duration=3)
            go_board = go.GoBoard()
            friend = go_board.load_pkl(file)
            ui.setup_board_window_pygame(friend)
            window.close()
            friend.play_game(True, False)

        elif event == "New Game From Custom":
            board_size = ui.start_game()
            go.initializing_game(window, board_size, defaults=False, fixes_handicap=True)

        elif event == "New Game From Default":
            go.initializing_game(window, 9, True)
        elif event == "Play Against AI":
            go.initializing_game(window, 9, True, vs_bot=True)
        elif event == "Play Multiplayer as host":
            import queue
            result_queue = queue.Queue()
            client_thread = threading.Thread(target=start_home_server, args=(result_queue,))
            client_thread.start()
            item1 = str(result_queue.get())
            item2 = str(result_queue.get())
            ui.server_info_button(item1, item2)
            go.initializing_game(window, board_size=9, defaults=True, vs_other_person=True, password=item1)

        elif event == "Play Multiplayer not as host":
            from player import Player
            ip = Player.get_input("Please enter a ip address:", lambda x: str(x)[:30])
            password2 = Player.get_input("Please enter a password:", lambda x: str(x)[:30])
            go.initializing_game(window, board_size=9, defaults=True, vs_other_person=True, password=password2, ip_address=ip)

        elif event == "New Hex Game":
            window.close()
            pygt.main()

        if event in (sg.WIN_CLOSED, 'Exit Game'):
            break

    window.close()


if __name__ == "__main__":
    sg.theme('DarkAmber')
    play_game_main()
