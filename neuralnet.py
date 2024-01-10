import neuralnetboard as nn


def training_run():
    temp = nn.initializing_game(9, True, vs_bot=True, ai_training=True, no_window=True)
    print(len(temp[0]))
    print("\n")
    return temp


def training_cycle():
    info_for_ai = []
    length = 200
    sum_val = 0
    """import cProfile
    import pstats
    with cProfile.Profile() as pr:
        for _ in range(length):
            info_for_ai.append(training_run(window))
            if info_for_ai[-1][1] == 1:
                sum_val += 1
        print(f"the amount is {sum_val} out of {length} games or a win percentage of {sum_val/length}")
        stats = pstats.Stats(pr)
        stats.sort_stats(pstats.SortKey.TIME)
        stats.print_stats()
        stats.dump_stats(filename="5000x30testingv3.prof")"""
    import time
    start_time = time.time()
    for _ in range(length):
        info_for_ai.append(training_run())
        if info_for_ai[-1][1] == 1:
            sum_val += 1
    print(f"the amount is {sum_val} out of {length} games or a win percentage of {sum_val/length}")
    print("--- %s seconds ---" % (time.time() - start_time))
    from sys import getsizeof
    print(getsizeof(info_for_ai))
