#include <stdio.h>

#define NORTH 0x01
#define EAST  0x02
#define SOUTH 0x04
#define WEST  0x08
#define ROBOT 0x10

#define HAS_WALL(x, wall) (x & wall)
#define HAS_ROBOT(x) (x & ROBOT)
#define SET_ROBOT(x) (x |= ROBOT)
#define UNSET_ROBOT(x) (x &= ~ROBOT)

#define PACK_UNDO(robot, start, last) (robot << 16 | start << 8 | last)
#define UNPACK_ROBOT(undo) ((undo >> 16) & 0xff)
#define UNPACK_START(undo) ((undo >> 8) & 0xff)
#define UNPACK_LAST(undo) (undo & 0xff)

#define PACK_MOVE(robot, direction) (robot << 4 | direction)
#define UNPACK_MOVE_ROBOT(move) ((move >> 4) & 0x0f)
#define UNPACK_MOVE_DIRECTION(move) (move & 0x0f)

#define MAX_DEPTH 255

#define bool unsigned char
#define true 1
#define false 0

char* DIRECTION[] = {
    "", "NORTH", "EAST", "", "SOUTH", "", "", "", "WEST"
};

char* COLOR[] = {
    "RED", "GREEN", "BLUE", "YELLOW"
};

unsigned char REVERSE[] = {
    0, SOUTH, WEST, 0, NORTH, 0, 0, 0, EAST
};

unsigned char OFFSET[] = {
    0, -16, 1, 0, 16, 0, 0, 0, -1
};

typedef struct {
    unsigned char grid[256];
    unsigned char robot; // 0-3
    unsigned char token; // 0-255
} Game;

typedef struct {
    unsigned char robots[4]; // 0-255
    unsigned char last[4];   // 0-3
    unsigned char moves;
} State;

bool over(
    Game* game, 
    State* state) 
{
    if (state->robots[game->robot] == game->token) {
        return true;
    }
    else {
        return false;
    }
}

bool can_move(
    Game* game, 
    State* state, 
    unsigned char robot, 
    unsigned char direction) 
{
    if (state->last[robot] == REVERSE[direction]) {
        return false;
    }
    unsigned char index = state->robots[robot];
    if (HAS_WALL(game->grid[index], direction)) {
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
    State* state, 
    unsigned char robot, 
    unsigned char direction) 
{
    unsigned char index = state->robots[robot];
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
    State* state, 
    unsigned char robot, 
    unsigned char direction) 
{
    unsigned char start = state->robots[robot];
    unsigned char end = compute_move(game, state, robot, direction);
    unsigned char last = state->last[robot];
    state->moves++;
    state->robots[robot] = end;
    state->last[robot] = direction;
    UNSET_ROBOT(game->grid[start]);
    SET_ROBOT(game->grid[end]);
    return PACK_UNDO(robot, start, last);
}

void undo_move(
    Game* game, 
    State* state, 
    unsigned int undo) 
{
    unsigned char robot = UNPACK_ROBOT(undo);
    unsigned char start = UNPACK_START(undo);
    unsigned char last = UNPACK_LAST(undo);
    unsigned char end = state->robots[robot];
    state->moves--;
    state->robots[robot] = start;
    state->last[robot] = last;
    SET_ROBOT(game->grid[start]);
    UNSET_ROBOT(game->grid[end]);
}

unsigned char _search(
    Game* game, 
    State* state, 
    unsigned char depth, 
    unsigned char max_depth, 
    unsigned char* path) 
{
    if (over(game, state)) {
        return depth;
    }
    if (depth == max_depth) {
        return 0;
    }
    // TODO: check memo
    for (unsigned char robot = 0; robot < 4; robot++) {
        if (depth == max_depth - 1) {
            if (robot != game->robot) {
                continue;
            }
        }
        for (unsigned char shift = 0; shift < 4; shift++) {
            unsigned char direction = 1 << shift;
            if (!can_move(game, state, robot, direction)) {
                continue;
            }
            unsigned int undo = do_move(game, state, robot, direction);
            unsigned char result = _search(
                game, state, depth + 1, max_depth, path
            );
            undo_move(game, state, undo);
            if (result) {
                path[depth] = PACK_MOVE(robot, direction);
                return result;
            }
        }
    }
    return 0;
}

unsigned char search(
    Game* game, 
    State* state, 
    unsigned char* path) 
{
    if (over(game, state)) {
        return 0;
    }
    for (unsigned char max_depth = 1; max_depth < MAX_DEPTH; max_depth++) {
        printf("%d\n", max_depth);
        unsigned char result = _search(game, state, 0, max_depth, path);
        if (result) {
            return result;
        }
    }
    return 0;
}

int main(int argc, char* argv[]) {
    Game game = {
        {9, 1, 1, 3, 9, 1, 1, 1, 1, 1, 3, 9, 1, 1, 1, 3, 8, 0, 16, 0, 16, 2, 12, 0, 2, 12, 0, 0, 16, 0, 4, 2, 8, 4, 0, 0, 0, 0, 1, 16, 0, 1, 0, 0, 0, 0, 3, 10, 8, 3, 8, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 8, 0, 0, 0, 2, 9, 0, 0, 0, 0, 6, 8, 0, 0, 0, 6, 8, 0, 6, 8, 0, 0, 0, 0, 0, 0, 1, 0, 4, 0, 0, 3, 12, 0, 1, 0, 0, 0, 0, 4, 4, 0, 0, 2, 9, 0, 0, 2, 9, 0, 0, 0, 0, 0, 2, 9, 3, 8, 0, 0, 0, 0, 0, 2, 8, 0, 4, 0, 2, 12, 2, 12, 6, 8, 0, 0, 4, 0, 0, 2, 8, 2, 9, 0, 0, 1, 0, 1, 1, 0, 0, 0, 3, 8, 0, 6, 8, 0, 0, 0, 0, 0, 0, 0, 2, 12, 0, 0, 0, 0, 0, 3, 12, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0, 0, 0, 0, 0, 2, 9, 0, 0, 0, 4, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 8, 0, 0, 0, 3, 8, 0, 0, 0, 4, 0, 0, 0, 0, 6, 10, 8, 6, 8, 0, 0, 0, 0, 0, 2, 9, 0, 0, 0, 0, 1, 2, 12, 5, 4, 4, 4, 6, 12, 4, 4, 4, 6, 12, 4, 4, 4, 6}, 
        2, 
        169
    };
    State state = {
        {39, 20, 28, 18},
        {0, 0, 0, 0},
        0
    };
    unsigned char path[MAX_DEPTH] = {0};
    unsigned char depth = search(&game, &state, path);
    for (unsigned char index = 0; index < depth; index++) {
        char* color = COLOR[UNPACK_MOVE_ROBOT(path[index])];
        char* direction = DIRECTION[UNPACK_MOVE_DIRECTION(path[index])];
        printf("%s %s\n", color, direction);
    }
    return 0;
}
