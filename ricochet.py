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
        ('grid', c_uint * 256),
        ('moves', c_uint * 4 * 256),
        ('robots', c_uint * 4),
        ('tokens', c_uint * 4),
        ('last', c_uint),
    ]

CALLBACK_FUNC = CFUNCTYPE(None, c_uint, c_uint, c_uint, c_uint)

def search(model, callback=None):
    callback = CALLBACK_FUNC(callback) if callback else None
    game = Game()
    game.last = 0
    grid = [0x0f] * 256
    for index in xrange(model.width * model.height):
        x, y = model.xy(index)
        grid[y * 16 + x] = model.get_mask(index)
    for i, value in enumerate(grid):
        game.grid[i] = value
    for i, value in enumerate(model.robots):
        if value < 0:
            game.robots[i] = 0xff
        else:
            x, y = model.xy(value)
            game.robots[i] = y * 16 + x
    for i, value in enumerate(model.tokens):
        if value < 0:
            game.tokens[i] = 0xff
        else:
            x, y = model.xy(value)
            game.tokens[i] = y * 16 + x
    path = create_string_buffer(256)
    depth = dll.search(byref(game), path, callback)
    result = []
    for value in path.raw[:depth]:
        value = ord(value)
        color = COLORS[(value >> 4) & 0x0f]
        direction = DIRECTIONS[value & 0x0f]
        result.append((color, direction))
    return result
