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
MAP_WIDTH = len(game_map[0])
MAP_HEIGHT = len(game_map)
SPF = 0.20 # second per frame.
render_field = copy.deepcopy(game_map)
tank_objs = []
bullet_objs = []
total_time = 0.0
tank_id_pattern = re.compile('([AB])[0-9]{2}')
bullet_id_pattern = re.compile('[0-9]{3}')

def render_to_screen(field):
    for row in field:
        for c in row:
            m = tank_id_pattern.match(c)
            if m and m.group(1) == 'A':
                print '\033[31m' + c + '\033[0m',
            elif m and m.group(1) == 'B':
                print '\033[34m' + c + '\033[0m',
            else:
                print c,
        print

def to_move_vec_form(direction):
    move_vec = {'y': 0, 'x': 0, 'direction': direction}
    if direction == 'left':
        move_vec.update({'y': 0, 'x': -1})
    elif direction == 'right':
        move_vec.update({'y': 0, 'x': 1})
    elif direction == 'up':
        move_vec.update({'y': -1, 'x': 0})
    else: # down
        move_vec.update({'y': 1, 'x': 0})
    return move_vec

def is_not_out_of_bound(n, axis):
    global MAP_HEIGHT, MAP_WIDTH
    if (axis == 'y' and n >= 0 and n < MAP_HEIGHT) or \
            (axis == 'x' and n >= 0 and n < MAP_WIDTH):
        return True
    else:
        return False

def str_to_int(elem_id):
    zero_counter = 0
    output = ''

    for c in elem_id:
        if c == '0':
            zero_counter += 1
        else:
            output += c

    if zero_counter == len(elem_id):
        return 0
    else:
        return int(output)

class TankGenerator():
    def __init__(self, tank, pos, interval):
        self.tank = tank
        self.pos = pos
        self.interval = interval
        self.counter = 0.0
        self.id_bucket = [i for i in range(100, -1, -1)]

    def gen(self, field):
        global tank_objs
        if round(self.counter, 1) == round(self.interval, 1):
            if field[self.pos['y']][self.pos['x']] == '...':
                new_tank = copy.deepcopy(self.tank)
                if new_tank.team == 'A':
                    new_tank.id = str(self.id_bucket.pop())
                elif new_tank.team == 'B':
                    new_tank.id = str(self.id_bucket.pop())
                if len(new_tank.id) == 1:
                    new_tank.id = '0' + new_tank.id
                new_tank.pos.update({'y': self.pos['y'], \
                        'x': self.pos['x']})
                tank_objs.append(new_tank)
            self.counter = 0.0
        else:
            self.counter += SPF

        return tank_objs 

class BulletGenerator():
    def __init__(self, bullet):
        self.bullet = bullet
        self.id_bucket = [i for i in range(100, -1, -1)]

    def gen(self, pos, move_vec, field):
        global bullet_objs
        y = pos['y'] + move_vec['y']
        x = pos['x'] + move_vec['x']

        if is_not_out_of_bound(y, 'y') and is_not_out_of_bound(x, 'x'):
            new_bullet = copy.deepcopy(self.bullet)
            new_bullet.move_vec = move_vec
            new_bullet.id = str(self.id_bucket.pop())
            if len(new_bullet.id) == 1:
                new_bullet.id = '00' + new_bullet.id
            elif len(new_bullet.id) == 2:
                new_bullet.id = '0' + new_bullet.id

            if field[y][x] == '...':
                new_bullet.pos.update({'y': y, 'x': x})
                bullet_objs.append(new_bullet)
            else:
                new_bullet.pos.update({'y': pos['y'], 'x': pos['x']})
                bullet_objs.append(new_bullet)
                new_bullet.check_front_cell_stat(field)
                new_bullet.destroy_target()

        return tank_objs 


class AITank():
    def __init__(self):
        self.id = ''
        self.team = ''
        self.speed = 0.0
        self.move_counter = 0.0
        self.pos = {'y': 0, 'x': 0}
        self.move_vec = {'y': 0, 'x': 0, 'direction': ''}
        self.prob_list = []
        self.is_neigh_cell_free = {'left': False, 'right': False, \
                'up': False, 'down': False}

    def move(self):
        if round(self.move_counter, 1) == round(self.speed, 1):
            self.pos['y'] += self.move_vec['y']
            self.pos['x'] += self.move_vec['x']
            self.move_counter = 0.0
        else:
            self.move_counter += SPF

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
    def is_enemy_in_range(self, field):
        global tank_id_pattern
        test_pos = {
            'y': self.pos['y'] + self.move_vec['y'], 
            'x': self.pos['x'] + self.move_vec['x']}
        cell_id = ''

        while is_not_out_of_bound(test_pos['y'], 'y' ) and \
                is_not_out_of_bound(test_pos['x'], 'x'):
            cell_id = field[test_pos['y']][test_pos['x']]
            is_enemy_found = tank_id_pattern.match(cell_id)

            if is_enemy_found and is_enemy_found.group(1) != self.team:
                return True
            elif cell_id != '...':
                return False
            else:
                test_pos['y'] += self.move_vec['y']
                test_pos['x'] += self.move_vec['x']

        return False

    def is_deadlock(self):
        return self.is_neigh_cell_free.values() == [False, False, False, \
                False]

    def is_collided(self):
        test_pos = {
            'y': self.pos['y'] + self.move_vec['y'],
            'x': self.pos['x'] + self.move_vec['x']}

        if not self.is_neigh_cell_free[self.move_vec['direction']] or \
                not (is_not_out_of_bound(test_pos['y'], 'y') or \
                is_not_out_of_bound(test_pos['x'], 'x')):
            return True
        else:
            return False

    def is_arbitrary_moved(self):
        n = random.randint(0, 4)
        if n == 0:
            return True
        else:
            return False

class Bullet():
    def __init__(self):
        self.id = ''
        self.speed = 0.2
        self.move_counter = 0.0
        self.pos = {'y': 0, 'x': 0}
        self.move_vec = {'y': 0, 'x': 0, 'direction': ''}
        self.is_front_cell_free = False
        self.front_cell_id = ''

    def move(self):
        if float(self.move_counter) == float(self.speed):
            self.pos['y'] += self.move_vec['y']
            self.pos['x'] += self.move_vec['x']
            self.move_counter = 0.0
        else:
            self.move_counter += SPF

    def check_front_cell_stat(self, field):
        y = self.pos['y'] + self.move_vec['y']
        x = self.pos['x'] + self.move_vec['x']
        self.is_front_cell_free = False

        if is_not_out_of_bound(y, 'y') and is_not_out_of_bound(x, 'x'):
            if field[y][x] == '...':
                self.is_front_cell_free = True
            self.front_cell_id = field[y][x]

    def destroy_itself(self):
        global bullet_objs, bullet_gen, game_map, render_field
        y = self.pos['y']
        x = self.pos['x']

        bullet_gen.id_bucket.append(str_to_int(self.id))

        for b in bullet_objs:
            if b.id == self.id:
                bullet_objs.remove(b)
        game_map[y][x] = '...'
        render_field[y][x] = '...'

    def destroy_target(self):
        global tank_objs, tank_id_pattern, bullet_id_pattern, game_map, \
                render_field, tank_genA, tank_genB, bullet_gen
        y = self.pos['y'] + self.move_vec['y']
        x = self.pos['x'] + self.move_vec['x']
        is_tank = tank_id_pattern.match(self.front_cell_id)
        is_bullet = bullet_id_pattern.match(self.front_cell_id)

        if is_tank:
            self.remove_tank_from_list(self.front_cell_id, y, x)
        elif is_bullet:
            self.remove_bullet_from_list(self.front_cell_id, y, x)
        elif self.front_cell_id == 'BRK':
            game_map[y][x] = '...'
            render_field[y][x] = '...'

    def remove_tank_from_list(self, front_cell_id, y, x):
        global tank_objs, game_map, render_field, tank_genA, tank_genB
        for t in tank_objs:
            if front_cell_id == t.team + t.id:
                if t.team == 'A':
                    tank_genA.id_bucket.append(str_to_int(t.id[1:]))
                elif t.team == 'B':
                    tank_genB.id_bucket.append(str_to_int(t.id[1:]))
                tank_objs.remove(t)
        game_map[y][x] = '...'
        render_field[y][x] = '...'

    def remove_bullet_from_list(self, front_cell_id, y, x):
        global bullet_objs, game_map, render_field, bullet_gen
        for b in bullet_objs:
            if front_cell_id == b.id:
                bullet_gen.id_bucket.append(str_to_int(b.id))
                bullet_objs.remove(b)
        game_map[y][x] = '...'
        render_field[y][x] = '...'

# setup tank prototypes.
tB = AITank()
tB.id = ''
tB.team = 'B'
tB.speed = 1.0
tB.move_vec = {'y': 1, 'x': 0, 'direction': 'down'}
tB.prob_list = ['left', 'left', 'right', 'right', 'up', 'down', \
        'down', 'down', 'down']

tA = AITank()
tA.id = ''
tA.team = 'A'
tA.speed = 1.0
tA.move_vec = {'y': -1, 'x': 0, 'direction': 'up'}
tA.prob_list = ['left', 'left', 'right', 'right', 'down', 'up', \
        'up', 'up', 'up']

b = Bullet()
bullet_gen = BulletGenerator(b)

# initiate game.
tank_genB = TankGenerator(tB, {'y': 0, 'x': 6}, 0.0)
tank_genA = TankGenerator(tA, {'y': 9, 'x': 3}, 0.0)
tank_genB.gen(render_field)
tank_genA.gen(render_field)
for t in tank_objs:
    render_field[t.pos['y']][t.pos['x']] = t.team + t.id

print "time:", total_time, "s."
render_to_screen(render_field)

tank_genB.interval = 2.0
tank_genA.interval = 2.0

# game loop.
while True:
    time.sleep(SPF)
    total_time += SPF
    print "time:", total_time, "s."

    if len(tank_objs) != 0:
        for t in tank_objs:
            if t.is_enemy_in_range(render_field):
                bullet_gen.gen(copy.deepcopy(t.pos), \
                        copy.deepcopy(t.move_vec), render_field)
            else:
                prev_pos = copy.deepcopy(t.pos)
                t.check_neigh_cells_stat(render_field)
                if t.is_collided() or t.is_arbitrary_moved():
                    t.rand_move_vec()
                if not t.is_deadlock():
                    t.move()
                    render_field[prev_pos['y']][prev_pos['x']] = \
                            game_map[prev_pos['y']][prev_pos['x']]
                render_field[t.pos['y']][t.pos['x']] = t.team + t.id

    if len(bullet_objs) != 0:
        for b in bullet_objs:
            prev_bullet_pos = copy.deepcopy(b.pos)
            b.check_front_cell_stat(render_field)
            if not b.is_front_cell_free:
                b.destroy_target()
                b.destroy_itself()
            else:
                b.move()
                render_field[prev_bullet_pos['y']][prev_bullet_pos['x']] = \
                        game_map[prev_bullet_pos['y']][prev_bullet_pos['x']]
                render_field[b.pos['y']][b.pos['x']] = b.id

    render_to_screen(render_field)
    tank_genB.gen(render_field)
    tank_genA.gen(render_field)
