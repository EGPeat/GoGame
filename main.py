import goclasses as go
import uifunctions as ui
import PySimpleGUI as sg

# Stuff to look into
# https://github.com/wonsiks/BadukMegapack
# https://github.com/mattheww/sgfmill
# https://www.oipaz.net/Carta.pdf   could provide a way for the computer to calculate score completely
# https://github.com/search?q=baduk+language%3APython&type=repositories&p=1&l=Python
# https://github.com/inclement/LazyBaduk/tree/master
# https://github.com/dakota-marshall/python-ogs
# https://github.com/MORaHo/Go-Baduk-Weiqi
# https://utf8-chartable.de/unicode-utf8-table.pl?start=10624&number=512&unicodeinhtml=hex
# https://senseis.xmp.net/?JapaneseCountingExample

# To do:
# Remake gui in Kivy or etc
# Add AI to game
# Add MP to game

# resuming then undoing turn is messed up
# passing and then undoing is also messed up
# removing dead stones removes the wrong ones? Maybe?


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
            board_size = load_board_size(file)
            go.initializing_game(window, board_size, defaults=True, file_import_option=True, from_file=True, choosen_file=file)

        elif event == "New Game From Custom":
            board_size = ui.start_game()
            go.initializing_game(window, board_size, defaults=False, from_file=False, fixes_handicap=True)

        elif event == "New Game From Default":
            go.initializing_game(window, 9, True)

        if event in (sg.WIN_CLOSED, 'Exit Game'):
            break

    window.close()


def load_board_size(file):
    data_to_parse = go.load_and_parse_file(file)
    board_size = data_to_parse["board_size"]
    return board_size


if __name__ == "__main__":

    sg.theme('DarkAmber')
    play_game_main()
