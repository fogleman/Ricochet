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
        ('last', c_ubyte * 4),
        ('moves', c_ubyte),
    ]

def search(game):
    data = game.export()
    _game = Game()
    _state = State()
    _game.robot = data['robot']
    _game.token = data['token']
    _state.moves = data['moves']
    for index, value in enumerate(data['grid']):
        _game.grid[index] = value
    for index, value in enumerate(data['robots']):
        _state.robots[index] = value
    for index, value in enumerate(data['last']):
        _state.last[index] = value
    path = create_string_buffer(256)
    depth = dll.search(byref(_game), byref(_state), path)
    result = []
    for value in path.raw[:depth]:
        value = ord(value)
        color = COLORS[(value >> 4) & 0x0f]
        direction = DIRECTIONS[value & 0x0f]
        result.append((color, direction))
    return result