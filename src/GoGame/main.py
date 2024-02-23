import GoGame.game_initialization as start
import GoGame.uifunctions as ui
import PySimpleGUI as sg


def play_game_main():
    '''
    This function initiates a PySimpleGui window, allowing the user to choose from various game options.
    The user can load from file, start a custom new game, start a custom default game, play a game against AI,
    Watch AIs play themselves, or train the AIs.
    It then calls the appropriate functions.
    '''
    window = ui.setup_menu()

    while True:
        event, _ = window.read()

        if event == "Choose File":
            from GoGame.saving_loading import choose_file
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
            from GoGame.neuralnet import training_cycle
            window.close()
            import cProfile
            import pstats
            with cProfile.Profile() as pr:
                training_cycle(5)
                stats = pstats.Stats(pr)
                stats.sort_stats(pstats.SortKey.TIME)
                stats.dump_stats(filename="5000x30testingv3.prof")
        elif event == "AI Training":
            from GoGame.neuralnet import loading_file_for_training
            window.close()
            loading_file_for_training(epochs=10, size_of_batch=32)
        elif event in (sg.WIN_CLOSED, 'Exit Game'):
            break

    window.close()


if __name__ == "__main__":
    sg.theme('DarkAmber')
    play_game_main()
