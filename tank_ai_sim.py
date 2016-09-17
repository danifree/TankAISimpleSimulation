#!/usr/bin/env python
import random
import time
import copy
import re
import os

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
states = copy.deepcopy(game_map)
tank_objs = []
bullet_objs = []
total_time = 0.0
tank_id_pattern = re.compile('([AB])[0-9]{2}')
bullet_id_pattern = re.compile('[0-9]{3}')
tank_ids_bucket = [i for i in range(100, -1, -1)]
bullet_ids_bucket = [i for i in range(100, -1, -1)]

def render_to_screen():
    for row in states:
        for c in row:
            m = tank_id_pattern.match(c)
            if m and m.group(1) == 'A':
                print '\033[31m' + c + '\033[0m',
            elif m and m.group(1) == 'B':
                print '\033[34m' + c + '\033[0m',
            else:
                print c,
        print

def to_movevec_form(direction):
    movevec = {'y': 0, 'x': 0, 'direction': direction}
    if direction == 'left':
        movevec.update({'y': 0, 'x': -1})
    elif direction == 'right':
        movevec.update({'y': 0, 'x': 1})
    elif direction == 'up':
        movevec.update({'y': -1, 'x': 0})
    else: # down
        movevec.update({'y': 1, 'x': 0})
    return movevec

def is_not_out_of_map(y, x):
    is_y_test = (y != '')
    is_x_test = (x != '')
    is_y_in_map = False
    is_x_in_map = False

    if is_y_test:
        if y > 0 and y < MAP_HEIGHT:
            is_y_in_map = True
        else:
            is_y_in_map = False
    else:
        is_y_in_map = True

    if is_x_test:
        if x > 0 and x < MAP_WIDTH:
            is_x_in_map = True
        else:
            is_x_in_map = False
    else:
        is_x_in_map = True

    return is_y_in_map == is_x_in_map

def str_to_int_id(elem_id):
    zero_counter = 0
    i = 0

    while i < len(elem_id) and elem_id[i] == '0':
        zero_counter += 1
        i += 1
    if zero_counter == len(elem_id):
        return 0
    else:
        return int(elem_id[i:])

def remove_explosion_symbs():
    j = 0
    while j < MAP_HEIGHT:
        i = 0
        while i < MAP_WIDTH:
            if states[j][i] == '.X.':
                states[j][i] = game_map[j][i]
            i += 1
        j += 1

class AITank():
    def __init__(self):
        self.id = ''
        self.team = ''
        self.speed = 0.0
        self.move_counter = 0.0
        self.pos = {'y': 0, 'x': 0}
        self.movevec = {'y': 0, 'x': 0, 'direction': ''}
        self.prob_list = []
        self.is_neigh_cell_free = {'left': False, 'right': False, \
                'up': False, 'down': False}

    def move(self):
        if round(self.move_counter, 1) == round(self.speed, 1):
            self.pos['y'] += self.movevec['y']
            self.pos['x'] += self.movevec['x']
            self.move_counter = 0.0
        else:
            self.move_counter += SPF

    def rand_movevec(self):
        n = self.prob_list[random.randint(0, len(self.prob_list) - 1)]
        if self.is_neigh_cell_free.values() != [False, False, False, False]:
            while not self.is_neigh_cell_free[n]:
                n = self.prob_list[random.randint(0, \
                        len(self.prob_list) - 1)]
        self.movevec.update(to_movevec_form(n))

    def check_neigh_cells_stat(self):
        y = self.pos['y'] 
        x = self.pos['x']
        self.is_neigh_cell_free = {'left': False, 'right': False, \
                'up': False, 'down': False}

        if is_not_out_of_map('', x - 1) and \
                states[y][x - 1] == '...':
            self.is_neigh_cell_free['left'] = True
        if is_not_out_of_map('', x + 1) and \
                states[y][x + 1] == '...':
            self.is_neigh_cell_free['right'] = True
        if is_not_out_of_map(y - 1, '') and \
                states[y - 1][x] == '...':
            self.is_neigh_cell_free['up'] = True
        if is_not_out_of_map(y + 1, '') and \
                states[y + 1][x] == '...':
            self.is_neigh_cell_free['down'] = True

    # check for an enemy in a straight line.
    def is_enemy_in_range(self):
        test_pos = {
            'y': self.pos['y'] + self.movevec['y'], 
            'x': self.pos['x'] + self.movevec['x']}
        cell_id = ''

        while is_not_out_of_map(test_pos['y'], test_pos['x']):
            cell_id = states[test_pos['y']][test_pos['x']]
            is_enemy_found = tank_id_pattern.match(cell_id)

            if is_enemy_found and is_enemy_found.group(1) != self.team:
                return True
            elif cell_id != '...':
                return False
            else:
                test_pos['y'] += self.movevec['y']
                test_pos['x'] += self.movevec['x']

        return False

    def is_not_deadlock(self):
        return self.is_neigh_cell_free.values() != [False, False, False, \
                False]

    def is_collided(self):
        test_pos = {
            'y': self.pos['y'] + self.movevec['y'],
            'x': self.pos['x'] + self.movevec['x']}

        if not self.is_neigh_cell_free[self.movevec['direction']] or \
                not (is_not_out_of_map(test_pos['y'], '') or \
                is_not_out_of_map('', test_pos['x'])):
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
        self.move_counter = 0.2
        self.pos = {'y': 0, 'x': 0}
        self.movevec = {'y': 0, 'x': 0, 'direction': ''}
        self.is_front_cell_free = False
        self.front_cell_id = ''

    def move(self):
        if float(self.move_counter) == float(self.speed):
            self.pos['y'] += self.movevec['y']
            self.pos['x'] += self.movevec['x']
            self.move_counter = 0.0
        else:
            self.move_counter += SPF

    def check_front_cell_stat(self):
        y = self.pos['y'] + self.movevec['y']
        x = self.pos['x'] + self.movevec['x']
        self.is_front_cell_free = False

        if is_not_out_of_map(y, x):
            if states[y][x] == '...':
                self.is_front_cell_free = True
            self.front_cell_id = states[y][x]

    def destroy_itself(self):
        y = self.pos['y']
        x = self.pos['x']

        bullet_ids_bucket.append(str_to_int_id(self.id))

        for b in bullet_objs:
            if b.id == self.id:
                bullet_objs.remove(b)
        game_map[y][x] = '...'
        states[y][x] = '...'

    def destroy_target(self):
        y = self.pos['y'] + self.movevec['y']
        x = self.pos['x'] + self.movevec['x']
        is_tank = tank_id_pattern.match(self.front_cell_id)
        is_bullet = bullet_id_pattern.match(self.front_cell_id)

        if is_tank:
            self.remove_tank_from_list(self.front_cell_id, y, x)
        elif is_bullet:
            self.remove_bullet_from_list(self.front_cell_id, y, x)
        elif self.front_cell_id == 'BRK':
            game_map[y][x] = '...'
            states[y][x] = '.X.'

    def remove_tank_from_list(self, front_cell_id, y, x):
        for t in tank_objs:
            if front_cell_id == t.team + t.id:
                tank_ids_bucket.append(str_to_int_id(t.id))
                tank_objs.remove(t)
        states[y][x] = '.X.'

    def remove_bullet_from_list(self, front_cell_id, y, x):
        for b in bullet_objs:
            if front_cell_id == b.id:
                bullet_ids_bucket.append(str_to_int_id(b.id))
                bullet_objs.remove(b)
        states[y][x] = '.X.'

class TankGenerator():
    def __init__(self, tank, pos, interval):
        self.tank = tank
        self.pos = pos
        self.interval = interval
        self.counter = 0.0

    def gen(self):
        if round(self.counter, 1) == round(self.interval, 1):
            if states[self.pos['y']][self.pos['x']] == '...':
                new_tank = copy.deepcopy(self.tank)
                new_tank.id = str(tank_ids_bucket.pop())
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

    def gen(self, pos, movevec):
        y = pos['y']
        x = pos['x']

        new_bullet = copy.deepcopy(self.bullet)
        new_bullet.movevec = movevec
        new_bullet.id = str(bullet_ids_bucket.pop())
        if len(new_bullet.id) == 1:
            new_bullet.id = '00' + new_bullet.id
        elif len(new_bullet.id) == 2:
            new_bullet.id = '0' + new_bullet.id
        new_bullet.pos.update({'y': y, 'x': x})
        bullet_objs.append(new_bullet)

# setup tanks and bullet.
tB = AITank()
tB.id = ''
tB.team = 'B'
tB.speed = 1.0
tB.movevec = {'y': 1, 'x': 0, 'direction': 'down'}
tB.prob_list = ['left', 'left', 'right', 'right', 'up', 'down', \
        'down', 'down', 'down']
tA = AITank()
tA.id = ''
tA.team = 'A'
tA.speed = 1.0
tA.movevec = {'y': -1, 'x': 0, 'direction': 'up'}
tA.prob_list = ['left', 'left', 'right', 'right', 'down', 'up', \
        'up', 'up', 'up']

b = Bullet()
bullet_gen = BulletGenerator(b)

# initiate game.
tank_genB = TankGenerator(tB, {'y': 0, 'x': 3}, 0.0)
tank_genA = TankGenerator(tA, {'y': 9, 'x': 6}, 0.0)
tank_genB.gen()
tank_genA.gen()
for t in tank_objs:
    states[t.pos['y']][t.pos['x']] = t.team + t.id

print "time:", total_time, "s."
render_to_screen()

tank_genB.interval = 2.0
tank_genA.interval = 2.0

# game loop.
while True:
    time.sleep(SPF)
    total_time += SPF
    os.system('clear')
    print "time:", total_time, "s."

    remove_explosion_symbs()

    if len(tank_objs) != 0:
        for t in tank_objs:
            if t.is_enemy_in_range():
                states[t.pos['y']][t.pos['x']] = t.team + t.id
                bullet_gen.gen(copy.deepcopy(t.pos), \
                        copy.deepcopy(t.movevec))
            else:
                prev_pos = copy.deepcopy(t.pos)
                t.check_neigh_cells_stat()
                if t.is_collided() or t.is_arbitrary_moved():
                    t.rand_movevec()
                if t.is_not_deadlock():
                    t.move()
                    states[prev_pos['y']][prev_pos['x']] = \
                            game_map[prev_pos['y']][prev_pos['x']]
                states[t.pos['y']][t.pos['x']] = t.team + t.id

    if len(bullet_objs) != 0:
        for b in bullet_objs:
            b.check_front_cell_stat()
            if b.is_front_cell_free:
                prev_pos = copy.deepcopy(b.pos)
                b.move()
                is_not_first_move = bullet_id_pattern.match(states\
                        [prev_pos['y']][prev_pos['x']])
                if is_not_first_move:
                    states[prev_pos['y']][prev_pos['x']] = \
                            game_map[prev_pos['y']][prev_pos['x']]
                states[b.pos['y']][b.pos['x']] = b.id
            else:
                b.destroy_target()
                b.destroy_itself()

    render_to_screen()
    tank_genB.gen()
    tank_genA.gen()
