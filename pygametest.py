import pygame
import math
import random
from typing import Tuple
import PySimpleGUI as sg
import os
import platform

RADIUS = 80
CIRC_RAD = 20


class HexNode():
    def __init__(self, row_value=None, col_value=None, screen_x_value=None, screen_y_value=None):
        self.row = row_value
        self.col = col_value
        self.screen_x = screen_x_value
        self.screen_y = screen_y_value
        self.stone_here_color = (120, 120, 120)
        self.neighbors = dict()

    def __str__(self):
        return (f"This is a BoardNode with coordinates of ({self.row},{self.col}),\
        and a board placement of ({self.screen_x},{self.screen_y})")  # and a stone of {self.stone_here_color}")

    # Allows for updating a specific variable in the HexNode class
    def change_boardnode_value(self, class_value, value):
        if hasattr(self, class_value):
            setattr(self, class_value, value)
        else:
            print("No attribute for that")


# longest one for a board of sidelength 6 is 11 (6*2-1)

def generate_board(side_length, start_point):
    nodes_set = set()
    nodes_dict = dict()
    generate_row(side_length - 1, (side_length * 2) - 1, start_point, nodes_set, nodes_dict, False)
    generate_board_helper(side_length, -30, True, nodes_set, nodes_dict, start_point)
    generate_board_helper(side_length, 150, False, nodes_set, nodes_dict, start_point)
    return (nodes_set, nodes_dict)


def generate_board_helper(side_length, angle_deg, up, nodes_set, nodes_dict, start_point):
    for idx in range(1, side_length):
        angle_rad = math.pi / 180 * angle_deg
        y_val = start_point[1] - idx * RADIUS * math.cos(angle_rad)
        if up:
            x_val = start_point[0] - idx * RADIUS * math.sin(angle_rad)
            generate_row((side_length - 1) - idx, (side_length * 2) - 1 - idx, (x_val, y_val), nodes_set, nodes_dict, True, True)
        if not up:
            x_val = start_point[0] + idx * RADIUS * math.sin(angle_rad)
            generate_row((side_length - 1) + idx, (side_length * 2) - 1 - idx, (x_val, y_val), nodes_set, nodes_dict, True, False)


def generate_row(row_number, length, starting_spot, nodes_set, nodes_dict, setup_connections, above=None):
    for idx in range(length):
        temp = HexNode(row_number, idx, starting_spot[0] + idx * RADIUS, starting_spot[1])
        nodes_set.add(temp)
        nodes_dict[f"{row_number}{idx}"] = temp
        if setup_connections and above:
            modifiers_above = [(0, -1), (1, 0), (1, 1)]
            for mod in modifiers_above:
                adding_neighbors(temp, mod, row_number, idx, nodes_dict)

        elif setup_connections and not above:
            modifiers_below = [(0, -1), (-1, 0), (-1, 1)]
            for mod in modifiers_below:
                adding_neighbors(temp, mod, row_number, idx, nodes_dict)
        elif not setup_connections:
            mod = (0, -1)
            adding_neighbors(temp, mod, row_number, idx, nodes_dict)


def adding_neighbors(temp, mod, row_number, idx, nodes_dict):
    temp_spot = (row_number + mod[0], idx + mod[1])
    if f"{temp_spot[0]}{temp_spot[1]}" in nodes_dict.keys():
        x = nodes_dict[f"{temp_spot[0]}{temp_spot[1]}"]
        x.neighbors[f"{row_number}{idx}"] = temp
        temp.neighbors[f"{temp_spot[0]}{temp_spot[1]}"] = x


def pointy_hex_corner(center, size, i):
    angle_deg = 60 * i - 90
    angle_rad = math.pi / 180 * angle_deg
    return (center[0] + size * math.cos(angle_rad),
            center[1] + size * math.sin(angle_rad))


def get_random_colour(min_=150, max_=255) -> Tuple[int, ...]:
    vx = tuple(random.choices(list(range(min_, max_)), k=3))
    return vx


def find_circle(screen, input_location, nodes):
    for item in nodes:
        item_location = [item.screen_x, item.screen_y]
        if math.dist(input_location, item_location) <= CIRC_RAD:
            item.stone_here_color = (238, 75, 43)
            pygame.draw.circle(screen, (238, 75, 43), (item.screen_x, item.screen_y), CIRC_RAD)
            pygame.display.flip()
            print(item_location)
            return True


def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    clock = pygame.time.Clock()
    # screen.fill((200, 162, 200))
    screen.fill((120, 120, 120))
    nodes = generate_board(6, (100, 500))

    for item in nodes[0]:
        for neighbor in item.neighbors.values():
            pygame.draw.line(screen, (0, 0, 0), (item.screen_x, item.screen_y), (neighbor.screen_x, neighbor.screen_y))

    for item in nodes[0]:
        pygame.draw.circle(screen, get_random_colour(), (item.screen_x, item.screen_y), CIRC_RAD)
    print(f"this is the length {len(nodes[0])}")

    pygame.display.flip()
    terminated = False
    while not terminated:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                temp = event.dict["pos"]
                location = [temp[0], temp[1]]
                find_circle(screen, location, nodes[0])
            elif event.type == pygame.QUIT:
                terminated = True

        clock.tick(50)
    pygame.display.quit()


# https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_PyGame_Integration.py
layout = [[sg.Text('Test of PySimpleGUI with PyGame')],
          [sg.Graph((800, 800), (800, 0), (0, 800),
                    background_color='lightblue', key='-GRAPH-', enable_events=True)],
          [sg.Button('Draw'), sg.Exit()]]

window = sg.Window('PySimpleGUI + PyGame', layout, finalize=True)
graph = window['-GRAPH-']

embed = graph.TKCanvas
os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
if platform.system == "Linux":
    os.environ['SDL_VIDEODRIVER'] = "x11"
elif platform.system == "Windows":
    os.environ['SDL_VIDEODRIVER'] = 'windib'

screen = pygame.display.set_mode((800, 800))
pygame.display.init()
pygame.display.update()
while True:
    event, values = window.read(timeout=10)
    pygame.display.update()
    break

screen.fill(pygame.Color(200, 162, 200))
clock = pygame.time.Clock()
pygame.display.init()
pygame.display.update()
nodes = generate_board(6, (100, 500))

for item in nodes[0]:
    for neighbor in item.neighbors.values():
        pygame.draw.line(screen, (0, 0, 0), (item.screen_x, item.screen_y), (neighbor.screen_x, neighbor.screen_y))

for item in nodes[0]:
    pygame.draw.circle(screen, get_random_colour(), (item.screen_x, item.screen_y), CIRC_RAD)
print(f"this is the length {len(nodes[0])}")

pygame.display.flip()


while True:
    event, values = window.read()
    print(event)
    print(values)
    print(type(event))
    print(type(values))
    if event in (sg.WIN_CLOSED, 'Exit'):
        print("tried to quit uwu")
        #pygame.display.quit()
        break
    
    elif event == '-GRAPH-':

        temp = values['-GRAPH-']
        print(temp)
        print(type(temp))
        location = [temp[1], temp[0]]
        print(location)
        print('lets go')
        find_circle(screen, location, nodes[0])
        pygame.display.flip()
    pygame.display.update()

    clock.tick(50)
pygame.display.quit()