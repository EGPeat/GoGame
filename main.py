import goclasses as go
import uifunctions as ui
import PySimpleGUI as sg
import pygametest as pygt
# To do:
# Typechecking setting in VSCode...
# Go back and fix the x and y mixup
# x and y also mixed up in the nn mcst
# Make it so the MCST/NN won't pass until later on?
# It will play the exact same game everytime...


def play_game_main():
    '''
    This function initiates a pySimpleGui window, allowing the user to choose from various game options.
    The user can load from file, start a custom new game, start a custom default game, play a game against AI,...
    Host a multiplayer game, connect to a multiplayer game, or play a hex version of go.
    It then calls the appropriate functions.
    '''
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
        elif event == "AI SelfPlay":
            from neuralnet import training_cycle
            window.close()
            import cProfile
            import pstats
            with cProfile.Profile() as pr:
                training_cycle()
                stats = pstats.Stats(pr)
                stats.sort_stats(pstats.SortKey.TIME)
                stats.dump_stats(filename="5000x30testingv3.prof")
        elif event == "AI Training":
            from neuralnet import loading_file_for_training
            window.close()
            loading_file_for_training()
        elif event == "New Hex Game":
            window.close()
            pygt.main()

        if event in (sg.WIN_CLOSED, 'Exit Game'):
            break

    window.close()


if __name__ == "__main__":
    sg.theme('DarkAmber')
    play_game_main()
