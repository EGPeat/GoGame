import goclasses as go
import uifunctions as ui
import PySimpleGUI as sg
import pygametest as pygt

# To do:
# Add AI to game
# Add MP to game


def play_game_main():
    window = ui.setup_menu()

    while True:
        event, values = window.read()

        if event == "Choose File":
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
            print(f"friend is {friend.mode}")
            friend.play_game(True, False)

        elif event == "New Game From Custom":
            board_size = ui.start_game()
            go.initializing_game(window, board_size, defaults=False, fixes_handicap=True)

        elif event == "New Game From Default":
            go.initializing_game(window, 9, True)
        elif event == "New Hex Game":
            window.close()
            pygt.main()

        if event in (sg.WIN_CLOSED, 'Exit Game'):
            break

    window.close()


if __name__ == "__main__":

    sg.theme('DarkAmber')
    play_game_main()
