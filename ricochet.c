#include <stdio.h>
#include <stdlib.h>

#define MAX_DEPTH 32

#define NORTH 0x01
#define EAST  0x02
#define SOUTH 0x04
#define WEST  0x08
#define ROBOT 0x10

#define HAS_WALL(x, wall) (x & wall)
#define HAS_ROBOT(x) (x & ROBOT)
#define SET_ROBOT(x) (x |= ROBOT)
#define UNSET_ROBOT(x) (x &= ~ROBOT)

#define PACK_MOVE(robot, direction) (robot << 4 | direction)
#define PACK_UNDO(robot, start, last) (robot << 16 | start << 8 | last)
#define UNPACK_ROBOT(undo) ((undo >> 16) & 0xff)
#define UNPACK_START(undo) ((undo >> 8) & 0xff)
#define UNPACK_LAST(undo) (undo & 0xff)
#define MAKE_KEY(x) (x[0] | (x[1] << 8) | (x[2] << 16) | (x[3] << 24))

#define bool unsigned int
#define true 1
#define false 0

unsigned char REVERSE[] = {
    0, SOUTH, WEST, 0, NORTH, 0, 0, 0, EAST
};

unsigned char OFFSET[] = {
    0, -16, 1, 0, 16, 0, 0, 0, -1
};

typedef struct {
    unsigned char grid[256];
    unsigned char robots[4];
    unsigned char robot;
    unsigned char token;
    unsigned char last;
} Game;

typedef struct {
    unsigned int mask;
    unsigned int size;
    unsigned int* data;
} Set;

unsigned int hash(unsigned int key) {
    key = ~key + (key << 15);
    key = key ^ (key >> 12);
    key = key + (key << 2);
    key = key ^ (key >> 4);
    key = key * 2057;
    key = key ^ (key >> 16);
    return key;
}

void set_alloc(Set* set, unsigned int count) {
    for (unsigned int i = 0; i < count; i++) {
        set->mask = 0xfff;
        set->size = 0;
        set->data = calloc(set->mask + 1, sizeof(unsigned int));
        set++;
    }
}

void set_free(Set* set, unsigned int count) {
    for (unsigned int i = 0; i < count; i++) {
        free(set->data);
        set++;
    }
}

void set_grow(Set* set);

bool set_add(Set* set, unsigned int key) {
    if (set->size * 2 > set->mask) {
        set_grow(set);
    }
    unsigned int index = hash(key) & set->mask;
    while (true) {
        unsigned int entry = set->data[index];
        if (entry == key) {
            return false;
        }
        if (entry == 0) {
            set->size++;
            set->data[index] = key;
            return true;
        }
        index = (index + 1) & set->mask;
    }
}

void set_grow(Set* set) {
    Set new_set;
    new_set.mask = (set->mask << 1) | 1;
    new_set.size = 0;
    new_set.data = calloc(new_set.mask + 1, sizeof(unsigned int));
    for (unsigned int index = 0; index <= set->mask; index++) {
        unsigned int key = set->data[index];
        if (key != 0) {
            set_add(&new_set, key);
        }
    }
    free(set->data);
    set->mask = new_set.mask;
    set->size = new_set.size;
    set->data = new_set.data;
}

bool game_over(Game* game) {
    if (game->robots[game->robot] == game->token) {
        return true;
    }
    else {
        return false;
    }
}

bool can_move(
    Game* game, 
    unsigned char robot, 
    unsigned char direction) 
{
    unsigned char index = game->robots[robot];
    if (HAS_WALL(game->grid[index], direction)) {
        return false;
    }
    if (game->last == PACK_MOVE(robot, REVERSE[direction])) {
        return false;
    }
    unsigned char new_index = index + OFFSET[direction];
    if (HAS_ROBOT(game->grid[new_index])) {
        return false;
    }
    return true;
}

unsigned char compute_move(
    Game* game, 
    unsigned char robot, 
    unsigned char direction) 
{
    unsigned char index = game->robots[robot];
    while (true) {
        if (HAS_WALL(game->grid[index], direction)) {
            break;
        }
        unsigned char new_index = index + OFFSET[direction];
        if (HAS_ROBOT(game->grid[new_index])) {
            break;
        }
        index = new_index;
    }
    return index;
}

unsigned int do_move(
    Game* game, 
    unsigned char robot, 
    unsigned char direction) 
{
    unsigned char start = game->robots[robot];
    unsigned char end = compute_move(game, robot, direction);
    unsigned char last = game->last;
    game->robots[robot] = end;
    game->last = PACK_MOVE(robot, direction);
    UNSET_ROBOT(game->grid[start]);
    SET_ROBOT(game->grid[end]);
    return PACK_UNDO(robot, start, last);
}

void undo_move(
    Game* game, 
    unsigned int undo) 
{
    unsigned char robot = UNPACK_ROBOT(undo);
    unsigned char start = UNPACK_START(undo);
    unsigned char last = UNPACK_LAST(undo);
    unsigned char end = game->robots[robot];
    game->robots[robot] = start;
    game->last = last;
    SET_ROBOT(game->grid[start]);
    UNSET_ROBOT(game->grid[end]);
}

unsigned int _nodes;
unsigned int _hits;
unsigned int _inner;

unsigned int _search(
    Game* game, 
    unsigned int depth, 
    unsigned int max_depth, 
    unsigned char* path,
    Set* sets) 
{
    if (depth == 0) {
        _nodes = 0;
        _hits = 0;
        _inner = 0;
    }
    _nodes++;
    if (game_over(game)) {
        return depth;
    }
    if (depth == max_depth) {
        return 0;
    }
    _inner++;
    if (!set_add(&sets[max_depth - depth - 1], MAKE_KEY(game->robots))) {
        _hits++;
        return 0;
    }
    for (unsigned char robot = 0; robot < 4; robot++) {
        if (depth == max_depth - 1) {
            if (robot != game->robot) {
                continue;
            }
        }
        for (unsigned char shift = 0; shift < 4; shift++) {
            unsigned char direction = 1 << shift;
            if (!can_move(game, robot, direction)) {
                continue;
            }
            unsigned int undo = do_move(game, robot, direction);
            unsigned int result = _search(
                game, depth + 1, max_depth, path, sets
            );
            undo_move(game, undo);
            if (result) {
                path[depth] = PACK_MOVE(robot, direction);
                return result;
            }
        }
    }
    return 0;
}

unsigned int search(
    Game* game, 
    unsigned char* path,
    void (*callback)(unsigned int, unsigned int, unsigned int, unsigned int)) 
{
    if (game_over(game)) {
        return 0;
    }
    unsigned int result = 0;
    Set sets[MAX_DEPTH];
    set_alloc(sets, MAX_DEPTH);
    for (unsigned int max_depth = 1; max_depth < MAX_DEPTH; max_depth++) {
        result = _search(game, 0, max_depth, path, sets);
        if (callback) {
            callback(max_depth, _nodes, _inner, _hits);
        }
        if (result) {
            break;
        }
    }
    set_free(sets, MAX_DEPTH);
    return result;
}

int main(int argc, char* argv[]) {
    Game game = {
        {9, 1, 5, 1, 3, 9, 1, 1, 1, 3, 9, 1, 1, 1, 1, 3, 8, 2, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 8, 6, 8, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 1, 0, 3, 8, 0, 0, 0, 0, 2, 12, 0, 2, 9, 0, 0, 0, 0, 4, 2, 12, 0, 0, 0, 4, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3, 10, 9, 0, 0, 0, 3, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 8, 6, 8, 0, 0, 0, 0, 4, 4, 0, 0, 2, 12, 0, 0, 2, 8, 1, 0, 0, 0, 0, 2, 9, 3, 8, 0, 0, 1, 0, 0, 2, 8, 0, 4, 0, 2, 12, 2, 12, 6, 8, 0, 0, 0, 0, 0, 6, 8, 18, 9, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 4, 0, 3, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 9, 0, 2, 28, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 8, 0, 0, 0, 2, 9, 0, 0, 0, 4, 0, 0, 0, 0, 0, 1, 0, 0, 2, 12, 2, 8, 0, 0, 16, 3, 8, 0, 0, 0, 4, 0, 0, 0, 0, 1, 2, 8, 6, 8, 0, 0, 0, 0, 0, 0, 3, 8, 0, 0, 0, 16, 2, 12, 5, 4, 4, 4, 6, 12, 4, 4, 4, 4, 6, 12, 4, 4, 6},
        {145, 211, 176, 238},
        2,
        54,
        0
    };
    unsigned char path[32];
    search(&game, path, 0);
}
