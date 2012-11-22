#include <stdio.h>
#include <stdlib.h>
#include <string.h>

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

const unsigned int REVERSE[] = {
    0, SOUTH, WEST, 0, NORTH, 0, 0, 0, EAST
};

const int OFFSET[] = {
    0, -16, 1, 0, 16, 0, 0, 0, -1
};

typedef struct {
    unsigned int grid[256];
    unsigned int token;
} Game;

typedef struct {
    unsigned char robots[4];
    unsigned short depth;
    unsigned short last;
    unsigned int parent;
} State;

typedef struct {
    unsigned int capacity;
    unsigned int size;
    State *data;
} Queue;

typedef struct {
    unsigned int key;
    unsigned int depth;
} Entry;

typedef struct {
    unsigned int mask;
    unsigned int size;
    unsigned int *data;
} Set;

void set_robots(Game *game, State *state) {
    for (unsigned int i = 0; i < 4; i++) {
        SET_ROBOT(game->grid[state->robots[i]]);
    }
}

void unset_robots(Game *game, State *state) {
    for (unsigned int i = 0; i < 4; i++) {
        UNSET_ROBOT(game->grid[state->robots[i]]);
    }
}

void queue_alloc(Queue *queue) {
    queue->size = 0;
    queue->data = (State *)calloc(queue->capacity, sizeof(State));
}

void queue_free(Queue *queue) {
    free(queue->data);
}

void queue_grow(Queue *queue) {
    Queue new_queue;
    new_queue.capacity = queue->capacity * 2;
    queue_alloc(&new_queue);
    memcpy(new_queue.data, queue->data, sizeof(State) * queue->size);
    free(queue->data);
    queue->capacity = new_queue.capacity;
    queue->data = new_queue.data;
}

State *queue_add(Queue *queue, State *state) {
    if (queue->size == queue->capacity - 1) {
        queue_grow(queue);
    }
    State *result = queue->data + queue->size;
    memcpy(result, state, sizeof(State));
    queue->size++;
    return result;
}

inline void swap(unsigned int *array, unsigned int a, unsigned int b) {
    unsigned int temp = array[a];
    array[a] = array[b];
    array[b] = temp;
}

inline unsigned int make_key(State *state) {
    unsigned int robots[4];
    memcpy(robots, state->robots, sizeof(unsigned int) * 4);
    if (robots[1] > robots[2]) {
        swap(robots, 1, 2);
    }
    if (robots[2] > robots[3]) {
        swap(robots, 2, 3);
    }
    if (robots[1] > robots[2]) {
        swap(robots, 1, 2);
    }
    return MAKE_KEY(robots);
}

unsigned int hash(unsigned int key) {
    key = ~key + (key << 15);
    key = key ^ (key >> 12);
    key = key + (key << 2);
    key = key ^ (key >> 4);
    key = key * 2057;
    key = key ^ (key >> 16);
    return key;
}

void set_alloc(Set *set) {
    set->size = 0;
    set->data = (unsigned int *)calloc(set->mask + 1, sizeof(unsigned int));
}

void set_free(Set *set) {
    free(set->data);
}

void set_grow(Set *set);

bool set_add(Set *set, unsigned int key) {
    unsigned int index = hash(key) & set->mask;
    unsigned int *entry = set->data + index;
    while (*entry && *entry != key) {
        index = (index + 1) & set->mask;
        entry = set->data + index;
    }
    if (*entry) {
        return false;
    }
    else {
        *entry = key;
        set->size++;
        if (set->size * 2 > set->mask) {
            set_grow(set);
        }
        return true;
    }
}

void set_grow(Set *set) {
    Set new_set;
    new_set.mask = (set->mask << 2) | 3;
    new_set.size = 0;
    new_set.data = (unsigned int *)calloc(new_set.mask + 1, sizeof(unsigned int));
    for (unsigned int index = 0; index <= set->mask; index++) {
        unsigned int key = set->data[index];
        if (key) {
            set_add(&new_set, key);
        }
    }
    free(set->data);
    set->mask = new_set.mask;
    set->size = new_set.size;
    set->data = new_set.data;
}

inline bool game_over(Game *game, State *state) {
    if (state->robots[0] == game->token) {
        return true;
    }
    else {
        return false;
    }
}

bool can_move(
    Game *game,
    State *state,
    unsigned int robot,
    unsigned int direction)
{
    unsigned int index = state->robots[robot];
    if (HAS_WALL(game->grid[index], direction)) {
        return false;
    }
    if (state->last == PACK_MOVE(robot, REVERSE[direction])) {
        return false;
    }
    unsigned int new_index = index + OFFSET[direction];
    if (HAS_ROBOT(game->grid[new_index])) {
        return false;
    }
    return true;
}

unsigned int compute_move(
    Game *game,
    State *state,
    unsigned int robot,
    unsigned int direction)
{
    unsigned int index = state->robots[robot] + OFFSET[direction];
    while (true) {
        if (HAS_WALL(game->grid[index], direction)) {
            break;
        }
        unsigned int new_index = index + OFFSET[direction];
        if (HAS_ROBOT(game->grid[new_index])) {
            break;
        }
        index = new_index;
    }
    return index;
}

void do_move(
    Game *game,
    State *state,
    unsigned int robot,
    unsigned int direction)
{
    state->robots[robot] = compute_move(game, state, robot, direction);;
    state->last = PACK_MOVE(robot, direction);
}

unsigned int _nodes;
unsigned int _hits;
unsigned int _inner;

unsigned int search(
    Game *game,
    State *state,
    unsigned char *path,
    void (*callback)(unsigned int, unsigned int, unsigned int, unsigned int))
{
    // check if already game over
    if (game_over(game, state)) {
        return 0;
    }
    // bfs queue
    Queue _queue;
    Queue *queue = &_queue;
    queue->capacity = 1 << 20;
    queue_alloc(queue);
    queue_add(queue, state);
    unset_robots(game, state);
    // memoization hash set
    Set _set;
    Set *set = &_set;
    set->mask = 0xfff;
    set_alloc(set);
    // bfs
    unsigned int index = 0;
    while (index < queue->size) {
        state = queue->data + index;
        if (game_over(game, state)) {
            break;
        }
        set_robots(game, state);
        for (unsigned int robot = 0; robot < 4; robot++) {
            for (unsigned int direction = 1; direction <= 8; direction <<= 1) {
                if (!can_move(game, state, robot, direction)) {
                    continue;
                }
                State *child = queue_add(queue, state);
                child->depth = state->depth + 1;
                child->parent = index;
                do_move(game, child, robot, direction);
                if (!set_add(set, make_key(child))) {
                    queue->size--;
                }
            }
        }
        unset_robots(game, state);
        index++;
    }
    // build path
    unsigned int result = state->depth;
    State *temp = state;
    while (true) {
        if (temp->depth == 0) {
            break;
        }
        path[temp->depth - 1] = temp->last;
        temp = queue->data + temp->parent;
    }
    // cleanup
    queue_free(queue);
    set_free(set);
    return result;
}

void _callback(
    unsigned int depth,
    unsigned int nodes,
    unsigned int inner,
    unsigned int hits)
{
    printf("%u %u %u %u\n", depth, nodes, inner, hits);
}

int main(int argc, char *argv[]) {
    // Game game = {
    //     {9, 1, 5, 1, 3, 9, 1, 1, 1, 3, 9, 1, 1, 1, 1, 3, 8, 2, 9, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 8, 6, 8, 0, 0, 0, 0, 0, 0, 0, 0, 4, 0, 0, 0, 1, 0, 3, 8, 0, 0, 0, 0, 2, 12, 0, 2, 9, 0, 0, 0, 0, 4, 2, 12, 0, 0, 0, 4, 0, 1, 0, 0, 0, 0, 0, 0, 0, 3, 10, 9, 0, 0, 0, 3, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 8, 6, 8, 0, 0, 0, 0, 4, 4, 0, 0, 2, 12, 0, 0, 2, 8, 1, 0, 0, 0, 0, 2, 9, 3, 8, 0, 0, 1, 0, 0, 2, 8, 0, 4, 0, 2, 12, 2, 12, 6, 8, 0, 0, 0, 0, 0, 6, 8, 18, 9, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 4, 0, 3, 8, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2, 9, 0, 2, 28, 0, 0, 0, 0, 0, 0, 0, 0, 0, 6, 8, 0, 0, 0, 2, 9, 0, 0, 0, 4, 0, 0, 0, 0, 0, 1, 0, 0, 2, 12, 2, 8, 0, 0, 16, 3, 8, 0, 0, 0, 4, 0, 0, 0, 0, 1, 2, 8, 6, 8, 0, 0, 0, 0, 0, 0, 3, 8, 0, 0, 0, 16, 2, 12, 5, 4, 4, 4, 6, 12, 4, 4, 4, 4, 6, 12, 4, 4, 6},
    //     {0},
    //     {176, 145, 211, 238},
    //     54,
    //     0
    // };
    // unsigned char path[32];
    // search(&game, path, _callback);
}
