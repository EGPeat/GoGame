import neuralnetboard as nn
import numpy as np
from typing import List
import sys
import keras as keras
np.set_printoptions(threshold=sys.maxsize)


def nn_model():
    shapez = (17, 9, 9)
    input_layer = keras.layers.Input(shape=shapez)
    conv_output = nn_model_conv_layer(input_layer)
    res_output = nn_model_res_layer(conv_output)
    for _ in range(9):
        res_output = nn_model_res_layer(res_output)

    policy_output = nn_model_policy_head(res_output)
    value_output = nn_model_value_head(res_output)
    model = keras.models.Model(inputs=input_layer, outputs={'dense_2': value_output, 'softmax': policy_output})
    load_model_weights(model)
    return model


def nn_model_conv_layer(input_array):
    conv1 = keras.layers.Conv2D(256, (3, 3), strides=(1, 1), padding='same', input_shape=(17, 9, 9))(input_array)
    b_norm_1 = keras.layers.BatchNormalization()(conv1)
    relu_1 = keras.layers.ReLU()(b_norm_1)
    return relu_1


def nn_model_res_layer(input_array):
    conv1 = keras.layers.Conv2D(256, (3, 3), strides=(1, 1), padding='same', input_shape=(17, 9, 9))(input_array)
    b_norm_1 = keras.layers.BatchNormalization()(conv1)
    relu_1 = keras.layers.ReLU()(b_norm_1)
    conv2 = keras.layers.Conv2D(256, (3, 3), strides=(1, 1), padding='same', input_shape=(17, 9, 9))(relu_1)
    b_norm_2 = keras.layers.BatchNormalization()(conv2)
    added = keras.layers.Add()([input_array, b_norm_2])
    relu_2 = keras.layers.ReLU()(added)
    return relu_2


def nn_model_policy_head(input_array):
    conv1 = keras.layers.Conv2D(2, (1, 1), strides=(1, 1), padding='same', input_shape=(17, 9, 9))(input_array)
    b_norm_1 = keras.layers.BatchNormalization()(conv1)
    relu_1 = keras.layers.ReLU()(b_norm_1)
    flatten_1 = keras.layers.Flatten()(relu_1)
    dense_1 = keras.layers.Dense(82)(flatten_1)
    output_choices = keras.layers.Softmax()(dense_1)
    return output_choices


def nn_model_value_head(input_array):
    conv1 = keras.layers.Conv2D(1, (1, 1), strides=(1, 1), padding='same', input_shape=(17, 9, 9))(input_array)
    b_norm_1 = keras.layers.BatchNormalization()(conv1)
    relu_1 = keras.layers.ReLU()(b_norm_1)
    flatten_1 = keras.layers.Flatten()(relu_1)
    dense1 = keras.layers.Dense(256)(flatten_1)
    relu_2 = keras.layers.ReLU()(dense1)
    win_chances = keras.layers.Dense(1, activation='tanh')(relu_2)
    return win_chances


def training_cycle():
    info_for_ai = []
    length = 1
    sum_val = 0
    import time
    start_time = time.time()
    for _ in range(length):
        info_for_ai.append(nn.initializing_game(9, True))
        if info_for_ai[-1] == 1:
            sum_val += 1
        loading_file_for_training()
    print(f"the amount is {sum_val} out of {length} games or a win percentage of {sum_val/length}")
    print("--- %s seconds ---" % (time.time() - start_time))


def neural_net_calcuation(input_boards: List[str], board_size: int, input_nn):
    input_array = generate_17_length(input_boards, board_size)
    nn_model_called = input_nn
    input_array = np.expand_dims(input_array, axis=0)
    output = nn_model_called.predict(input_array, verbose=0)
    value_output = float(output['dense_2'][0][0])
    policy_output = output['softmax']
    output_array = ((value_output, policy_output))
    # float casting could cause some sort of loss of percision?. Fix later
    return output_array


def generate_17_length(input_boards: List[str], board_size: int):
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
    return input_array


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


def save_model_weights(model, filename="model_weights.h5"):
    model.save_weights(filename)


def load_model_weights(model, filename="model_weights.h5"):
    model.load_weights(filename)


def loading_file_for_training():
    import json
    import random
    with open("saved_self_play.json", "r") as jfile:
        # dataset = json.load(jfile)
        selected_samples = json.load(jfile)
    model = nn_model()

    value_loss = keras.losses.MeanSquaredError()  # Change?
    policy_loss = keras.losses.CategoricalCrossentropy()  # Change?
    metrics = ['accuracy']  # change?
    length = len(selected_samples) // 4
    selected_samples = random.sample(selected_samples, length)
    # dataset = [-500000:]
    # selected_samples = random.sample(dataset, 2048)
    inputs = np.array([np.asarray(sample[0], dtype=np.float32) for sample in selected_samples])
    outputs = {'dense_2': np.array([sample[2] for sample in selected_samples]),
               'softmax': np.array([sample[1] for sample in selected_samples])}
    model.compile(optimizer='adam', loss={'dense_2': value_loss, 'softmax': policy_loss}, metrics={'softmax': metrics})

    model.fit(inputs, outputs, epochs=10, batch_size=32)
    save_model_weights(model)
