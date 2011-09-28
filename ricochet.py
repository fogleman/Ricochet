from ctypes import *

COLORS = {
    0: 'R',
    1: 'G',
    2: 'B',
    3: 'Y',
}

DIRECTIONS = {
    1: 'N',
    2: 'E',
    4: 'S',
    8: 'W',
}

dll = CDLL('_ricochet')

class Game(Structure):
    _fields_ = [
        ('grid', c_ubyte * 256),
        ('robot', c_ubyte),
        ('token', c_ubyte),
    ]

class State(Structure):
    _fields_ = [
        ('robots', c_ubyte * 4),
        ('last', c_ubyte),
        ('moves', c_ubyte),
    ]

def search(game):
    data = game.export()
    _game = Game()
    _state = State()
    _game.robot = data['robot']
    _game.token = data['token']
    _state.moves = data['moves']
    _state.last = data['last']
    for index, value in enumerate(data['grid']):
        _game.grid[index] = value
    for index, value in enumerate(data['robots']):
        _state.robots[index] = value
    path = create_string_buffer(256)
    depth = dll.search(byref(_game), byref(_state), path)
    result = []
    for value in path.raw[:depth]:
        value = ord(value)
        color = COLORS[(value >> 4) & 0x0f]
        direction = DIRECTIONS[value & 0x0f]
        result.append((color, direction))
    return result

if __name__ == '__main__':
    import model
    import time
    import random
    import collections
    count = 0
    best = (0, 0)
    hist = collections.defaultdict(int)
    while True:
        count += 1
        seed = random.randint(0, 0x7fffffff)
        start = time.clock()
        path = search(model.Game(seed))
        moves = len(path)
        hist[moves] += 1
        key = (moves, seed)
        if key > best:
            best = key
        path = [''.join(move) for move in path]
        path = ', '.join(path)
        duration = time.clock() - start
        print '%d. %2d (%.3f) %s [%s]'% (count, moves, duration, best, path)
        print dict(hist)
