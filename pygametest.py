import pygame
import math
import random
import PySimpleGUI as sg
from uifunctions import hex_ui_setup
import goclasses


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


class HexGo(goclasses.GoBoard):  # make it inherit from the goclasses.py class
    def __init__(self, window, screen, radius=60, circ_rad=15, side_length=6, baseboard_size=17, defaults=True):
        super().__init__(board_size=baseboard_size, defaults=defaults)
        self.radius = radius
        self.circ_rad = circ_rad
        self.side_length = side_length
        self.pysg_window = window
        self.pygame_screen = screen
        self.nodes_set = set()
        self.nodes_dict = dict()
        self.board_array = [[]]*(2*side_length-1)

    def generate_board(self, start_point):
        self.generate_row(self.side_length - 1, (self.side_length * 2) - 1, start_point, False)
        self.generate_board_helper(-30, True, start_point)
        self.generate_board_helper(150, False, start_point)

    def generate_board_helper(self, angle_deg, up, start_point):
        for idx in range(1, self.side_length):
            angle_rad = math.pi / 180 * angle_deg
            y_val = start_point[1] - idx * self.radius * math.cos(angle_rad)
            if up:
                x_val = start_point[0] - idx * self.radius * math.sin(angle_rad)
                self.generate_row((self.side_length - 1) - idx, (self.side_length * 2) - 1 - idx, (x_val, y_val), True, True)
            if not up:
                x_val = start_point[0] + idx * self.radius * math.sin(angle_rad)
                self.generate_row((self.side_length - 1) + idx, (self.side_length * 2) - 1 - idx, (x_val, y_val), True, False)

    def generate_row(self, row_number, length, starting_spot, setup_connections, above=None):
        templist = list()
        for idx in range(length):
            temp = HexNode(row_number, idx, starting_spot[0] + idx * self.radius, starting_spot[1])
            self.nodes_set.add(temp)
            templist.append(temp)
            self.nodes_dict[f"{row_number}{idx}"] = temp
            if setup_connections and above:
                modifiers_above = [(0, -1), (1, 0), (1, 1)]
                for mod in modifiers_above:
                    self.adding_neighbors(temp, mod, row_number, idx)

            elif setup_connections and not above:
                modifiers_below = [(0, -1), (-1, 0), (-1, 1)]
                for mod in modifiers_below:
                    self.adding_neighbors(temp, mod, row_number, idx)
            elif not setup_connections:
                mod = (0, -1)
                self.adding_neighbors(temp, mod, row_number, idx)
        self.board_array[row_number] = list(templist)

    def adding_neighbors(self, temp, mod, row_number, idx):
        temp_spot = (row_number + mod[0], idx + mod[1])
        if f"{temp_spot[0]}{temp_spot[1]}" in self.nodes_dict.keys():
            x = self.nodes_dict[f"{temp_spot[0]}{temp_spot[1]}"]
            x.neighbors[f"{row_number}{idx}"] = temp
            temp.neighbors[f"{temp_spot[0]}{temp_spot[1]}"] = x

    def find_circle(self, input_location):
        for item in self.nodes_set:
            item_location = [item.screen_x, item.screen_y]
            if math.dist(input_location, item_location) <= self.circ_rad:
                item.stone_here_color = (238, 75, 43)
                pygame.draw.circle(self.pygame_screen, (238, 75, 43), (item.screen_x, item.screen_y), self.circ_rad)
                # ^change color when players are added
                pygame.display.flip()
                return True


def get_random_colour(min_=150, max_=255):
    vx = tuple(random.choices(list(range(min_, max_)), k=3))
    return vx


def setup_pygame_board(window):
    screen = pygame.display.set_mode((700, 700))
    while True:  # For some reason this is required
        event, values = window.read(timeout=10)
        pygame.display.update()
        break
    screen.fill(pygame.Color(110, 162, 170))
    pygame.display.init()
    pygame.display.update()

    hex_game = HexGo(window, screen)
    hex_game.generate_board((50, 350))
    for item in hex_game.nodes_set:
        for neighbor in item.neighbors.values():
            pygame.draw.line(screen, (0, 0, 0), (item.screen_x, item.screen_y), (neighbor.screen_x, neighbor.screen_y))

    for item in hex_game.nodes_set:
        pygame.draw.circle(screen, get_random_colour(), (item.screen_x, item.screen_y), hex_game.circ_rad)
    pygame.display.flip()
    return hex_game


def main():
    window = hex_ui_setup()
    hex_game = setup_pygame_board(window)

    while True:  # eventually should be eaten by the pysimplegui from main/goclasses.py
        event, values = window.read()
        if event in (sg.WIN_CLOSED, 'Exit Game'):
            quit()

        elif event == '-GRAPH-':
            temp = values['-GRAPH-']
            hex_game.find_circle([temp[0], temp[1]])
            #output,  =hex_game.find_piece_click([temp[0], temp[1]])
            pygame.display.flip()
        pygame.display.update()
    pygame.display.quit()


# main()
