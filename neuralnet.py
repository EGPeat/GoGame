import goclasses as go
import uifunctions as ui
import PySimpleGUI as sg
import pygametest as pygt

# This setup for the neuralnet has it making a pysimplegui window and etc. It's not necessary, but would take extra work to fix.
# Fix it eventually


def training_run(window):
    temp = go.initializing_game(window, 9, True, vs_bot=True, ai_training=True, no_window=True)
    print(len(temp))
    print(len(temp[0]))
    print("\n\n")
    #print(temp)
    return temp


def training_cycle(window):
    info_for_ai = []
    length = 25
    sum_val = 0
    for _ in range(length):
        info_for_ai.append(training_run(window))
        if info_for_ai[-1][1] == 1:
            sum_val += 1
    
    print(f"the amount is {sum_val} out of {length} games or a win percentage of {sum_val/length}")