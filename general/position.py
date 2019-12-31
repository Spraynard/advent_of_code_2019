class Position:
    def __init__(self, x, y):
        self.x = x
        self.y = y

    def setPosition(self, x, y):
        self.x = x
        self.y = y

    def __str__(self):
        return f"[{self.x}, {self.y}]"

    def __repr__(self):
        return str(self)

    def __eq__(self, other):
        return (self.x == other.x) and (self.y == other.y)

    def __hash__(self):
        return hash(str(self))

    def __add__(self, other):
        return Position(self.x + other.x, self.y + other.y)

class Positioned:
    def getPosition(self):
        raise Exception("getPosition -- Not Implemented")