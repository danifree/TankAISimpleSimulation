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

class Tank:
	def __init__(self):
		self.pos = {'y': 0, 'x': 0}
		self.move_vec = {'y': 0, 'x': 0, 'direction': ''}
		self.prob_list = ['left', 'left', 'right', 'right', 'up', 'down', 'down', 'down', 'down']
		self.is_neigh_cell_free = {'left': False, 'right': False, 'up': False, 'down': False}

	def move(self):
		self.pos['y'] = self.pos['y'] + self.move_vec['y']
		self.pos['x'] = self.pos['x'] + self.move_vec['x']

	def check_neigh_cells(self, field):
		self.is_neigh_cell_free = {'left': False, 'right': False, 'up': False, 'down': False}
		x = self.pos['x']
		y = self.pos['y']

		if x - 1 >= 0 and field[y][x - 1] == '.':
			self.is_neigh_cell_free['left'] = True
		if x + 1 <= 9 and field[y][x + 1] == '.':
			self.is_neigh_cell_free['right'] = True
		if y - 1 >= 0 and field[y - 1][x] == '.':
			self.is_neigh_cell_free['up'] = True
		if y + 1 <= 9 and field[y + 1][x] == '.':
			self.is_neigh_cell_free['down'] = True

	def rand_move_vec(self):
		n = self.prob_list[random.randint(0, 8)]
		while self.is_neigh_cell_free[n] == False:
			n = self.prob_list[random.randint(0, 8)]
		
		if n == 'left':
			self.move_vec['y'] = 0 
			self.move_vec['x'] = -1
			self.move_vec['direction'] = n	
		elif n == 'right':
			self.move_vec['y'] = 0 
			self.move_vec['x'] = 1
			self.move_vec['direction'] = n	
		elif n == 'up':
			self.move_vec['y'] = -1 
			self.move_vec['x'] = 0
			self.move_vec['direction'] = n	
		else:
			self.move_vec['y'] = 1 
			self.move_vec['x'] = 0
			self.move_vec['direction'] = n	

# render all game elements to the screen.
def screen_render(field):
	for row in field:
		for c in row:
			print c,
		print

# initial render.
# create AI tank.
t = Tank()
t.pos = {'y': 0, 'x': 0}
t.move_vec = {'y': 1, 'x': 0, 'direction': 'down'}

# render game field and AI tank.
render_field = copy.deepcopy(field)
render_field[t.pos['y']][t.pos['x']] = 'T'

# print all rendered elements to screen.
screen_render(render_field)

# game loop.
while True:
	time.sleep(0.5)

	# render field.
	render_field = copy.deepcopy(field)

	# tanks check 4 neighbor cells (left, right, up, down).
	t.check_neigh_cells(render_field)

	# tanks random new moving direction if one of conditions is true.
	#if t.is_collided() or t.is_arbitrary_moved():
	#	 t.random_move_vec()
	t.rand_move_vec()

	# tanks move.
	t.move()

	# move tank in the field.
	render_field[t.pos['y']][t.pos['x']] = 'T'

	# print all rendered elements to screen.
	screen_render(render_field)

	# print some information for debugging.
	print 'is_neigh_cell_free:', t.is_neigh_cell_free
	print 'move_vec:', t.move_vec
	print 'pos:', t.pos
