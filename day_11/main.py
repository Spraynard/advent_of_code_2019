from intcode_computer import IntcodeComputer
from enum import Enum, IntEnum
import os
from time import sleep

class RobotMode(Enum):
    GROUNDING = 1
    PAINTING = 2
    MOVING = 3

class Color(IntEnum):
    BLACK = 0
    WHITE = 1

class Rotations(IntEnum):
    LEFT = 0
    RIGHT = 1

class Orientations(IntEnum):
    UP = 0
    LEFT = -90
    RIGHT = 90
    DOWN = 180

class Robot:
    def __init__(self):
        self.position = [0,0]
        self.orientation = 0 #in degrees

    def relay_current_location_information(self, computer, colors):
        color_at_location = self.ground(colors)
        computer.set_input_queue([color_at_location])

    '''Takes in location colors and returns color based on current location'''
    def ground(self, colors):
        position = make_position_string(self.position)
        color_at_position = colors[position] if position in colors else int(Color.BLACK)
        return color_at_position

    '''Takes in location colors and returns another location colors dictionary based on current position'''
    def paint(self, color, colors):
        copies = colors.copy()
        position = make_position_string(self.position)
        copies[position] = color
        return copies

    def rotate_in_direction( self, rotation ):
        if rotation == Rotations.LEFT:
            self.orientation -= 90
        else:
            self.orientation += 90

        if abs(self.orientation) == 360:
            self.orientation = 0
        elif self.orientation == -270:
            self.orientation = 90
        elif self.orientation == 270:
            self.orientation = -90

        return True

    def move_forward(self):
        if self.orientation == Orientations.UP:
            self.position = [self.position[0], self.position[1] + 1]
        elif abs(self.orientation) == Orientations.DOWN:
            self.position = [self.position[0], self.position[1] - 1]
        elif self.orientation == Orientations.LEFT:
            self.position = [self.position[0] - 1, self.position[1]]
        else:
            self.position = [self.position[0] + 1, self.position[1]]

        return True

    def move(self, direction):
        self.rotate_in_direction(direction)
        self.move_forward()

def replaceMultiple(mainString, toBeReplaces, newString):
    # Iterate over the strings to be replaced
    for elem in toBeReplaces :
        # Check if string is in the main string
        if elem in mainString :
            # Replace the string
            mainString = mainString.replace(elem, newString)

    return  mainString

def print_location_colors( location_colors ):
    # find the max x and y
    os.system('clear')
    locations = [ [int(position_val) for position_val in location.split(",")] for location in location_colors.keys() ]
    min_width = min(locations, key=lambda location: location[0])[0]
    min_height = min(locations, key=lambda location: location[1])[1]

    max_width = max(locations, key=lambda location: location[0])[0]
    max_height = max(locations, key=lambda location: location[1])[1]

    for y_val in range(max_height, min_height - 1, -1):
        for x_val in range(min_width, max_width + 1):
            position = make_position_string([x_val, y_val])
            output_value = "#" if position in location_colors and location_colors[position] == 1 else "."
            print(output_value, end=" ")
        print("\n")

def make_position_string( position_array ):
    if position_array is None:
        return None
    return str(position_array[0]) + "," + str(position_array[1])

if __name__ == "__main__":
    with open('input.txt', 'r') as f:
        instructions = f.read()

    current_robot_mode = RobotMode.GROUNDING
    location_colors = { "0,0" : int(Color.WHITE) }
    robot_locations = set([]) # Locations of where our robot has been
    computer = IntcodeComputer(instructions, True, True, True, False, True, False)
    robot = Robot()
    at_least_once_paint_count = 1
    while True:
        # print(location_colors)
        # p`rint_location_colors(location_colors)
        # Inputting current location into robot computer
        robot.relay_current_location_information(computer, location_colors)

        # Get the output from the robot's computer
        robot_panel_color_output = computer.process_intcode()
        robot_movement_direction_output = computer.process_intcode()

        paint_position = make_position_string(robot.position)

        if paint_position is not None and paint_position not in location_colors:
            at_least_once_paint_count += 1

        location_colors = robot.paint(robot_panel_color_output, location_colors)
        robot.move(robot_movement_direction_output)

        if ( robot_panel_color_output is None or robot_movement_direction_output is None ):
            break
        # sleep(0.15)
    print(f"At least once paint count: {at_least_once_paint_count}")
    print_location_colors(location_colors)
