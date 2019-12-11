from enum import IntEnum
from math import pi, atan, sqrt
from collections import deque

FULL_CIRCLE = round(2 * pi, 3)
HALF_CIRCLE = round(FULL_CIRCLE / 2, 3)
QUARTER_CIRCLE = round(HALF_CIRCLE / 2, 3)

def get_angle_reference_point(distance_x, distance_y):
    '''
    We use these references to get the actual angle of another asteroid
    from 0 to 2*pi
    '''
    if distance_x < 0 and distance_y >= 0:
        angle_reference = HALF_CIRCLE + QUARTER_CIRCLE
    elif distance_x <= 0 and distance_y < 0:
        angle_reference = HALF_CIRCLE
    elif distance_x > 0 and distance_y <= 0:
        angle_reference = QUARTER_CIRCLE
    else:
        angle_reference = 0

    return angle_reference

class Position:
    '''
    Position Of An Asteroid
    '''
    def __init__(self, x, y):
        self.x = x
        self.y = y

"""
Radians Only
"""
class Laser:
    def __init__(self, rotation=0,rotation_step=0.001,rotation_direction="ccw"):
        self.rotation_direction = rotation_direction
        self.rotation = 0
        self.rotation_step = rotation_step
        self.rounding_decimals = len(str(rotation_step).split(".")[1])

    def set_rotation(self, rotation):
        self.rotation = round(rotation, self.rounding_decimals)

    def rotate_one_step(self):
        if self.rotation_direction == "ccw" and (self.rotation - self.rotation_step == -self.rotation_step):
            self.set_rotation(FULL_CIRCLE)

        if self.rotation_direction == "cw" and (self.rotation + self.rotation_step > round(FULL_CIRCLE, self.rounding_decimals) + self.rotation_step):
            self.set_rotation(0)

        self.rotation
        change_in_rotation = -self.rotation_step if self.rotation_direction == "ccw" else self.rotation_step

        # Move rotation rotation by one step
        self.set_rotation( self.rotation + change_in_rotation)

def square( num ):
    return num * num

class Asteroid:
    def __init__(self, position):
        self.position = position

    def __str__(self):
        return "Asteroid: [ {pos_x}, {pos_y} ]".format(pos_x=self.position.x, pos_y=self.position.y)

    def __sub__(self, other):
        return tuple([
            self.position.x - other.position.x,
            self.position.y - other.position.y
        ])

    def distance_to(self, other):
        distance_x, distance_y = self - other
        return sqrt(square(distance_x) + square(distance_y))

    def find_angle_between_another_asteroid(self, other):
        '''
        From the relative position of this asteroid (i.e. self).
        Find the counterclockwise angle between
        '''
        diff_x, diff_y = self - other
        rounding_num = 3
        angle_reference_point = get_angle_reference_point(diff_x, diff_y)

        '''
        When we reference an asteroid against itself
        '''
        if diff_x == 0 and diff_y == 0:
            return "X"

        angle_between_asteroids = 0

        if diff_x != 0 and diff_y != 0:
            angle_between_asteroids = abs(atan(diff_x/diff_y))

            #bottom left or bottom right diagonal
            if (diff_x > 0 and diff_y < 0) or (diff_x < 0 and diff_y > 0):
                angle_between_asteroids = abs(atan(diff_y/diff_x))

        return round(angle_between_asteroids + angle_reference_point, rounding_num)

def get_asteroids(asteroid_map):
    '''
    Given an asteroid map, build and return all of the asteroids in that map.

    @return array
    '''
    asteroids = []
    asteroid_map = asteroid_map.split("\n") if isinstance(asteroid_map, str) else asteroid_map
    for y_pos, row in enumerate(asteroid_map):
        for x_pos, column in enumerate(row):
            current_position = Position(x_pos, y_pos)
            if column == "#":
                asteroids += [ Asteroid(current_position) ]

    return asteroids

def build_relative_angle_mappings_from_asteroid(asteroid, asteroids):
    return [ asteroid.find_angle_between_another_asteroid(relative_asteroid) for relative_asteroid in asteroids ]

def build_relative_angle_mappings_from_asteroids(asteroids):
    '''
    Builds a relative angle array from one asteroid to all the other asteroids.
    On^2 time
    '''
    angle_mappings = []
    for asteroid in asteroids:
        angle_mappings += [ build_relative_angle_mappings_from_asteroid(asteroid, asteroids) ]

    return angle_mappings

def map_angle_mapping_to_asteroid_map( angle_mapping, asteroid_map ):
    '''
    Given an angle mapping array and a full map, insert the given angle mappings over
    the asteroids in the asteroid.

    Display specific function
    '''
    relative_asteroid_angle_queue = deque(angle_mapping)
    copied_map = [list(row) for row in parse_asteroid_map(asteroid_map)]

    for row_num, row in enumerate(copied_map):
        for column_num, column in enumerate(row):
            if column == "#":
                copied_map[row_num][column_num] = str(relative_asteroid_angle_queue.popleft())

    return copied_map

def map_all_angle_mappings_to_asteroid_map( angle_mappings, asteroid_map ):
    return [ map_angle_mapping_to_asteroid_map(angle_mapping, asteroid_map) for angle_mapping in angle_mappings ]


def parse_asteroid_map(asteroid_map):
    return [list(row) for row in asteroid_map.split("\n")]

def get_num_asteroids_visible_from_asteroid(asteroid_map):
    '''
    Returns a list of tuples which contain the asteroid and the number of asteroids visible from that asteroid
    '''
    asteroids = get_asteroids(asteroid_map)
    visibility_map = []
    for asteroid in asteroids:
        angles_between_asteroids = set([ asteroid.find_angle_between_another_asteroid(other_asteroid) for other_asteroid in asteroids ])
        visibility_map += [ tuple([ asteroid, len([angle for angle in angles_between_asteroids if angle != "X" ])])]

    return visibility_map

def get_asteroid_with_max_num_asteroids_visible( asteroid_map ):
    return max(get_num_asteroids_visible_from_asteroid(asteroid_map), key=lambda item: item[1])

def print_asteroid_relative_angle_map_at_asteroid(asteroid, asteroids, map):
    print_asteroid_map(map_angle_mapping_to_asteroid_map(build_relative_angle_mappings_from_asteroid(asteroid, asteroids), map))

def print_asteroid_map(parsed_asteroid_map):
    '''
    Print a map with specific formatting based on the numbers we are outputting
    '''
    for row in parsed_asteroid_map:
        for column in row:
            print("{:^6}".format(column), end="")
        print("\n")
    return True

def print_asteroid_maps(parsed_asteroid_maps):
    for asteroid_map in parsed_asteroid_maps:
        print("*" * 15)
        print_asteroid_map(asteroid_map)
        print("*" * 15)
    return True

def get_asteroids_at_angle( angle, relative_asteroid_angles, asteroids ):
    asteroids_at_angle = []
    for index, asteroid in enumerate(asteroids):

        asteroid_angle = relative_asteroid_angles[index]

        if angle == asteroid_angle:
            asteroids_at_angle += [ asteroid ]

    return asteroids_at_angle

def destroy_closest_asteroid( mounted_asteroid, asteroids, asteroid_map ):

    def find_closest_asteroid():
        closest_distance = None
        closest_asteroid = None
        for asteroid in asteroids:
            distance_between_mounted = mounted_asteroid.distance_to(asteroid)
            if closest_distance is None or distance_between_mounted < closest_distance:
                closest_asteroid = asteroid
                closest_distance = distance_between_mounted

        return closest_asteroid

    closest_asteroid = find_closest_asteroid()
    if closest_asteroid is None:
        return None

    asteroid_map[closest_asteroid.position.y][closest_asteroid.position.x] = '.'

    return closest_asteroid

# def print_asteroid_map_for_specific_asteroid()
def fire_lasers_until_nth_asteroid( mounted_asteroid, asteroid_map, n=200 ):
    laser = Laser()
    asteroid_map = parse_asteroid_map(asteroid_map)
    asteroid_destruction_count = 0

    while True:
        laser_rotation = laser.rotation

        current_asteroids = get_asteroids(asteroid_map)
        relative_asteroid_angles = build_relative_angle_mappings_from_asteroid(mounted_asteroid, current_asteroids)
        asteroids_at_angle = get_asteroids_at_angle(laser_rotation, relative_asteroid_angles, current_asteroids)
        destroyed_asteroid = destroy_closest_asteroid(mounted_asteroid, asteroids_at_angle, asteroid_map)

        if destroyed_asteroid is not None:
            asteroid_destruction_count += 1

        if asteroid_destruction_count == n:
            return destroyed_asteroid

        laser.rotate_one_step()

if __name__ == '__main__':
    with open('ex_1.txt', 'r') as f:
        test_file_1 = f.read()
        print(get_asteroid_with_max_num_asteroids_visible(test_file_1))
    with open('ex_2.txt', 'r') as f:
        test_file_2 = f.read()
        print(get_asteroid_with_max_num_asteroids_visible(test_file_2))
    with open('ex_3.txt', 'r') as f:
        test_file_3 = f.read()
        print(get_asteroid_with_max_num_asteroids_visible(test_file_3))
    with open('ex_4.txt', 'r') as f:
        test_file_4 = f.read()
        print(get_asteroid_with_max_num_asteroids_visible(test_file_4))
    with open('ex_5.txt', 'r') as f:
        test_file_5 = f.read()
        print(get_asteroid_with_max_num_asteroids_visible(test_file_5))
    with open('input.txt', 'r') as f:
        file = f.read()
        main_asteroid = get_asteroid_with_max_num_asteroids_visible(file)[0]
        print(fire_lasers_until_nth_asteroid(main_asteroid, file))



    # print(get_num_asteroids_visible_from_asteroid(test_file_1))


