import re
import sys
from itertools import permutations
import functools

class Vector:
    def __init__(self, x, y, z):
        self.x = int(x)
        self.y = int(y)
        self.z = int(z)

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z

        return Vector(x, y, z)

    def __sub__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z

        return Vector(x, y, z)

class Position(Vector):
    def __init__(self, x=0, y=0, z=0):
        super().__init__(x, y, z)

class Velocity(Vector):
    def __init__(self, x=0, y=0, z=0):
        super().__init__(x, y, z)

class Moon:
    def __init__(self, position, velocity):
        self.position = position
        self.starting_position = None
        self.velocity = velocity

    def __str__(self):
        pos_x = self.position.x
        pos_y = self.position.y
        pos_z = self.position.z
        vel_x = self.velocity.x
        vel_y = self.velocity.y
        vel_z = self.velocity.z
        return "pos=<x={:2d}, y={:2d}, z={:2d}>, vel=<x={:2d}, y={:2d}, z={:2d}>".format(pos_x, pos_y, pos_z, vel_x, vel_y, vel_z)

    def __get_potential_energy(self):
        return abs(self.position.x) + abs(self.position.y) + abs(self.position.z)

    def __get_kinetic_energy(self):
        return abs(self.velocity.x) + abs(self.velocity.y) + abs(self.velocity.z)

    def get_total_energy(self):
        return self.__get_potential_energy() * self.__get_kinetic_energy()

    def set_position(self, position_element):
        matches = re.match(r"<x=(-?\d+), y=(-?\d+), z=(-?\d+)>", position_element)
        x = int(matches.group(1))
        y = int(matches.group(2))
        z = int(matches.group(3))
        self.position.x = x
        self.position.y = y
        self.position.z = z
        self.starting_position = Position(x, y, z)

    def update_velocity_from_other_moon_on_axis(self, axis, self_axis_position, other_axis_position):
        """
        Updates the velocity of this moon based on the axis given.
        """
        if self_axis_position < other_axis_position:
            setattr(
                self.velocity, axis, getattr(self.velocity, axis) + 1
            )
        elif self_axis_position > other_axis_position:
            setattr(
                self.velocity, axis, getattr(self.velocity, axis) - 1
            )

    def update_velocity_from_other_moon_gravity(self, other, dimension=None):
        """
        Updates our moon's entire velocity based on the gravitational pull
        of another moon
        """
        self.update_velocity_from_other_moon_on_axis('x', self.position.x, other.position.x)
        self.update_velocity_from_other_moon_on_axis('y', self.position.y, other.position.y)
        self.update_velocity_from_other_moon_on_axis('z', self.position.z, other.position.z)

    def apply_velocity_to_position(self):
        self.position.x += self.velocity.x
        self.position.y += self.velocity.y
        self.position.z += self.velocity.z

    def at_starting_position(self):
        isVelocityZero = self.velocity.x == 0 and self.velocity.y == 0 and self.velocity.z == 0
        isStartingPosition = (
            self.position.x == self.starting_position.x and
            self.position.y == self.starting_position.y and
            self.position.z == self.starting_position.z )

        return ( isVelocityZero and isStartingPosition )

def print_moons(moons):
    print("*" * 20)
    for moon in moons:
        print(moon)
    print("*" * 20)
    print("\n")

def greatest_common_divisor(a, b):
    """
    Euclid's Algorithm
    """
    if b == 0:
        return a
    return greatest_common_divisor(b, a % b)

def least_common_multiple(a, b):
    if a == 0 or b == 0:
        return 0
    return int((a * b) / greatest_common_divisor(a, b))

if __name__ == "__main__":
    try:
        num_of_time_steps = int(sys.argv[1])
    except:
        num_of_time_steps = 10

    time_step = 0

    with open('input.txt', 'r') as f:
        example_scan = f.read()

    moons = []
    dimensional_time_steps = []
    for moon_position in example_scan.split("\n"):
        moon = Moon(Position(), Velocity())
        moon.set_position(moon_position)
        moons += [ moon ]

    for dimension in ['x', 'y', 'z']:
        time_step = 0
        simulation_started = False
        while True:
            for moon_permutation in permutations(moons, 2):
                moon_1 = moon_permutation[0]
                moon_2 = moon_permutation[1]
                moon_1_dimension_position = getattr(moon_1.position, dimension)
                moon_2_dimension_position = getattr(moon_2.position, dimension)

                moon_1.update_velocity_from_other_moon_on_axis(dimension, moon_1_dimension_position, moon_2_dimension_position )

            for moon in moons:
                moon.apply_velocity_to_position()

            time_step += 1

            if all([ moon.at_starting_position() for moon in moons ]):
                break

        dimensional_time_steps += [ time_step ]

    total_num_steps = functools.reduce(
        lambda a, b: least_common_multiple(a, b),
        dimensional_time_steps,
        1
    )

    print(total_num_steps)

    # Simulate motion
    # while True:
    #     for moon_permutation in permutations(moons, 2):
    #         moon_1 = moon_permutation[0]
    #         moon_2 = moon_permutation[1]

    #         moon_1.update_velocity_from_other_moon_gravity(moon_2)

    #     for moon in moons:
    #         moon.apply_velocity_to_position()

    #     time_step += 1

    # total_energy_in_system = functools.reduce(
    #     lambda sum, moon: sum + moon.get_total_energy(),
    #     moons,
    #     0
    # )

    # print(f"Total Energy in System {total_energy_in_system}")
    # print(f"Total Time Step: {time_step}")