#!/usr/bin/env python
import random
import time
import copy

field = [[".","B","B",".",".",".",".",".",".","."],
        [".",".",".",".",".",".",".",".",".","."],
        [".",".",".",".",".",".",".",".",".","."],
        [".","B","B",".","B",".","B",".",".","."],
        [".",".",".",".","B",".","B",".",".","."],
        [".","B","B",".","B",".","B",".",".","."],
        [".","B","B",".","B",".","B",".",".","."],
        [".",".",".",".","B",".","B",".",".","."],
        [".",".",".",".",".",".",".",".",".","."],
        [".",".",".",".",".","B","B","B",".","B"],
        [".",".",".",".",".",".",".",".",".","B"]]
r = 1
tx = 0
ty = 0
move_vec = [0, 0]

# render all game elements to screen.
def screen_render(temp_field):
    for row in temp_field:
        for c in row:
            print c,
        print

# random move_vec, where input l = [is_left_free, is_right_free, is_up_free
# , is_down_free].
def rand_move(l):
    prob_list = [0, 0, 1, 1, 2, 3, 3, 3, 3]

    # random new direction according to prob_list.
    n = prob_list[random.randint(0, 8)]
    while l[n] == False:
        n = prob_list[random.randint(0, 8)]

    # 0 =  decision to go left, 1 = decision to go right, 2 = decision to go up
	# , 3 = decision to go down
	# move vector [ty][tx]
    if n == 0:
        move_vec = [0, -1]
    elif n == 1:
        move_vec = [0, 1]
    elif n == 2:
        move_vec = [-1, 0]
    else:
        move_vec = [1, 0]

    return move_vec

def check_neigh_cell(tx, ty, temp_field):
    neigh_cells = [False, False, False, False]
    if tx - 1 >= 0 and temp_field[ty][tx - 1] == '.':
        neigh_cells[0] = True
    if tx + 1 <= 9 and temp_field[ty][tx + 1] == '.':
        neigh_cells[1] = True
    if ty - 1 >= 0 and temp_field[ty - 1][tx] == '.':
        neigh_cells[2] = True
    if ty + 1 <= 9 and temp_field[ty + 1][tx] == '.':
        neigh_cells[3] = True

    return neigh_cells

def is_collided(self): 
	if (not self.is_neigh_cell_free[self.move_vector['direction']]) or \
		((self.move_vec['x'] == -1) and self.pos['x'] == 0) or \
		((self.move_vec['x'] == 1) and self.pos['x'] == 9) or \
		((self.move_vec['y'] == -1) and self.pos['y'] == 0) or \
 		((self.move_vec['y'] == 1) and self.pos['y'] == 9): 
		return True 
	else: 
		return False


# initial render
temp_field = copy.deepcopy(field)
temp_field[ty][tx] = "T"
screen_render(temp_field)

# game loop
while True:
    time.sleep(0.5)

    # render field
    temp_field = copy.deepcopy(field)

    # check 4 neigh_cell if free
    neigh_cells = check_neigh_cell(tx, ty, temp_field)
	
    # random move vector
	# if position at move vector is not free then call these lines
	# move to check cordition
    if r == 1 :
        move_vec = copy.deepcopy(rand_move(neigh_cells))
       	r += 1
    print move_vec
    
    # move
    ty, tx = ty + move_vec[0], tx + move_vec[1]

    # render tank
    temp_field[ty][tx] = "T"

    # print out to screen
    screen_render(temp_field)
