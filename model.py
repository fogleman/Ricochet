import itertools
import random

# Directions
NORTH = 'N'
EAST = 'E'
SOUTH = 'S'
WEST = 'W'

DIRECTIONS = [NORTH, EAST, SOUTH, WEST]

REVERSE = {
    NORTH: SOUTH,
    EAST: WEST,
    SOUTH: NORTH,
    WEST: EAST,
}

OFFSET = {
    NORTH: -16,
    EAST: 1,
    SOUTH: 16,
    WEST: -1,
}

# Masks
M_NORTH = 0x01
M_EAST  = 0x02
M_SOUTH = 0x04
M_WEST  = 0x08
M_ROBOT = 0x10

M_LOOKUP = {
    NORTH: M_NORTH,
    EAST: M_EAST,
    SOUTH: M_SOUTH,
    WEST: M_WEST,
}

# Colors
RED = 'R'
GREEN = 'G'
BLUE = 'B'
YELLOW = 'Y'

COLORS = [RED, GREEN, BLUE, YELLOW]

# Shapes
CIRCLE = 'C'
TRIANGLE = 'T'
SQUARE = 'Q'
HEXAGON = 'H'

SHAPES = [CIRCLE, TRIANGLE, SQUARE, HEXAGON]

# Tokens
TOKENS = [''.join(token) for token in itertools.product(COLORS, SHAPES)]

# Quadrants
QUAD_1A = (
    'NW,N,N,N,NE,NW,N,N,'
    'W,S,X,X,X,X,SEYH,W,'
    'WE,NWGT,X,X,X,X,N,X,'
    'W,X,X,X,X,X,X,X,'
    'W,X,X,X,X,X,S,X,'
    'SW,X,X,X,X,X,NEBQ,W,'
    'NW,X,E,SWRC,X,X,X,S,'
    'W,X,X,N,X,X,E,NW'
)

QUAD_1B = (
    'NW,NE,NW,N,NS,N,N,N,'
    'W,S,X,E,NWRC,X,X,X,'
    'W,NEGT,W,X,X,X,X,X,'
    'W,X,X,X,X,X,SEYH,W,'
    'W,X,X,X,X,X,N,X,'
    'SW,X,X,X,X,X,X,X,'
    'NW,X,E,SWBQ,X,X,X,S,'
    'W,X,X,N,X,X,E,NW'
)

QUAD_2A = (
    'NW,N,N,NE,NW,N,N,N,'
    'W,X,X,X,X,E,SWBC,X,'
    'W,S,X,X,X,X,N,X,'
    'W,NEYT,W,X,X,S,X,X,'
    'W,X,X,X,E,NWGQ,X,X,'
    'W,X,SERH,W,X,X,X,X,'
    'SW,X,N,X,X,X,X,S,'
    'NW,X,X,X,X,X,E,NW'
)

QUAD_2B = (
    'NW,N,N,N,NE,NW,N,N,'
    'W,X,SERH,W,X,X,X,X,'
    'W,X,N,X,X,X,X,X,'
    'WE,SWGQ,X,X,X,X,S,X,'
    'SW,N,X,X,X,E,NWYT,X,'
    'NW,X,X,X,X,S,X,X,'
    'W,X,X,X,X,NEBC,W,S,'
    'W,X,X,X,X,X,E,NW'
)

QUAD_3A = (
    'NW,N,N,NE,NW,N,N,N,'
    'W,X,X,X,X,SEGH,W,X,'
    'WE,SWRQ,X,X,X,N,X,X,'
    'SW,N,X,X,X,X,S,X,'
    'NW,X,X,X,X,E,NWYC,X,'
    'W,X,S,X,X,X,X,X,'
    'W,X,NEBT,W,X,X,X,S,'
    'W,X,X,X,X,X,E,NW'
)

QUAD_3B = (
    'NW,N,NS,N,NE,NW,N,N,'
    'W,E,NWYC,X,X,X,X,X,'
    'W,X,X,X,X,X,X,X,'
    'W,X,X,X,X,E,SWBT,X,'
    'SW,X,X,X,S,X,N,X,'
    'NW,X,X,X,NERQ,W,X,X,'
    'W,SEGH,W,X,X,X,X,S,'
    'W,N,X,X,X,X,E,NW'
)

QUAD_4A = (
    'NW,N,N,NE,NW,N,N,N,'
    'W,X,X,X,X,X,X,X,'
    'W,X,X,X,X,SEBH,W,X,'
    'W,X,S,X,X,N,X,X,'
    'SW,X,NEGC,W,X,X,X,X,'
    'NW,S,X,X,X,X,E,SWRT,'
    'WE,NWYQ,X,X,X,X,X,NS,'
    'W,X,X,X,X,X,E,NW'
)

QUAD_4B = (
    'NW,N,N,NE,NW,N,N,N,'
    'WE,SWRT,X,X,X,X,S,X,'
    'W,N,X,X,X,X,NEGC,W,'
    'W,X,X,X,X,X,X,X,'
    'W,X,SEBH,W,X,X,X,S,'
    'SW,X,N,X,X,X,E,NWYQ,'
    'NW,X,X,X,X,X,X,S,'
    'W,X,X,X,X,X,E,NW'
)

QUADS = [
    (QUAD_1A, QUAD_1B),
    (QUAD_2A, QUAD_2B),
    (QUAD_3A, QUAD_3B),
    (QUAD_4A, QUAD_4B),
]

# Rotation
ROTATE_QUAD = [
    56, 48, 40, 32, 24, 16,  8,  0, 
    57, 49, 41, 33, 25, 17,  9,  1, 
    58, 50, 42, 34, 26, 18, 10,  2, 
    59, 51, 43, 35, 27, 19, 11,  3, 
    60, 52, 44, 36, 28, 20, 12,  4, 
    61, 53, 45, 37, 29, 21, 13,  5, 
    62, 54, 46, 38, 30, 22, 14,  6, 
    63, 55, 47, 39, 31, 23, 15,  7,
]

ROTATE_WALL = {
    NORTH: EAST,
    EAST: SOUTH,
    SOUTH: WEST,
    WEST: NORTH,
}

# Helper Functions
def idx(x, y, size=16):
    return y * size + x

def xy(index, size=16):
    x = index % size
    y = index / size
    return (x, y)

def rotate_quad(data, times=1):
    for i in range(times):
        result = [data[index] for index in ROTATE_QUAD]
        result = [''.join(ROTATE_WALL.get(c, c) for c in x) for x in result]
        data = result
    return data

def create_grid(quads=None):
    if quads is None:
        quads = [random.choice(pair) for pair in QUADS]
        random.shuffle(quads)
    quads = [quad.split(',') for quad in quads]
    quads = [rotate_quad(quads[i], i) for i in [0, 1, 3, 2]]
    result = [None for i in range(16 * 16)]
    for i, quad in enumerate(quads):
        dx, dy = xy(i, 2)
        for j, data in enumerate(quad):
            x, y = xy(j, 8)
            x += dx * 8
            y += dy * 8
            index = idx(x, y)
            result[index] = data
    return result

def to_mask(cell):
    result = 0
    for letter, mask in M_LOOKUP.items():
        if letter in cell:
            result |= mask
    return result

# Game
class Game(object):
    @staticmethod
    def hardest():
        quads = [QUAD_2B, QUAD_4B, QUAD_3B, QUAD_1B]
        robots = [226, 48, 43, 18]
        token = 'BT'
        return Game(quads=quads, robots=robots, token=token)
    def __init__(self, seed=None, quads=None, robots=None, token=None):
        if seed:
            random.seed(seed)
        self.grid = create_grid(quads)
        if robots is None:
            self.robots = self.place_robots()
        else:
            self.robots = dict(zip(COLORS, robots))
        self.token = token or random.choice(TOKENS)
        self.moves = 0
        self.last = None
    def place_robots(self):
        result = {}
        used = set()
        for color in COLORS:
            while True:
                index = random.randint(0, 255)
                if index in (119, 120, 135, 136):
                    continue
                if self.grid[index][-2:] in TOKENS:
                    continue
                if index in used:
                    continue
                result[color] = index
                used.add(index)
                break
        return result
    def get_robot(self, index):
        for color, position in self.robots.iteritems():
            if position == index:
                return color
        return None
    def can_move(self, color, direction):
        if self.last == (color, REVERSE[direction]):
            return False
        index = self.robots[color]
        if direction in self.grid[index]:
            return False
        new_index = index + OFFSET[direction]
        if new_index in self.robots.itervalues():
            return False
        return True
    def compute_move(self, color, direction):
        index = self.robots[color]
        robots = self.robots.values()
        while True:
            if direction in self.grid[index]:
                break
            new_index = index + OFFSET[direction]
            if new_index in robots:
                break
            index = new_index
        return index
    def do_move(self, color, direction):
        start = self.robots[color]
        last = self.last
        if last == (color, REVERSE[direction]):
            raise Exception
        end = self.compute_move(color, direction)
        if start == end:
            raise Exception
        self.moves += 1
        self.robots[color] = end
        self.last = (color, direction)
        return (color, start, last)
    def undo_move(self, data):
        color, start, last = data
        self.moves -= 1
        self.robots[color] = start
        self.last = last
    def get_moves(self, colors=None):
        result = []
        colors = colors or COLORS
        for color in colors:
            for direction in DIRECTIONS:
                if self.can_move(color, direction):
                    result.append((color, direction))
        return result
    def over(self):
        color = self.token[0]
        return self.token in self.grid[self.robots[color]]
    def key(self):
        return tuple(self.robots.itervalues())
    def search(self):
        max_depth = 1
        while True:
            #print 'Searching to depth:', max_depth
            result = self._search([], set(), 0, max_depth)
            if result is not None:
                return result
            max_depth += 1
    def _search(self, path, memo, depth, max_depth):
        if self.over():
            return list(path)
        if depth == max_depth:
            return None
        key = (depth, self.key())
        if key in memo:
            return None
        memo.add(key)
        if depth == max_depth - 1:
            colors = [self.token[0]]
        else:
            colors = None
        moves = self.get_moves(colors)
        for move in moves:
            data = self.do_move(*move)
            path.append(move)
            result = self._search(path, memo, depth + 1, max_depth)
            path.pop(-1)
            self.undo_move(data)
            if result:
                return result
        return None
    def export(self):
        grid = []
        token = None
        robots = [self.robots[color] for color in COLORS]
        for index, cell in enumerate(self.grid):
            mask = to_mask(cell)
            if index in robots:
                mask |= M_ROBOT
            grid.append(mask)
            if self.token in cell:
                token = index
        robot = COLORS.index(self.token[0])
        return {
            'grid': grid,
            'robot': robot,
            'token': token,
            'robots': robots,
        }
