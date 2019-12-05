'''
For each wire, build a set of positions that 
constitute where the wire is on the panel board.

Perform a set intersect operation to find all positions that are the same
between the two wires

Map over these positions with a cab driver distance and find the minimum distance, i.e., the closest to the origin.
'''

from collections import deque

class Point:
    def __init__(self, x, y):
        self.x = x
        self.y = y

class Position(Point):
    def __str__(self):
        return "( {x_value}, {y_value} )".format(x_value=self.x, y_value=self.y)
    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)
    def __hash__(self):
        return hash((self.x, self.y))
    def get_snake_distance(self, other):
        return abs(self.x - other.x) + abs(self.y - other.y)

class Wire:
    def __init__(self, moves):
        self.moves = moves
        self.positions = self.create_positions(moves)

    def get_intersections(self, other):
        '''
        Return a set of positions where this and another wire intersect
        '''
        return self.positions.intersection(other.positions)
    
    def print_positions(self):
        print([str(position) for position in self.positions])
        return True

    def create_positions(self, moves):
        '''
        Returns a set of positions that model the areas of the grid that our wire
        covers
        '''
        move_queue = [move for move in moves.split(",")]
        positions = set()
        current = Position(0,0)

        for move in move_queue:
            direction, amount = ( move[0], int(move[1:]) )

            if direction == 'U':
                delta = abs(current.y - (current.y + amount))
                move_positions = [Position(current.x, current.y + step) for step in range(0, delta + 1)]
                current = Position(current.x, current.y + amount)
            elif direction == 'D':
                delta = abs(current.y - (current.y + amount))
                move_positions = [Position(current.x, current.y - step) for step in range(0, delta + 1)]
                current = Position(current.x, current.y - amount)
            elif direction == 'L':
                delta = abs(current.x - (current.x + amount))
                move_positions = [Position(current.x - step, current.y ) for step in range(0, delta + 1)]
                current = Position(current.x - amount,current.y)
            elif direction == 'R':
                delta = abs(current.x - (current.x + amount))
                move_positions = [Position(current.x + step, current.y ) for step in range(0, delta + 1)]
                current = Position(current.x + amount, current.y)
            positions = positions.union(set(move_positions))

        return positions

if __name__ == '__main__':
    moveset_1 = 'R1,R1,U1,U1,U1'
    moveset_2 = 'U1,U1,R1,R1,R1'

    wire_1 = Wire(moveset_1)
    wire_2 = Wire(moveset_2)

    intersections = wire_1.get_intersections(wire_2)
    snake_distance_intersections = [ pos.get_snake_distance(Position(0,0)) for pos in intersections ]
    closest = min(snake_distance_intersections)


    moves_file = open('input.txt', 'r')

    with moves_file:
        moves_data = moves_file.readlines()

        '''
        for some reason this data has \n in it...
        '''
        moves_1, moves_2 = [moves_data[0].replace("\n",""), moves_data[1].replace("\n","")]
        wire_1 = Wire(moves_1)
        wire_2 = Wire(moves_2)

        intersections = wire_1.get_intersections(wire_2)
        snake_distance_intersections = [ pos.get_snake_distance(Position(0,0)) for pos in intersections if not pos == Position(0,0)]
        closest = min(snake_distance_intersections)

    print(f"Closest: {closest}")
