import sys
import enum
import os
import resource
from time import sleep
from collections import deque
import copy
sys.path.append("..")
sys.setrecursionlimit(1000000)
# resource.setrlimit(resource.RLIMIT_STACK, [0x10000000, resource.RLIM_INFINITY])
# sys.setrecursionlimit(0x100000)

from general.position import Position, Positioned
from general.intcode_computer.main import IntcodeComputer

"""
Going to try and solve this by creating a movement tree where node
is a movement command and a robot that processes that command.

Most likely this is pretty close to Djitska's, but worse written.

"""
class MovementCommand(enum.IntEnum):
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4

class MoveStatus(enum.IntEnum):
    WALL = 0
    SUCCESS = 1
    OXYGEN = 2

class RobotComputer(IntcodeComputer):
    def __init__(self, memory):
        super().__init__(memory, True, True, True)

class Node():
    def __init__(self, key, value):
        self.key = key
        self.value = value
        self.parent = None
        self.children = []

    def setParent(self, node):
        self.parent = node
        return True

class Robot(Node):
    """
    The response code from intcode computer will be the key
    The position will be the value
    """
    def __init__(self, position, memory, distance = 0,command = None, computer = None, computerClass = RobotComputer):
        super().__init__(None, position)
        self.memory = memory
        self.computer = computer or computerClass(memory)
        self.command = command if command is None else int(command)
        self.distance = distance
        self.movements = [
            MovementCommand.WEST,
            MovementCommand.NORTH,
            MovementCommand.EAST,
            MovementCommand.SOUTH
        ]
    def getDistance(self):
        return self.distance

    def getPosition(self):
        return self.value

    def copyComputer(self):
        return copy.copy(self.computer)

    def process_movement(self):
        '''
        Performs one movement based off of the current
        memory
        '''
        self.computer.set_input_queue([self.command])

        movementStatus = self.computer.process_intcode()
        self.key = movementStatus
        self.memory = self.computer.instructions

        return movementStatus


def buildPathFrom(node):
    path = []
    while node.parent:
        path += [ node.getPosition() ]
        node = node.parent

    return list(reversed(path))


def createPositionFromMovementCommand(currentPosition, movementCommand):
    position = None
    # print(f"currentPosition: {currentPosition}")
    if movementCommand == MovementCommand.EAST:
        position = Position(currentPosition.x + 1, currentPosition.y)
    elif movementCommand == MovementCommand.NORTH:
        position = Position(currentPosition.x, currentPosition.y + 1)
    elif movementCommand == MovementCommand.WEST:
        position = Position(currentPosition.x - 1, currentPosition.y)
    elif movementCommand == MovementCommand.SOUTH:
        position = Position(currentPosition.x, currentPosition.y - 1)

    return position

# def createRobotFromMovementCommand(computer, parent, currentPosition, movementCommand):
#     position = createPositionFromMovementCommand(currentPosition, movementCommand)
#     robot = Robot(position, computer.instructions


visitedPositions = set([])
mappingData = {}
def outputMap(robotPosition, size=5, mapType='robot'):
    os.system("clear")
    robot_x = robotPosition.x
    robot_y = robotPosition.y
    # print(f"Robot: {robotPosition}")
    # if self.max_y - 10 < 0:


    lower_x = robot_x - size
    upper_x = robot_x + size
    lower_y = robot_y + size
    upper_y = robot_y - size

    if mapType == 'full':
        min_x = min([ position.x for position in visitedPositions ])
        max_x = max([ position.x for position in visitedPositions ])
        min_y = min([ position.y for position in visitedPositions ])
        max_y = max([ position.y for position in visitedPositions ])
        lower_x = min_x
        upper_x = max_x
        lower_y = max_y
        upper_y = min_y


    for row in range(lower_y, upper_y, -1):
        for col in range(lower_x, upper_x):
            reference = Position(col, row)

            output = " "

            if str(reference) in mappingData:
                referenceStatus = mappingData[str(reference)]

                if referenceStatus == MoveStatus.WALL:
                    output = "#"

                if referenceStatus == MoveStatus.SUCCESS:
                    output = "."

                if referenceStatus == MoveStatus.OXYGEN:
                    output = "X"

            if reference == robotPosition:
                output = "R"

            print(output, end=" ")
        print("\n")
    # print(f"min-x: {self.min_x}, max-x: {self.max_x}, min-y: {self.min_y}, max_y: {self.max_y}")
    # print(self.worldNodes)
    # print(f"Robot Position: {robot.getPosition()}")
    return True
'''
Modified search in which we initialize the current node that we
are at and try to traverse it.
'''
def getFirstValidPath(robot, path = [], visited=[], key=MoveStatus.OXYGEN, minDistance=0):
    if robot.command:
        robot.process_movement()
        # outputMap(robot.getPosition(), 5)
        # print(robot.getPosition())


    # The robot has processed that there is a wall ahead
    if robot.key == MoveStatus.WALL:
        visitedPositions.add(robot.getPosition())
        mappingData[str(robot.getPosition())] = MoveStatus.WALL

        return None

    # We have found the robot we are looking for
    if robot.key and robot.key == key and minDistance == 0:
        print("DING")
        return path

    # Useful if we want to find the shortest possible path to n steps?
    if robot.key and robot.key == key and robot.distance == minDistance and minDistance != 0:
        return path


    # Haven't found anything, but we will still keep going
    copiedComputer = robot.copyComputer()
    visitedPositions.add(robot.getPosition())
    mappingData[str(robot.getPosition())] = MoveStatus.SUCCESS
    # sleep(0.10)

    for command in robot.movements:

        position = createPositionFromMovementCommand(robot.getPosition(), command)

        if position in visited:
            continue

        visitedCopy = visited.copy()

        visitedCopy += [ position ]

        newRobot = Robot(position, copiedComputer.instructions, robot.distance + 1, command, copiedComputer)
        newRobot.setParent(robot)

        ## recursively try and find the path
        path = getFirstValidPath(newRobot, buildPathFrom(newRobot), visitedCopy, key, minDistance)

        if not path:
            continue

        return path

    return None


if __name__ == '__main__':
    with open('input.txt', 'r') as f:
        robotInstructions = f.read()

    startPosition = Position(0,0)
    robot = Robot(startPosition, robotInstructions)
    print(getFirstValidPath(robot))