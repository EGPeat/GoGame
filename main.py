import game_initialization as start
import uifunctions as ui
import PySimpleGUI as sg
import pygametest as pygt
# from test_cases.testinggoclasses import test_function
# To do:
# Typehint more/better
# x and y also mixed up in the nn mcst
# Make it so the MCST/NN won't pass until later on?
# It will play the exact same game everytime...
# move programming files to a new folder
# Add readme and better documentation


def play_game_main():
    '''
    This function initiates a pySimpleGui window, allowing the user to choose from various game options.
    The user can load from file, start a custom new game, start a custom default game, play a game against AI,...
    Host a multiplayer game, connect to a multiplayer game, or play a hex version of go.
    It then calls the appropriate functions.
    '''
    window = ui.setup_menu()

    # All of the go.initializing_game stuff is kinda messed up in python 3.9, but good in 3.10
    while True:
        event, _ = window.read()

        if event == "Choose File":
            from saving_loading import choose_file
            choose_file(window)
            break

        elif event == "New Game From Custom":
            board_size = ui.start_game()
            start.initializing_game(window, board_size, defaults=False)

        elif event == "New Game From Default":
            start.initializing_game(window, 9, True)
        elif event == "Play Against AI":
            start.initializing_game(window, 9, True, vs_bot=True)
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

        elif event in (sg.WIN_CLOSED, 'Exit Game'):
            break

    window.close()


if __name__ == "__main__":
    sg.theme('DarkAmber')
    play_game_main()
