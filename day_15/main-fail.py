import sys
import enum
import os
from time import sleep
from collections import deque
sys.path.append("..")

from general.position import Position, Positioned
from general.intcode_computer.main import IntcodeComputer

class Node(Positioned):
    def __init__(self, position, distance):
        self.position = position
        self.distance = distance

    def getPosition(self):
        return self.position

    def getDistance(self):
        return self.distance

    def __str__(self):
        return f"({self.position.x}, {self.position.y}, {self.distance})"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return (
            self.position.x == other.position.x and
            self.position.y == other.position.y
        )

class MovementCommand(enum.IntEnum):
    NORTH = 1
    SOUTH = 2
    WEST = 3
    EAST = 4

class MoveStatus(enum.IntEnum):
    WALL = 0
    SUCCESS = 1
    OXYGEN = 2

class Robot(Positioned):
    def __init__(self, computer):
        self.computer = computer
        self.position = Position(0, 0)

    def getPosition(self):
        return self.position

    def getAdjacentNodesWithDirection(self, distance):
        return [
            (Node(Position(self.position.x - 1, self.position.y), distance), MovementCommand.WEST ),# left
            (Node(Position(self.position.x, self.position.y + 1), distance), MovementCommand.NORTH ), # Up
            (Node(Position(self.position.x + 1, self.position.y), distance), MovementCommand.EAST ), # Right
            (Node(Position(self.position.x, self.position.y - 1), distance), MovementCommand.SOUTH) # Down
        ]

    def postMovement(self, movementCode = False):
        if not movementCode:
            self.computer.set_input_queue([movementCode])
        return self.computer.process_intcode()

    def setPosition(self, position):
        self.position = position
        return True

    def setPositionFromNode(self, node):
        self.setPosition(node.getPosition())
        return True

class WorldMap:
    def __init__(self):
        self.worldNodes = []
        self.environmentReferences = {}
        self.positioned = None
        self.min_x = None
        self.min_y = None
        self.max_x = None
        self.max_y = None

    def __updateMeta(self):
        nodePositionXValues = [ node.position.x for node in self.worldNodes ]
        nodePositionYValues = [ node.position.y for node in self.worldNodes ]
        self.min_x = min(nodePositionXValues)
        self.min_y = min(nodePositionYValues)
        self.max_x = max(nodePositionXValues)
        self.max_y = max(nodePositionYValues)

    def setInitialPositioned(self, positioned):
        self.worldNodes.append(Node(positioned.position, 0))
        self.setPositioned(positioned)

    def setPositioned(self, positioned):
        if not issubclass(positioned.__class__, Positioned):
            raise Exception("Setting non-positioned item.")

        self.positioned = positioned
        self.__updateMeta()

    def isDuplicateNode(self, node):
        if not node in self.worldNodes:
            return False

        for worldNode in self.worldNodes:
            if node == worldNode and worldNode.distance <= node.distance:
                return True

        return False

    def add(self, node):
        duplicateNode = self.isDuplicateNode(node)

        if duplicateNode:
            return

        self.worldNodes += [ node ]
        self.__updateMeta()

    def addEnvironment(self, position, environmentType):
        self.environmentReferences[str(position)] = environmentType

    def output(self):
        os.system("clear")
        robotPosition = self.positioned.getPosition()
        robot_x = robotPosition.x
        robot_y = robotPosition.y
        # print(f"Robot: {robotPosition}")
        # if self.max_y - 10 < 0:

        for row in range(robot_y + 5, robot_y - 5, -1):
            for col in range(robot_x - 5, robot_x + 5):
                reference = Position(col, row)
                # print(f"REFERENCE: {reference}")
                output = "."

                if reference == robotPosition:
                    output = "R"

                if str(reference) in self.environmentReferences:
                    output = self.environmentReferences[str(reference)]

                print(output, end=" ")
            print("\n")
        # print(f"min-x: {self.min_x}, max-x: {self.max_x}, min-y: {self.min_y}, max_y: {self.max_y}")
        # print(self.worldNodes)
        # print(f"Robot Position: {robot.getPosition()}")
        return True

class World:
    def __init__(self, robot, worldMap):
        self.robot = robot
        self.worldMap = worldMap
        worldMap.setInitialPositioned(robot)
    '''
    Pathfinding Algorithm
    '''
    def run(self, controlled = True):

        run = True
        count = 0
        for currentNode in self.worldMap.worldNodes:
            # print(f"CURRENT NODE: -> {currentNode}")
            # print(self.worldMap.worldNodes)
            # currentNode = self.worldMap.worldNodes.popleft()
            currentNodeDistance = currentNode.distance
            robot.setPositionFromNode(currentNode)
            # self.worldMap.output()
            # print(f"robotPosition {robot.getPosition()}")
            newDirectionalNodes = robot.getAdjacentNodesWithDirection(currentNodeDistance + 1)
            # print(self.worldMap.worldNodes)
            # print(newDirectionalNodes)
            if controlled:
                moveStatus = self.robot.postMovement()
            if moveStatus == MoveStatus.WALL:
                self.worldMap.addEnvironment(newNode.position, 'W')
            elif moveStatus == MoveStatus.SUCCESS:
                # Post the position
                self.worldMap.add(newNode)
            elif moveStatus == MoveStatus.OXYGEN:
                # We found the oxygen. Find the shortest path.
                run = False
            else:
                for nodeWithDirection in newDirectionalNodes:
                    newNode = nodeWithDirection[0]
                    direction = nodeWithDirection[1]
                    movement = int(direction)
                    # print(newNode)
                    # print(direction)
                    # print(nodeWithDirection)
                    moveStatus = self.robot.postMovement(movement)
                    # print(f"{nodeWithDirection} --> {moveStatus}")
                    if moveStatus == MoveStatus.WALL:
                        self.worldMap.addEnvironment(newNode.position, 'W')
                    elif moveStatus == MoveStatus.SUCCESS:
                        # Post the position
                        self.worldMap.add(newNode)
                    elif moveStatus == MoveStatus.OXYGEN:
                        # We found the oxygen. Find the shortest path.
                        run = False

            if not run:
                break
            # print(self.worldMap.worldNodes)
            # sleep(0.1)
            count += 1
            # if count % 10 == 0:
            self.worldMap.output()
        print(self.worldMap)
        self.worldMap.output()




if __name__ == "__main__":
    with open('input.txt', 'r') as f:
        instructions = f.read()

    computer = IntcodeComputer(instructions, True, True, True, False, True)
    computer_2 = IntcodeComputer(instructions, False, True, True, False, True)
    robot = Robot(computer)
    controlledRobot = Robot(computer_2)
    world = World(robot, WorldMap())
    world_2 = World(controlledRobot, WorldMap())
    # world.run()
    world_2.run(True)

