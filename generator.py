from editor import Model
import anneal
import random
import ricochet

STEPS = 1000
WIDTH  = 6
HEIGHT = 6
ROBOTS = 4
TOKENS = 4
WALLS = 800
MIRROR_X = True
MIRROR_Y = True
MIRROR_XY = False

def check(model):
    def _check(model, seen, index):
        if seen[index]:
            return
        seen[index] = True
        x, y = model.xy(index)
        if x > 0:
            _check(model, seen, model.index(x - 1, y))
        if y > 0:
            _check(model, seen, model.index(x, y - 1))
        if x < model.width - 1:
            _check(model, seen, model.index(x + 1, y))
        if y < model.height - 1:
            _check(model, seen, model.index(x, y + 1))
    for index in xrange(ROBOTS):
        if model.robots[index] < 0:
            return False
    for index in xrange(TOKENS):
        if model.tokens[index] < 0:
            return False
    seen = [False] * (model.width * model.height)
    _check(model, seen, model.robots[0])
    for index in xrange(ROBOTS):
        if not seen[model.robots[index]]:
            return False
    for index in xrange(TOKENS):
        if not seen[model.tokens[index]]:
            return False
    return True

def move_func(model):
    while True:
        ok = True
        n = random.randint(0, 1)
        if n == 0: # robot
            index = random.randint(0, ROBOTS - 1)
            while True:
                n = random.randint(0, model.width * model.height - 1)
                if n not in model.tokens and n not in model.robots:
                    model.robots[index] = n
                    break
        elif n == 1: # token
            index = random.randint(0, TOKENS - 1)
            while True:
                n = random.randint(0, model.width * model.height - 1)
                if n not in model.tokens and n not in model.robots:
                    model.tokens[index] = n
                    break
        else: # grid
            index = random.randint(0, model.width * model.height - 1)
            wall = 2 ** random.randint(0, 3)
            model.toggle_walls(index, wall, MIRROR_X, MIRROR_Y, MIRROR_XY)
            if model.walls > WALLS:
                model.toggle_walls(index, wall, MIRROR_X, MIRROR_Y, MIRROR_XY)
                ok = False
        if not check(model):
            ok = False
        if ok:
            break

def energy_func(model):
    def callback(depth, nodes, inner, hits):
        print 'Depth: %d, Nodes: %d (%d inner, %d hits)' % (depth, nodes, inner, hits)
    path = ricochet.search(model, None)
    energy = -len(path)
    return energy

def generate(model=None):
    model = model or Model(WIDTH, HEIGHT)
    annealer = anneal.Annealer(energy_func, move_func)
    best_state, _ = annealer.anneal(model, 20, 0.001, STEPS, 9)
    return best_state

def main():
    model = Model(WIDTH, HEIGHT)
    annealer = anneal.Annealer(energy_func, move_func)
    #best_state, best_energy = annealer.auto(model, 1)
    best_state, best_energy = annealer.anneal(model, 20, 0.001, STEPS, 9)
    print best_energy
    print best_state.get_json()

if __name__ == '__main__':
    main()
