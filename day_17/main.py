import sys
sys.path.append('..')
from time import sleep
import collections
import functools
import operator
import enum
import copy
import re

from general.intcode_computer.main import IntcodeComputer
from general.position import Position

class NeighborDirection(enum.Enum):
    NORTH = Position(0, -1)
    EAST = Position(1, 0)
    SOUTH = Position(0, 1)
    WEST = Position(-1, 0)

'''
ASCII codes for our Routines
'''
class Routines(enum.Enum):
    A = ord('A')
    B = ord('B')
    C = ord('C')

'''
ASCII codes for directions
'''
class DirectionCodes(enum.Enum):
    LEFT = ord('L')
    RIGHT = ord('R')

class Orientations(enum.Enum):
    NORTH = ord('^')
    EAST = ord('>')
    SOUTH = ord('v')
    WEST = ord('<')

orientationsDirectionsMapping = {
    Orientations.NORTH : {
        DirectionCodes.LEFT: NeighborDirection.WEST,
        DirectionCodes.RIGHT: NeighborDirection.EAST
    },
    Orientations.EAST : {
        DirectionCodes.LEFT : NeighborDirection.NORTH,
        DirectionCodes.RIGHT : NeighborDirection.SOUTH
    },
    Orientations.SOUTH : {
        DirectionCodes.LEFT : NeighborDirection.EAST,
        DirectionCodes.RIGHT : NeighborDirection.WEST
    },
    Orientations.WEST : {
        DirectionCodes.LEFT : NeighborDirection.SOUTH,
        DirectionCodes.RIGHT : NeighborDirection.NORTH
    }
}

orientationsLookaheadMapping = {
    Orientations.NORTH : {
        DirectionCodes.LEFT: Orientations.WEST,
        DirectionCodes.RIGHT: Orientations.EAST
    },
    Orientations.EAST : {
        DirectionCodes.LEFT : Orientations.NORTH,
        DirectionCodes.RIGHT : Orientations.SOUTH
    },
    Orientations.SOUTH : {
        DirectionCodes.LEFT : Orientations.EAST,
        DirectionCodes.RIGHT : Orientations.WEST
    },
    Orientations.WEST : {
        DirectionCodes.LEFT : Orientations.SOUTH,
        DirectionCodes.RIGHT : Orientations.NORTH
     }
}

class Location():
    def __init__(self, position, charCode):
        self.neighboring = []
        self.key = position
        self.value = chr(charCode)

    def addNeighbor(self, neighbor):
        self.neighboring.append(neighbor)
        return True

    def removeFromNeighboring(self):
        '''
        Clears this node from other nodes
        '''
        for neighbor in self.neighboring:
            neighbor.neighboring.remove(self)

    def __str__(self):
        return '''
Position: {position}
Code: {value}
Neighbors: {neighboring}
'''.format(value=self.value, position=self.key, neighboring=self.neighboring)

    def __repr__(self):
        return str([self.key, self.value])

    def __eq__(self, other):
        return (self.key == other.key) and (self.neighboring == other.neighboring)

    def printNeighbors(self):
        for neighbor in self.neighboring:
            print("*" * 20)
            print(neighbor)
            print("*" * 20)

    def isIntersectionPoint(self):
        return (
            self.value == '#' and
            all([ location.value == '#' for location in self.neighboring ]) and
            len(self.neighboring) == 4
        )

    def isScaffolding(self):
        return self.value == '#'

    def getNeighborAt(self, direction):
        neighborPosition = self.key + direction

        for neighbor in self.neighboring:
            if neighbor.key == neighborPosition:
                return neighbor

        return None

    def moveTo(self, other):
        '''
        Move a robot to another location
        '''
        if not self.getOrientation():
            print("Do not have an orientation")
            return

        # neighborPosition = self.key + direction
        # print(f"Neighbor Position {neighborPosition}")
        # locationToMoveTo = None

        # for neighbor in self.neighboring:
        #     if neighbor.key == neighborPosition:
        #         locationToMoveTo = neighbor

        # if not locationToMoveTo:
        #     print("Could not find location")
        #     return

        self.removeFromNeighboring()
        other.removeFromNeighboring()
        self.neighboring.remove(other)

        otherCopy = copy.copy(other)

        other.key = self.key
        other.neighboring = self.neighboring
        self.key = otherCopy.key
        self.neighboring = otherCopy.neighboring

        for neighbor in other.neighboring:
            neighbor.addNeighbor(other)


        for neighbor in self.neighboring:
            neighbor.addNeighbor(self)

        self.addNeighbor(other)
        other.addNeighbor(self)

        return True

    def getOrientation(self):
        try:
            orientation = Orientations(ord(self.value))
        except:
            orientation = None
        finally:
            return orientation

def cameraView( computer, printOut=False ):
    '''
    Builds a graph of what the camera currently sees.
    Root is at the initial position, (0,0)
    '''
    position_x = 0
    position_y = 0
    locations = {}
    while True:
        charCode = computer.process_intcode()
        # print(charCode)
        if not charCode:
            break

        if charCode == 10:
            position_y += 1
            position_x = 0
            if printOut:
                print("\n")
            continue

        currentPosition = Position(position_x, position_y)

        '''
        When reaching end of all processing. Our charcode will actually be a large, non ASCII value.
        This could make setting our currentLocation raise an error
        '''
        try:
            currentLocation = Location(currentPosition, charCode)
        except ValueError:
            return charCode

        locations[currentPosition] = currentLocation

        westPosition = Position(position_x - 1, position_y)

        if westPosition in locations:
            currentLocation.addNeighbor(locations[westPosition])
            locations[westPosition].addNeighbor(currentLocation)

        northPosition = Position(position_x, position_y - 1)
        if northPosition in locations:
            currentLocation.addNeighbor(locations[northPosition])
            locations[northPosition].addNeighbor(currentLocation)

        eastPosition = Position(position_x + 1, position_y)
        if eastPosition in locations:
            currentLocation.addNeighbor(locations[eastPosition])
            locations[eastPosition].addNeighbor(currentLocation)

        southPosition = Position(position_x, position_y + 1)
        if southPosition in locations:
            currentLocation.addNeighbor(locations[southPosition])
            locations[southPosition].addNeighbor(currentLocation)

        if printOut:
            print(chr(charCode), end=" ")

        position_x += 1

    return locations[Position(0,0)]

def searchIntersectionPoints(node):
    '''
    DFS that searches for all nodes in which there is an intersection point
    '''
    S = collections.deque([node])
    visited = []
    intersections = []
    while S:
        currentLocation = S.pop()

        if currentLocation.key not in visited:
            visited.append(currentLocation.key)

            if currentLocation.isIntersectionPoint():
                intersections.append(currentLocation)

            for neighboringLocation in currentLocation.neighboring:
                S.append(neighboringLocation)

    return intersections

def searchByPositionOrRobot(root, key):
    '''
    Key can also be a string of 'robot'
    '''

    S = collections.deque([root])
    visited = []
    while S:
        currentLocation = S.pop()

        if currentLocation.key not in visited:
            visited.append(currentLocation.key)

            '''
            Only the robot has an orientation
            '''
            if key == "robot" and currentLocation.getOrientation():
                return currentLocation

            if type(key) == Position and currentLocation.key == key:
                return currentLocation


            for neighboringLocation in currentLocation.neighboring:
                S.append(neighboringLocation)

    return None

def buildScaffoldPath( robot ):
    visited = []
    scaffoldPath = []
    moveCount = 0
    while True:
        orientation = robot.getOrientation()
        leftLocation = robot.getNeighborAt(orientationsDirectionsMapping[orientation][DirectionCodes.LEFT].value)
        rightLocation = robot.getNeighborAt(orientationsDirectionsMapping[orientation][DirectionCodes.RIGHT].value)
        forwardLocation = robot.getNeighborAt(NeighborDirection[orientation.name].value)

        # Having a forward location means that we can keep going.
        if forwardLocation and forwardLocation.isScaffolding():
            # print(f"FORWARD LOCATION: {forwardLocation}")
            robot.moveTo(forwardLocation)
            moveCount += 1
        # Orient the robot to the left
        elif leftLocation and leftLocation.isScaffolding():
            # print("Turning Left")
            if moveCount:
                scaffoldPath.append(str(moveCount))

            moveCount = 0
            robot.value = chr(orientationsLookaheadMapping[orientation][DirectionCodes.LEFT].value)
            scaffoldPath.append(DirectionCodes.LEFT.name[0])
        # Orient the robot to the right
        elif rightLocation and rightLocation.isScaffolding():
            # print("Turning Right")
            if moveCount:
                scaffoldPath.append(str(moveCount))

            moveCount = 0
            robot.value = chr(orientationsLookaheadMapping[orientation][DirectionCodes.RIGHT].value)
            scaffoldPath.append(DirectionCodes.RIGHT.name[0])
        else:
            if moveCount:
                scaffoldPath.append(str(moveCount))
            break

    return scaffoldPath

def getNumSubsets( subset, path ):
    return len(re.findall("".join(subset),"".join(path)))

def getMoveCommands( path ):
    pathLen = len(path)
    patternSize = 2
    totalSubsetNum = int(pathLen / patternSize)
    patterns = []

    pathIndex = 0
    while pathIndex < pathLen:
        patternStart = pathIndex
        patternEnd = pathIndex + patternSize

        pattern = path[patternStart:patternEnd]

        pathIndex = patternEnd

        if pattern in patterns:
            print(patterns)
            continue

        numOfPatternSubsets = getNumSubsets(pattern, path)

        totalSubsetNum -= numOfPatternSubsets
        print(f"PATTERN {pattern}\nNum Subsets: {numOfPatternSubsets}\nTotal Subset Num: {totalSubsetNum}\nPatternNum: {len(','.join(pattern))}\n")

        patterns.append(pattern)


        if totalSubsetNum < 0 or len(patterns) > 3 or len(",".join(pattern)) > 20:
            pathIndex = 0
            patternSize += 2
            totalSubsetNum = int(pathLen / patternSize)
            patterns = []

        if totalSubsetNum == 0 and len(patterns) == 3:
            break

        if patternEnd - patternStart > 20:
            return False

    return patterns

def convertMoveFunctionsToStrings(moveFns):
    stringPatterns = []
    for function in moveFns:
        convertedFn = list(map(lambda item: item.name[0] if item in [code for code in DirectionCodes] else str(item),function))
        stringPatterns.append(",".join(convertedFn))

    return stringPatterns

def convertToASCII(initial):
    return [ord(char) for char in list(initial)] + [ord("\n")]

def convertMoveFunctionsToASCII(moveFns):
    returnValue = []
    for fn in moveFns:
        returnValue += convertToASCII(fn)
    return returnValue
    # return [ convertToASCII(function) for function in moveFns ]

def createMainRoutine( patterns, path ):
    mainRoutine = path
    patterns = sorted(patterns, key=lambda arr: len(arr), reverse=True)
    for index, routine in enumerate(Routines):
        pattern = patterns[index]

        mainRoutine = mainRoutine.replace(pattern, str(routine.name))

    return mainRoutine



if __name__ == "__main__":
    with open('input.txt', 'r') as f:
        instructions = f.read()

    computer = IntcodeComputer(instructions, False, True, True, False, True, False)

    # # print(startNode)
    # # startNode.printNeighbors()
    # # intersection_points = searchIntersectionPoints(startNode)
    # # print(intersection_points)
    # # print(functools.reduce(
    # #     operator.add,
    # #     [ pos.x * pos.y for pos in [ location.key for location in intersection_points ] ]
    # # ))
    # robot = searchByPositionOrRobot(startNode, 'robot')
    # path = buildScaffoldPath(robot)
    # print(path)
    # print(robot)
    # Part 2 Change the value at adress 0 from 1 to 2 in instructions
# ['LEFT', '12', 'RIGHT', '8', 'LEFT', '6', 'RIGHT', '8', 'LEFT', '6', 'RIGHT', '8', 'LEFT', '12', 'LEFT', '12', 'RIGHT', '8', 'LEFT', '12', 'RIGHT', '8', 'LEFT', '6', 'RIGHT', '8', 'LEFT', '6', 'LEFT', '12', 'RIGHT', '8', 'LEFT', '6', 'RIGHT', '8', 'LEFT', '6', 'RIGHT', '8', 'LEFT', '12', 'LEFT', '12', 'RIGHT', '8', 'LEFT', '6', 'RIGHT', '6', 'LEFT', '12', 'RIGHT', '8', 'LEFT', '12', 'LEFT', '12', 'RIGHT', '8', 'LEFT', '6', 'RIGHT', '6', 'LEFT', '12', 'LEFT', '6', 'RIGHT', '6', 'LEFT', '12', 'RIGHT', '8', 'LEFT', '12', 'LEFT', '12', 'RIGHT', '8']
    # testPath = 'R,8,R,8,R,4,R,4,R,8,L,6,L,2,R,4,R,4,R,8,R,8,R,8,L,6,L,2'
    # testPattern = [['R', '8', 'R', '8', 'R', '4', 'R', '4'], ['R', '8', 'L', '6', 'L', '2', 'R', '4'], ['R', '4', 'R', '8', 'R', '8', 'R', '8']]
    # testPattern2 = [['R', '8', 'R', '8'], ['R', '4', 'R', '4', 'R', '8'], ['L', '6', 'L', '2']]
    instructions = instructions.split(',')
    instructions[0] = str(2)
    instructions = ",".join(instructions)

    # Found this by hand after finding the scaffold path :(
    moveFunctions = [
        [DirectionCodes.LEFT,12,DirectionCodes.RIGHT,8,DirectionCodes.LEFT,6,DirectionCodes.RIGHT,8,DirectionCodes.LEFT,6],
        [DirectionCodes.RIGHT,8,DirectionCodes.LEFT,12,DirectionCodes.LEFT,12,DirectionCodes.RIGHT,8],
        [DirectionCodes.LEFT,6,DirectionCodes.RIGHT,6,DirectionCodes.LEFT,12]
    ]

    path = 'L,12,R,8,L,6,R,8,L,6,R,8,L,12,L,12,R,8,L,12,R,8,L,6,R,8,L,6,L,12,R,8,L,6,R,8,L,6,R,8,L,12,L,12,R,8,L,6,R,6,L,12,R,8,L,12,L,12,R,8,L,6,R,6,L,12,L,6,R,6,L,12,R,8,L,12,L,12,R,8'

    moveFunctions = convertMoveFunctionsToStrings(moveFunctions)
    mainRoutine = createMainRoutine(moveFunctions, path)
    convertedMoveFunctions = convertMoveFunctionsToASCII(moveFunctions)
    convertedMainRoutine = convertToASCII(mainRoutine)
    print(mainRoutine)
    print(convertedMoveFunctions)
    print(convertedMainRoutine)
    print(convertedMainRoutine + convertedMoveFunctions)

    # print(instructions)
    newComputer = IntcodeComputer(instructions, True, True, True, False, True, False)
    newComputer.set_input_queue(convertedMainRoutine + convertedMoveFunctions + [110, 10])
    dustCollected = cameraView(newComputer, True)
    print(f"Dust Collected: {dustCollected}")

    # print([str(asciiCode) for asciiCode in convertedMainRoutine])
    # newComputer.set_input_queue([asciiCode for asciiCode in convertedMainRoutine])
    # newComputer.process_intcode()
    # print("1")
    # newComputer.set_input_queue([asciiCode for asciiCode in convertedMoveFunctions[0]])
    # newComputer.process_intcode()
    # print("2")
    # newComputer.set_input_queue([asciiCode for asciiCode in convertedMoveFunctions[1]])
    # newComputer.process_intcode()
    # print("3")
    # newComputer.set_input_queue([asciiCode for asciiCode in convertedMoveFunctions[2]])
    # newComputer.process_intcode()
    # print("4")
    # newComputer.set_input_queue([110])
    # print(newComputer.process_intcode())
    # print("Yup")
    # print(stringPattern)
    # mainRoutine = createMainRoutine(testPattern2, testPath)
    # print(mainRoutine)