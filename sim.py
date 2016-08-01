#!/usr/bin/env python
import random
import time
import copy
import re

# map of game where
# 'BRK' is a brick, 
# 'STL' is a steel,
# '...' is a free space.
game_map = [['...','...','...','...','STL','STL','...','...','...','...'],
            ['...','BRK','...','...','BRK','BRK','...','...','BRK','...'],
            ['...','BRK','...','...','BRK','BRK','...','...','BRK','...'],
            ['...','...','...','...','...','...','...','...','...','...'],
            ['BRK','...','...','BRK','...','...','BRK','...','...','BRK'],
            ['STL','...','...','BRK','...','...','BRK','...','...','STL'],
            ['...','...','...','BRK','...','...','BRK','...','...','...'],
            ['...','BRK','...','BRK','...','...','BRK','...','BRK','...'],
            ['...','BRK','...','...','...','...','...','...','BRK','...'],
            ['...','...','...','...','STL','STL','...','...','...','...']]
map_width = len(game_map[0])
map_height = len(game_map)
id_bucketA = [i for i in range(100, -1, -1)]
id_bucketB = [i for i in range(100, -1, -1)]
tank_objs = []
spf = 1.0 # second per frame.
total_time = 0
id_tank_pattern = re.compile('([AB])[0-9]{2}')

def render_to_screen(field):
    for row in field:
        for c in row:
            m = id_tank_pattern.match(c)
            if m and m.group(1) == 'A':
                print '\033[31m' + c + '\033[0m',
            elif m and m.group(1) == 'B':
                print '\033[34m' + c + '\033[0m',
            else:
                print c,
        print

def gen_AITank(tank, y, x, interval, field):
    global total_time, tank_objs

    if total_time%interval == 0 and field[y][x] == '...':
        new_tank = copy.deepcopy(tank)

        if new_tank.team == 'A':
            new_tank.id = str(id_bucketA.pop())
        elif new_tank.team == 'B':
            new_tank.id = str(id_bucketB.pop())
        if len(new_tank.id) == 1:
            new_tank.id = '0' + new_tank.id

        new_tank.pos.update({'y': y, 'x': x})
        tank_objs.append(new_tank)

def to_move_vec_form(direction):
    move_vec = {'y': 0, 'x': 0, 'direction': direction}
    if direction == 'left':
        move_vec.update({'y': 0, 'x': -1})
    elif direction == 'right':
        move_vec.update({'y': 0, 'x': 1})
    elif direction == 'up':
        move_vec.update({'y': -1, 'x': 0})
    else:
        move_vec.update({'y': 1, 'x': 0})

    return move_vec

def is_not_out_of_bound(n, axis):
    global map_height, map_width

    if (axis == 'y' and n >= 0 and n < map_height) or \
            (axis == 'x' and n >= 0 and n < map_width):
        return True
    else:
        return False

class AITank():
    def __init__(self):
        self.id = ''
        self.team = ''
        self.speed = 0
        self.heart = 0
        self.pos = {'y': 0, 'x': 0}
        self.move_vec = {'y': 0, 'x': 0, 'direction': ''}
        self.prob_list = []
        self.is_neigh_cell_free = {'left': False, 'right': False, \
                'up': False, 'down': False}

    def move(self):
        self.pos['y'] = self.pos['y'] + self.move_vec['y']
        self.pos['x'] = self.pos['x'] + self.move_vec['x']

    def rand_move_vec(self):
        n = self.prob_list[random.randint(0, len(self.prob_list) - 1)]

        if self.is_neigh_cell_free.values() != [False, False, False, False]:
            while not self.is_neigh_cell_free[n]:
                n = self.prob_list[random.randint(0, \
                        len(self.prob_list) - 1)]

        self.move_vec.update(to_move_vec_form(n))

    def check_neigh_cells_stat(self, field):
        y = self.pos['y']
        x = self.pos['x']

        self.is_neigh_cell_free = {'left': False, 'right': False, \
                'up': False, 'down': False}

        if is_not_out_of_bound(x - 1, 'x') and field[y][x - 1] == '...':
            self.is_neigh_cell_free['left'] = True
        if is_not_out_of_bound(x + 1, 'x') and field[y][x + 1] == '...':
            self.is_neigh_cell_free['right'] = True
        if is_not_out_of_bound(y - 1, 'y') and field[y - 1][x] == '...':
            self.is_neigh_cell_free['up'] = True
        if is_not_out_of_bound(y + 1, 'y') and field[y + 1][x] == '...':
            self.is_neigh_cell_free['down'] = True

    # check for an enemy in a straight line.
    def is_enemy_in_range(self, direction, field):
        global id_tank_pattern

        vec = to_move_vec_form(direction)
        test_pos = {
            'y': self.pos['y'] + vec['y'], 
            'x': self.pos['x'] + vec['x']
        }
        cell_id = ''

        while is_not_out_of_bound(test_pos['y'], 'y' ) and \
                is_not_out_of_bound(test_pos['x'], 'x'):
            cell_id = field[test_pos['y']][test_pos['x']]
            is_enemy_found = id_tank_pattern.match(cell_id)

            if is_enemy_found and is_enemy_found.group(1) != self.team:
                return True
            elif cell_id != '...':
                return False
            else:
                test_pos.update({
                    'y': test_pos['y'] + vec['y'], \
                    'x': test_pos['x'] + vec['x'] \
                })

    def is_collided(self):
        if (not self.is_neigh_cell_free[self.move_vec['direction']]) or \
                ((self.move_vec['x'] == -1) and self.pos['x'] == 0) or\
                ((self.move_vec['x'] == 1) and self.pos['x'] == map_width) \
                or \
                ((self.move_vec['y'] == -1) and self.pos['y'] == 0) or\
                ((self.move_vec['y'] == 1) and self.pos['y'] == map_height):
            return True
        else:
            return False

    def is_arbitrary_moved(self):
        n = random.randint(0, 4)

        if n == 0:
            return True
        else:
            return False

# setup tank prototypes.
tB = AITank()
tB.id = ''
tB.team = 'B'
tB.pos = {'y': 0, 'x': 0}
tB.move_vec = {'y': 1, 'x': 0, 'direction': 'down'}
tB.prob_list = ['left', 'left', 'right', 'right', 'up', 'down', \
        'down', 'down', 'down']

tA = AITank()
tA.id = ''
tA.team = 'A'
tA.pos = {'y': 6, 'x': 0}
tA.move_vec = {'y': -1, 'x': 0, 'direction': 'up'}
tA.prob_list = ['left', 'left', 'right', 'right', 'down', 'up', \
        'up', 'up', 'up']

# initiate game.
render_field = copy.deepcopy(game_map)
gen_AITank(tB, 0, 0, 5, render_field)
gen_AITank(tA, 9, 9, 5, render_field)
for t in tank_objs:
    render_field[t.pos['y']][t.pos['x']] = t.team + t.id

print "time:", total_time, "s."
render_to_screen(render_field)

# game loop.
while True:
    time.sleep(spf)
    total_time += spf
    print "time:", total_time, "s."

    if total_time < 30:
        gen_AITank(tB, 0, 0, 5, render_field)
        gen_AITank(tA, 9, 9, 5, render_field)

    if len(tank_objs) != 0:
        for t in tank_objs:
            prev_tank_pos = copy.deepcopy(t.pos)

            t.check_neigh_cells_stat(render_field)

            if t.is_collided() or t.is_arbitrary_moved():
                t.rand_move_vec()

            if not (t.is_enemy_in_range(t.move_vec['direction'], \
                    render_field) or t.is_neigh_cell_free.values() == \
                    [False, False, False, False]):
                t.move()

            render_field[prev_tank_pos['y']][prev_tank_pos['x']] = \
                    game_map[prev_tank_pos['y']][prev_tank_pos['x']]
            render_field[t.pos['y']][t.pos['x']] = t.team + t.id

    render_to_screen(render_field)
