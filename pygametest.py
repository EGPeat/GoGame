import pygame
import math
import random
from typing import Tuple

radius = 80


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
    generate_row(side_length-1, (side_length*2)-1, start_point, nodes_set, nodes_dict, False)
    for idx in range(1, side_length):  # upwards
        angle_deg = -30
        angle_rad = math.pi / 180 * angle_deg
        y_val = start_point[1] - idx * radius * math.cos(angle_rad)
        x_val = start_point[0] - idx * radius * math.sin(angle_rad)
        generate_row((side_length-1)-idx, (side_length*2)-1-idx, (x_val, y_val), nodes_set, nodes_dict, True, True)
    for idx in range(1, side_length):  # downwards
        angle_deg = 150
        angle_rad = math.pi / 180 * angle_deg
        y_val = start_point[1] - idx * radius * math.cos(angle_rad)
        x_val = start_point[0] + idx * radius * math.sin(angle_rad)
        generate_row((side_length-1)+idx, (side_length*2)-1-idx, (x_val, y_val), nodes_set, nodes_dict, True, False)
    return (nodes_set, nodes_dict)


def generate_row(row_number, length, starting_spot, nodes_set, nodes_dict, setup_connections, above=None):
    for idx in range(length):
        temp = HexNode(row_number, idx, starting_spot[0]+idx*radius, starting_spot[1])
        nodes_set.add(temp)
        nodes_dict[f"{row_number}{idx}"] = temp
        if setup_connections and above:
            modifiers_above = [(0, -1), (1, 0), (1, 1)]
            for mod in modifiers_above:
                temp_spot = (row_number + mod[0], idx + mod[1])
                if f"{temp_spot[0]}{temp_spot[1]}" in nodes_dict.keys():
                    x = nodes_dict[f"{temp_spot[0]}{temp_spot[1]}"]
                    x.neighbors[f"{row_number}{idx}"] = temp
                    temp.neighbors[f"{temp_spot[0]}{temp_spot[1]}"] = x

        elif setup_connections and not above:
            modifiers_below = [(0, -1), (-1, 0), (-1, 1)]
            for mod in modifiers_below:
                temp_spot = (row_number + mod[0], idx + mod[1])
                if f"{temp_spot[0]}{temp_spot[1]}" in nodes_dict.keys():
                    x = nodes_dict[f"{temp_spot[0]}{temp_spot[1]}"]
                    x.neighbors[f"{row_number}{idx}"] = temp
                    temp.neighbors[f"{temp_spot[0]}{temp_spot[1]}"] = x
        elif not setup_connections:
            modifier = (0, -1)
            temp_spot = (row_number + modifier[0], idx + modifier[1])
            if f"{temp_spot[0]}{temp_spot[1]}" in nodes_dict.keys():
                x = nodes_dict[f"{temp_spot[0]}{temp_spot[1]}"]
                x.neighbors[f"{row_number}{idx}"] = temp
                temp.neighbors[f"{temp_spot[0]}{temp_spot[1]}"] = x


def pointy_hex_corner(center, size, i):
    angle_deg = 60 * i - 90
    angle_rad = math.pi / 180 * angle_deg
    return (center[0] + size * math.cos(angle_rad),
            center[1] + size * math.sin(angle_rad))


def make_hex_coords(center):
    list_before = list()
    for i in range(6):
        temp = pointy_hex_corner(center, radius, i)
        list_before.append(temp)
    return tuple(list_before)


def get_random_colour(min_=150, max_=255) -> Tuple[int, ...]:
    vx = tuple(random.choices(list(range(min_, max_)), k=3))
    return vx


def multiple_hexagons(screen, point, amount):
    for num in range(amount):
        vertex_tuple = make_hex_coords((point[0]+(num*radius*math.sqrt(3)), point[1]))
        pygame.draw.polygon(screen, get_random_colour(), vertex_tuple)
        pygame.draw.lines(screen, (0, 0, 0), True, vertex_tuple, 4)


def multiple_circles(screen, point, amount):
    for num in range(amount):
        current_point = (point[0]+(num*(radius*2)), point[1])
        last_point = (point[0]+((num-1)*(radius*2)), point[1])
        if num > 0:
            pygame.draw.line(screen, (0, 0, 0), current_point, last_point)
    for num in range(amount):
        current_point = (point[0]+(num*(radius*2)), point[1])
        pygame.draw.circle(screen, get_random_colour(), current_point, 10)


def circle_hex(screen, point):
    vertex_tuple = make_hex_coords((point[0], point[1]))
    for idx, vert in enumerate(vertex_tuple):
        pygame.draw.line(screen, (0, 0, 0), point, vert, 5)
        pygame.draw.circle(screen, get_random_colour(), vert, 10)
    pygame.draw.circle(screen, get_random_colour(), point, 10)


def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000))
    clock = pygame.time.Clock()
    # screen.fill((200, 162, 200))
    screen.fill((120, 120, 120))
    nodes = generate_board(6, (100, 500))

    for item in nodes[0]:
        print(item)
        print(type(item))
        print(item.neighbors)
        for neighbor in item.neighbors.values():
            print(neighbor)
            pygame.draw.line(screen, (0, 0, 0), (item.screen_x, item.screen_y), (neighbor.screen_x, neighbor.screen_y))

    for item in nodes[0]:
        pygame.draw.circle(screen, get_random_colour(), (item.screen_x, item.screen_y), 20)
    print(f"this is the length {len(nodes[0])}")
    # multiple_hexagons(screen, (400, 400), 4)
    # multiple_circles(screen, (400, 400), 4)
    # circle_hex(screen, (400, 400))
    pygame.display.flip()
    terminated = False
    while not terminated:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminated = True

        clock.tick(50)
    pygame.display.quit()


main()
