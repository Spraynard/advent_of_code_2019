# Standard Library
import sys
import os
from enum import IntEnum
sys.path.append("..") # Setting top level on path to import modules

# Local Application Imports
from general.intcode_computer.main import IntcodeComputer
from general.helpers import trueIfNotNone

class TileID(IntEnum):
    EMPTY = 0 # No game object in this tile
    WALL = 1 # Walls are indestructible barriers
    BLOCK = 2 # Blocks can be broken by ball
    HORIZONTAL_PADDLE = 3 # Paddle is indestructible
    BALL = 4 # Ball moves diagonally and bounces off objects

class Tile:
    def __init__(self, id, x, y):
        self.id = int(id)
        self.position = [x, y]

    def __eq__(self, other):
        return (
            self.position[0] == other.position[0] and
            self.position[1] == other.position[1] and
            self.id == other.id
        )

    def isOfType(self, type):
        '''
        Type can either be an integer or a TileID enum
        '''
        return self.id == type

    def getID(self):
        return self.id

class Wall(Tile):
    def __init__(self, x, y):
        super().__init__(TileID.WALL, x, y)

    def __str__(self):
        return "="

class Block(Tile):
    def __init__(self, x, y):
        super().__init__(TileID.BLOCK, x, y)

    def __str__(self):
        return "#"

class HorizontalPaddle(Tile):
    def __init__(self, x, y):
        super().__init__(TileID.HORIZONTAL_PADDLE, x, y)

    def __str__(self):
        return "_"

class Ball(Tile):
    def __init__(self, x, y):
        super().__init__(TileID.BALL, x, y)

    def __str__(self):
        return u'\u25CF'

class Empty(Tile):
    def __init__(self, x, y):
        super().__init__(TileID.EMPTY, x, y)

    def __str__(self):
        return " "

class TileFactory:
    @staticmethod
    def createTile(tile_id = None, x = 0, y = 0):
        '''
        Returns a tile object that has a position as given
        in the parameters of this function.
        '''
        tile = None

        if tile_id == TileID.EMPTY:
            tile = Empty(x, y)
        elif tile_id == TileID.WALL:
            tile = Wall(x, y)
        elif tile_id == TileID.BLOCK:
            tile = Block(x, y)
        elif tile_id == TileID.HORIZONTAL_PADDLE:
            tile = HorizontalPaddle(x, y)
        elif tile_id == TileID.BALL:
            tile = Ball(x, y)
        else:
            raise Exception(f"Tile ID of {tile_id} is not supported")

        return tile

class Game:
    """
    Software is the intcode program string
    """
    def __init__(self, computer, tile_factory):
        self.computer = computer
        self.tile_factory = tile_factory
        self.score = 0
        self.tiles = []
        self.position_to_block = {}

    def tileCount(self):
        return len(self.tiles)

    def setScore(self, score):
        self.score = score

    def loop(self):
        action_array = [
                self.computer.process_intcode(), # Get X Position
                self.computer.process_intcode(), # Get Y Position
                self.computer.process_intcode()  # Get Tile ID
        ]

        if not all([ trueIfNotNone(action) for action in action_array ]):
            ''' Intcode Signal of 999 was processed '''
            return False

        # Converting the output to INT if it's not already int.
        x, y, tile_id = action_array

        # Game is specifying a new score
        if x == -1 and y == 0:
            self.setScore(tile_id)
            return True

        tile = self.tile_factory.createTile( tile_id, x, y )
        self.position_to_block[str([x, y])] = tile
        self.tiles += [ tile ]

        return True

    def __numRows(self):
        return max([ tile.position[1] for tile in self.tiles ])

    def __numColumnsInRow(self, rowNum):
        return max([ tile.position[0] for tile in self.tiles if tile.position[1] == rowNum ])

    def outputMap(self):
        os.system("clear")
        for row in range(self.__numRows() + 1):
            for column in range(self.__numColumnsInRow(row) + 1):
                print(self.position_to_block[str([column, row])], end=" ")
            print("\n")

    def outputScore(self):
        print("""
****************************
* Current Score: {score}   *
****************************
""".format(score=self.score))
    def play(self):
        while self.loop():
            self.outputMap()
            self.outputScore()

        return True

if __name__ == "__main__":
    with open('input.txt', 'r') as f:
        instructions = f.read()
        # Free Play Mode
        instructions_array = list(instructions)
        instructions_array[0] = '2'
        instructions = "".join(instructions_array)

    game = Game(
        IntcodeComputer(instructions, False, True, True, False, True),
        TileFactory
    )

    game.play()

    block_tiles = [ tile for tile in game.tiles if tile.isOfType(TileID.BLOCK) ]
    print(f"Number of block tiles when played: {len(block_tiles)}")
    print(f"Number of tiles when played: {game.tileCount()}")