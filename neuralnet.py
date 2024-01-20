import neuralnetboard as nn
import numpy as np
from typing import List
import sys
import keras as keras
# Add in something to train the ai model more times, but every once in a while backup the parameters
np.set_printoptions(threshold=sys.maxsize)
# https://keras.io/guides/making_new_layers_and_models_via_subclassing/


def nn_model(input_array):
    conv_output = nn_model_conv_layer(input_array)
    res_output = nn_model_res_layer(conv_output)
    for _ in range(39):
        res_output = nn_model_res_layer(res_output)

    policy_output = nn_model_policy_head(res_output)
    value_output = nn_model_value_head(res_output)
    return (value_output, policy_output)


def nn_model_conv_layer(input_array):
    input_array = np.expand_dims(input_array, axis=0)
    conv1 = keras.layers.Conv2D(256, (3, 3), strides=(1, 1), padding='same', input_shape=(16, 9, 9))(input_array)
    b_norm_1 = keras.layers.BatchNormalization()(conv1)
    relu_1 = keras.layers.ReLU()(b_norm_1)
    return relu_1


def nn_model_res_layer(input_array):
    conv1 = keras.layers.Conv2D(256, (3, 3), strides=(1, 1), padding='same', input_shape=(16, 9, 9))(input_array)
    b_norm_1 = keras.layers.BatchNormalization()(conv1)
    relu_1 = keras.layers.ReLU()(b_norm_1)
    conv2 = keras.layers.Conv2D(256, (3, 3), strides=(1, 1), padding='same', input_shape=(16, 9, 9))(relu_1)
    b_norm_2 = keras.layers.BatchNormalization()(conv2)
    added = keras.layers.Add()([input_array, b_norm_2])
    relu_2 = keras.layers.ReLU()(added)
    return relu_2


def nn_model_policy_head(input_array):
    conv1 = keras.layers.Conv2D(2, (1, 1), strides=(1, 1), padding='same', input_shape=(16, 9, 9))(input_array)
    b_norm_1 = keras.layers.BatchNormalization()(conv1)
    relu_1 = keras.layers.ReLU()(b_norm_1)
    flatten_1 = keras.layers.Flatten()(relu_1)
    dense_1 = keras.layers.Dense(82)(flatten_1)
    output_choices = keras.layers.Softmax()(dense_1)
    return output_choices


def nn_model_value_head(input_array):
    conv1 = keras.layers.Conv2D(1, (1, 1), strides=(1, 1), padding='same', input_shape=(16, 9, 9))(input_array)
    b_norm_1 = keras.layers.BatchNormalization()(conv1)
    relu_1 = keras.layers.ReLU()(b_norm_1)
    flatten_1 = keras.layers.Flatten()(relu_1)
    dense1 = keras.layers.Dense(256)(flatten_1)
    relu_2 = keras.layers.ReLU()(dense1)
    win_chances = keras.layers.Dense(1, activation='tanh')(relu_2)
    return win_chances


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


def neural_net_calcuation(input_boards: List[str], board_size: int):
    input_array = np.zeros((17, board_size, board_size), dtype=np.float32)
    board_idx = 0
    color_turn = 0
    if int(input_boards[-1][0][0]) == 1:
        color_turn = 1
    else:
        color_turn = 2

    while input_boards:
        pop_board = input_boards.pop(0)
        if len(pop_board) != board_size * board_size:
            pop_board = pop_board[1:]

        if color_turn == 1 and len(input_boards) != 0:
            helper_black(input_array, pop_board, board_size, board_idx)
            board_idx += 1
            helper_white(input_array, pop_board, board_size, board_idx)
            board_idx += 1
        elif color_turn == 2 and len(input_boards) != 0:
            helper_white(input_array, pop_board, board_size, board_idx)
            board_idx += 1
            helper_black(input_array, pop_board, board_size, board_idx)
            board_idx += 1

        if len(input_boards) == 0:
            helper_end(input_array, pop_board, board_size, board_idx)

    print("uwu2")
    output_array = nn_model(input_array)

    print(input_array)
    print(output_array)
    val = np.argmax(output_array[1])
    print(val)

    row = val // board_size
    col = val % board_size
    print(f"the value spot is {row},{col}")
    print("uwu")

    print("owo")


def helper_black(input_array, pop_board, board_size, board_idx):
    for idx in range(len(pop_board)):
        val = int(pop_board[idx])
        if val == 1:
            val = 1
        if val == 2:
            val = 0
        row = idx // board_size
        col = idx % board_size
        input_array[board_idx][row][col] = val
    board_idx += 1


def helper_white(input_array, pop_board, board_size, board_idx):
    for idx in range(len(pop_board)):
        val = int(pop_board[idx])
        if val == 1:
            val = 0
        if val == 2:
            val = 1
        row = idx // board_size
        col = idx % board_size
        input_array[board_idx][row][col] = val
    board_idx += 1


def helper_end(input_array, pop_board, board_size, board_idx):
    for idx in range(len(pop_board)):
        val = int(pop_board[idx])
        if val == 2:
            val = 0
        row = idx // board_size
        col = idx % board_size
        input_array[board_idx][row][col] = val
    board_idx += 1
