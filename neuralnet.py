import goclasses as go

# This setup for the neuralnet has it making a pysimplegui window and etc. It's not necessary, but would take extra work to fix.
# Fix it eventually


def training_run(window):
    temp = go.initializing_game(window, 9, True, vs_bot=True, ai_training=True, no_window=True)
    print(len(temp))
    print(len(temp[0]))
    print("\n\n")
    # print(temp)
    return temp


def training_cycle(window):
    info_for_ai = []
    length = 25
    sum_val = 0
    # import cProfile
    # import pstats
    # with cProfile.Profile() as pr:
    for _ in range(length):
        info_for_ai.append(training_run(window))
        if info_for_ai[-1][1] == 1:
            sum_val += 1
    print(f"the amount is {sum_val} out of {length} games or a win percentage of {sum_val/length}")
    # stats = pstats.Stats(pr)
    # stats.sort_stats(pstats.SortKey.TIME)
    # stats.print_stats()
    # stats.dump_stats(filename="5000x30testingv3.prof")
