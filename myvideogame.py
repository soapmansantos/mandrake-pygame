import pygame, sys, math, random
import numpy as np
from pygame.locals import *
pygame.init()
clock = pygame.time.Clock()
pygame.display.set_caption("Mandrake")
WindowSize = (1200, 800)
#WindowSize = (600, 400)

screen = pygame.display.set_mode(WindowSize, 0, 64)

#display = pygame.Surface((285, 18daa5))
displayx, displayy = 285*3.5, 185*3.5
display = pygame.Surface((displayx, displayy))

restart = False

#text----------------------------------------------------------------------------------------
pygame.font.init()
font = pygame.font.SysFont("VT323", 15)


#loading background----------------------------------------------------------------------------------------
mountains_image = pygame.image.load("background/mountains_background.png").convert()
sea_background = []
for x in range(3):
	img = pygame.image.load(f"background/sea/sea_bg_{x}.png").convert()
	sea_background.append(img)
 


#player----------------------------------------------------------------------------------------
true_scroll = [0, 0]


player_image = pygame.image.load("animations/run/run_0.png").convert() 
player_image.set_colorkey((255,255,255))
player_image = pygame.transform.scale(player_image, (30, 30))

#pointer
pointer_image = pygame.image.load("images/crosshair_.png").convert()
pointer_image.set_colorkey((255,255,255))
pointer_image = pygame.transform.scale(pointer_image, (pointer_image.get_width()*2, pointer_image.get_height()*2))


pointer_rect = pygame.Rect(800, 400, pointer_image.get_width(), pointer_image.get_height())

#particles----------------------------------------------------------------------------------------


class Particles(pygame.sprite.Sprite):
	def __init__(self, x, y, size, speed, min_size, rate, colour):
		pygame.sprite.Sprite.__init__(self)
		self.x = x
		self.y = y
		self.size = size
		self.speed = speed
		self.colour = colour
		self.min_size = min_size
		self.rate = rate

	def update(self, scroll):
		self.x += self.speed[0]
		self.y += self.speed[1]
		self.size -= self.rate

		if self.size <= self.min_size:
			self.kill()

		pygame.draw.rect(display, (self.colour), pygame.Rect(self.x - scroll[0], self.y - scroll[1], self.size, self.size))

particles = pygame.sprite.Group()
bp_colours = [(89, 83, 82), (128, 114, 112), (186, 173, 171), (186, 159, 155)]
ep_colours = [(196, 185, 155), (219, 212, 193), (105, 92, 60), (179, 151, 68)]


#enemies----------------------------------------------------------------------------------------

class Enemies(pygame.sprite.Sprite):
	def __init__(self, x, y):
		pygame.sprite.Sprite.__init__(self)
		self.image = pygame.image.load("enemies/algae_enemy.png").convert()
		self.image.set_colorkey((255, 255, 255))
		self.rect = self.image.get_rect()
		self.x = x
		self.y = y
		self.hit_count = 0
		self.hit_timer = 0
		self.follow = False
		self.speed = 0


	def update(self, targetx, targety, speed, distance, tile_rects, scroll):

		if distance < 250:
			self.follow = True

		if self.follow:
			dx, dy = targetx - self.rect.x, targety - self.rect.y
			dist = math.hypot(dx, dy)
			if dist != 0:
				dx, dy = dx / dist, dy / dist  # Normalize.
		       	# Move along this normalized vector towards the player at current speed.

			dx, dy = dx*speed, dy*speed

			self.x += dx
			self.y += dy

			self.rect.x = int(self.x)   
			self.rect.y = int(self.y)
		else:
			self.rect.x = self.x
			self.rect.y = self.y

		if self.hit_count >= 4:
			self.kill()

		

		hit_list = collision_test(self.rect, tile_rects)	

		for tile in hit_list:
		 	if targetx > self.rect.x:
		 		dx, dy = 0, 0
		 	if targetx < self.rect.x:
		 		dx, dy = 0, 0 

		 

		display.blit(pygame.transform.flip(self.image, enemy_flip, False), (self.rect.x - scroll[0], self.rect.y - scroll[1]))

enemy_speed = 4
enemy_flip = False





#bullets (using sprites)----------------------------------------------------------------------------------------

class Bullet(pygame.sprite.Sprite):
	def __init__(self, x, y, targetx, targety, speed, path):
		pygame.sprite.Sprite.__init__(self)

		self.image = pygame.image.load(f"{path}.png").convert()
		self.image.set_colorkey((255, 255, 255))
		self.rect = self.image.get_rect()
		self.rect.centery = y
		self.rect.centerx = x
		self.speed = speed
		self.targetx = targetx
		self.targety = targety
		angle = math.atan2(targety-y, targetx-x)
		self.dx = math.cos(angle)
		self.dy = math.sin(angle)
		self.image = pygame.transform.rotate(self.image, angle)
		self.x = x
		self.y = y
		self.timer = 0

		self.collide = False
		self.hit_player = False

	def update(self, tile_rects, scroll, player, dashing):


		self.x += self.dx*self.speed
		self.y += self.dy*self.speed

		self.rect.x = int(self.x)
		self.rect.y = int(self.y)


		hit_list = collision_test(self.rect, tile_rects)

		for tile in hit_list:
		 	if self.targetx > self.rect.x:
		 		self.collide = True
		 	if self.targetx < self.rect.x:
		 		self.collide = True
		 	if self.targety > self.rect.y:
		 		self.collide = True
		 	if self.targety < self.rect.y:
		 		self.collide = True

		if self.rect.colliderect(player) and not dashing:
			self.hit_player = True
			for x in range(random.randint(10, 15)):
				particle = Particles(self.rect.x, self.rect.y, random.randint(0, 100)/10, (random.randint(-100, 100)/90, random.randint(-100, 100)/100), 3, 0.5, random.choice(bp_colours))
				particles.add(particle)

		if self.hit_player:
			self.timer += 1
		if self.timer > 1:
			self.kill()


		if self.collide:
			for x in range(random.randint(10, 15)):
				particle = Particles(self.rect.x, self.rect.y, random.randint(0, 100)/10, (random.randint(-100, 100)/90, random.randint(-100, 100)/100), 3, 0.5, random.choice(bp_colours))
				particles.add(particle)
			self.kill()

		if self.collide is False:
			display.blit(pygame.transform.flip(self.image, bullet_flip, False), (self.rect.x - scroll[0], self.rect.y - scroll[1]))



bullet_flip = False
bullets = pygame.sprite.Group()




#objects class----------------------------------------------------------------------------------------

class Objects(pygame.sprite.Sprite):
	def __init__(self, x, y, path):
		pygame.sprite.Sprite.__init__(self)

		self.image = pygame.image.load(f"{path}.png").convert()
		self.image.set_colorkey((255, 255, 255))
		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y
		self.x  = x
		self.y = y
		self.frame = 0
		self.flip = False
		self.in_bounds = False
		self.path = path
		self.timer = 0
		self.timer2 = 0
		self.collide = False
		self.count = 0

		self.leaf_movement = []
		self.leaf_dash = False

	def dash_box(self):
		display.blit(self.image, (self.x - true_scroll[0], self.y - true_scroll[1]))

	def spikes(self):
		if self.path == "tiles/spike_tiles/spike_1":
			self.image = pygame.transform.scale(self.image, (TILE_SIZE/2, TILE_SIZE))
		elif self.path == "tiles/spike_tiles/spike_3":
			self.image = pygame.transform.scale(self.image, (TILE_SIZE/2, TILE_SIZE))
			if self.count < 3:
				self.count += 1
			if self.count == 1:
				self.rect.x += TILE_SIZE/2
				self.x += TILE_SIZE/2
		else:
			self.image = pygame.transform.scale(self.image, (TILE_SIZE, TILE_SIZE/2))


		display.blit(self.image, (self.x - true_scroll[0], self.y - true_scroll[1]))


	def leaf(self, speed):
		self.image = pygame.transform.scale(self.image, (TILE_SIZE - 10, TILE_SIZE - 5))
		self.timer += 1
		if self.timer < 20:
			self.y += speed
		elif self.timer < 40:
			self.y -= speed
		elif self.timer >= 40:
			self.timer = 0


		display.blit(self.image, (self.x - true_scroll[0], self.y - true_scroll[1]))

	def cannon(self, distance, targetx, targety):
		if self.timer == 0:
			bullet = Bullet(self.x, self.y, targetx, targety, 5, "images/red_bullet")
			bullets.add(bullet)
			if distance < 500:
				bullet_sound.play()
		self.timer += 1

		if self.timer >= 40:
			self.timer = 0

		display.blit(self.image, (self.x - true_scroll[0], self.y - true_scroll[1] + 10))


	def leaf_enemy(self, speed, time, target, tile_rects):

		self.leaf_movement = [0, 0]



		self.leaf_movement[1] += 6

		if get_distance(self.rect, target) < 250:
			self.timer2 += 1

			if self.timer2 < 8:
				self.leaf_dash = True
				angle = math.atan2(target.y - self.rect.centery, target.x - self.rect.centerx)
				dx, dy = math.cos(angle), math.sin(angle)
				self.leaf_movement[0] += dx*10
				self.leaf_movement[1] += dy*15

			if self.timer2 >= 8:
				self.leaf_dash = False

			if self.timer2 >= 30:
				self.timer2 = 0

		elif get_distance(self.rect, target) >= 250 or self.timer2 > 8:
			self.timer += 1

			if self.timer <= time:
				self.flip = False
				self.leaf_movement[0] += speed
			elif self.timer <= time*2:
				self.flip = True
				self.leaf_movement[0] -= speed
			elif self.timer > time*2:
				self.timer = 0

		move(self.rect, self.leaf_movement, tile_rects)


		display.blit(pygame.transform.flip(self.image, self.flip, False), (self.rect.x - true_scroll[0], self.rect.y - true_scroll[1]))


#object location----------------------------------------------------------------------------------------


def add_obj(loc, pos, path, group):

	if loc not in pos:
		pos.append(loc)
		group.add(Objects(loc[0], loc[1], path))




#map----------------------------------------------------------------------------------------

def load_map(path):
	f = open(path + ".txt", "r")
	data = f.read()
	f.close()
	data = data.split("\n")
	game_map = []
	for row in data:
		data_split = row.split(",")
		game_map.append(data_split)
	game_map = game_map[:-1]

	for row in range(len(game_map)):
		for i in range(len(game_map[row])):
			game_map[row][i] = str((int(game_map[row][i])+1))
	
	return game_map




#loading tiles------------------------------------------------------------------------------------------


TILE_SIZE = 32
TILE_TYPES = 8
tile_list = []

for x in range(1, TILE_TYPES + 1):
	img = pygame.image.load(f"tiles/rock_tiles/rock_tile_{x}.png").convert()
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img.set_colorkey((255, 255, 255))
	tile_list.append(img)
filler_tile_img = pygame.image.load("tiles/rock_tiles/rock_ground_filler.png").convert()
filler_tile_img = pygame.transform.scale(filler_tile_img, (TILE_SIZE, TILE_SIZE))
tile_list.append(filler_tile_img)



spikes_list = []

for x in range(4):
	img = pygame.image.load(f"tiles/spike_tiles/spike_{x}.png").convert()
	img.set_colorkey((255, 255, 255))
	spikes_list.append(img)



for x in range(TILE_TYPES+1):
	img = pygame.image.load(f"tiles/stone/stone_{x}.png").convert()
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img.set_colorkey((255, 255, 255))
	tile_list.append(img)
stone_filler = pygame.image.load("tiles/stone/stone_filler.png").convert()
stone_filler = pygame.transform.scale(stone_filler, (TILE_SIZE, TILE_SIZE))
tile_list.append(stone_filler)




#moving functions---------------------------------------------------------------------------------------

def collision_test(rect, tiles):
	 hit_list = []
	 for tile in tiles:
	 	if rect.colliderect(tile):
	 		hit_list.append(tile)

	 return hit_list


def move(rect, movement, tiles):
	collision_types = {"top" : False, "bottom" : False, "right" : False, "left" : False}
	rect.x += movement[0]
	hit_list = collision_test(rect, tiles)
	for tile in hit_list:
	 	if movement[0] > 0:
	 		rect.right = tile.left
	 		collision_types["right"] = True
	 	elif movement[0] < 0:
	 		rect.left = tile.right
	 		collision_types["left"] = True

	rect.y += movement[1]
	hit_list = collision_test(rect, tiles)
	for tile in hit_list:
		if movement[1] > 0:
			rect.bottom = tile.top
			collision_types["bottom"] = True
		elif movement[1] < 0:
			rect.top = tile.bottom
			collision_types["top"] = True

	return rect, collision_types

def get_distance(origin, target):
	distance = math.hypot(target[1]-origin[1], target[0]-origin[0])
	return distance

#animations----------------------------------------------------------------------------------------

global animation_frames
animation_frames = {}

def load_animation(path, frame_durations):
	global animation_frames
	animation_name = path.split("/")[-1]
	animation_frame_data = []
	n = 0
	for frame in frame_durations:
		animation_frame_id = animation_name + "_" + str(n)
		img_loc = path + "/" + animation_frame_id + ".png"
		animation_image = pygame.image.load(img_loc).convert()
		animation_image.set_colorkey((255, 255, 255))
		animation_frames[animation_frame_id] = animation_image.copy()
		for i in range(frame):
			animation_frame_data.append(animation_frame_id)
		n += 1

	return animation_frame_data

def change_action(action_var, frame, new_value):
	if action_var != new_value:
		action_var = new_value
		frame = 0
	return action_var, frame

animation_database = {}
	
animation_database["run"] = load_animation("animations/run", [2]*6)
animation_database["idle"] = load_animation("animations/idle", [10]*2)
animation_database["algae_enemy"] = load_animation("animations/algae_enemy", [3]*5)
animation_database["jump"] = load_animation("animations/jump", [4]*9)
animation_database["climb"] = load_animation("animations/climb", [10]*3)
animation_database["dash"] = load_animation("animations/dash", [2]*5)
animation_database["dash_box"] = load_animation("animations/dash_box", [8]*4)
animation_database["leaf_run"] = load_animation("animations/leaf_run", [8]*3)

max_fall = end_dash = False


#sounds and music-------------------------------------------------------------------------------------------------------
pygame.mixer.pre_init(44100, -16, 2, 512)
pygame.mixer.set_num_channels(64)


pygame.mixer.music.load("sfx/music_1.mp3")
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.05)

dash_sound = pygame.mixer.Sound("sfx/dash_sound.wav")
#dash_sound.set_volume(0.4)

jump_sound = pygame.mixer.Sound("sfx/jump_sound.wav")
jump_sound.set_volume(0.4)

slide_jump_sound = pygame.mixer.Sound("sfx/jump_sound.wav")
slide_jump_sound.set_volume(0.4)

slide_sound = pygame.mixer.Sound("sfx/slide_sound.wav")
slide_sound_timer = 0
slide_sound.set_volume(0.1)



grass_sound = [pygame.mixer.Sound("sfx/grass_sound_0.wav"), pygame.mixer.Sound("sfx/grass_sound_1.wav")]
grass_sound[0].set_volume(0.4)
grass_sound[1].set_volume(0.4)

grass_sound_timer = 0

db_sound = pygame.mixer.Sound("sfx/dash_box_sound.wav")

bullet_sound = pygame.mixer.Sound("sfx/shooting_sound.wav")
bullet_sound.set_volume(0.6)

damage_sound = pygame.mixer.Sound("sfx/damage_sound.wav")
damage_sound.set_volume(0.5)

leaf_sound = pygame.mixer.Sound("sfx/leaf_sound.wav")
leaf_sound.set_volume(0.7)

enemy_hit_sound = pygame.mixer.Sound("sfx/enemy_hit2.wav")
enemy_hit_sound.set_volume(0.5)

leaf_e_dash_sound = pygame.mixer.Sound("sfx/leaf_e_dash.wav")
leaf_e_dash_sound.set_volume(0.6)






def main(player_rect, screen_shake, shake_timer, player_acc, movingright, movingleft, player_y_momentum, stomp, slide_jump, slide, slide_dash, slide_timer,
 dash, dash_count, recoil, air_timer, jump, end_dash, player_action, max_fall, enemy_action, enemy_frame, db_action, db_dash, end_dash_timer, leaf_action, player_image, player_flip,
  leaf_count, restart, player_frame, dash_speed, slide_sound_timer, grass_sound_timer, jump_count, enemies, enemy_pos, db_group, db_pos, spikes, spikes_pos, leaves,
   leaf_pos, cannons, cannon_pos, leaf_enemies, leaf_e_pos, life, life_timer, recoil_timer, slide_jump_count, temp, hit, game_map, level, max_depth, ground, particle_timer):

	while True:

		display.fill((0, 0, 0))


		if level < 4 and level != 1:
			max_depth = 1150
		else:
			max_depth = 750

		if player_rect.y < max_depth:
			true_scroll[0] += (player_rect.x - true_scroll[0] - displayx/2) // 15
			true_scroll[1] += (player_rect.y - true_scroll[1] - displayy/2) // 15 


		scroll = true_scroll.copy()
		scroll[0] = int(scroll[0])
		scroll[1] = int(scroll[1])


		

		bg_scroll = [0, 0]

		
		for x in range(len(sea_background)):
			sea_background[x].set_colorkey((255, 255, 255))
			sea_background[x] = pygame.transform.scale(sea_background[x], (WindowSize[0]*(displayx/WindowSize[0])*1.2, WindowSize[1]*(displayy/WindowSize[1])*1.2))

			if x == 0:
				bg_scroll[0] = (-true_scroll[0]/16) % sea_background[x].get_width()
			if x == 1:
				bg_scroll[0] = (-true_scroll[0]/8) % sea_background[x].get_width()
			if x == 2:
				bg_scroll[0] = (-true_scroll[0]/2) % sea_background[x].get_width()

			if bg_scroll[0] < WindowSize[0] + 300:
				display.blit(sea_background[x], (bg_scroll[0], - WindowSize[1]/(displayy/70)))

			display.blit(sea_background[x], (bg_scroll[0] - sea_background[x].get_width(), - WindowSize[1]/(displayy/70)))
		
		tile_rects = []

		
		
		y = 0
		for row in game_map:
			x = 0
			for tile in row:
				if 0 < int(tile) < 20:
					display.blit(tile_list[int(tile)-1], ((x * TILE_SIZE) - true_scroll[0], (y * TILE_SIZE) - true_scroll[1]))
				

				if tile == "20":
					add_obj([(x*TILE_SIZE), (y*TILE_SIZE)], db_pos, "animations/dash_box/dash_box_0", db_group)

				if tile == "21":
					add_obj([(x*TILE_SIZE), (y*TILE_SIZE + TILE_SIZE/2)], spikes_pos, "tiles/spike_tiles/spike_0", spikes)

				if tile == "22":
					if [(x*TILE_SIZE), (y*TILE_SIZE)] not in enemy_pos:
						enemy_pos.append([(x*TILE_SIZE), (y*TILE_SIZE)])
						enemy = Enemies((x*TILE_SIZE), (y*TILE_SIZE))
						enemies.add(enemy)
				

				if tile == "23":
					add_obj([(x*TILE_SIZE), (y*TILE_SIZE)], leaf_pos, "tiles/leaf", leaves)


				if tile == "24":
					add_obj([(x*TILE_SIZE), (y*TILE_SIZE)], cannon_pos, "tiles/cannon", cannons)

				if tile == "25":
					add_obj([(x*TILE_SIZE), (y*TILE_SIZE + TILE_SIZE/4)], leaf_e_pos, "animations/leaf_run/leaf_enemy_img", leaf_enemies)

				if tile == "26":
					add_obj([(x*TILE_SIZE), (y*TILE_SIZE)], spikes_pos, "tiles/spike_tiles/spike_1", spikes)

				if tile == "27":
					add_obj([(x*TILE_SIZE), (y*TILE_SIZE)], spikes_pos, "tiles/spike_tiles/spike_2", spikes)

				if tile == "28":
					add_obj([(x*TILE_SIZE), (y*TILE_SIZE)], spikes_pos, "tiles/spike_tiles/spike_3", spikes)

			


				if tile != "0" and int(tile) < 20:
					tile_rects.append(pygame.Rect((x * TILE_SIZE), (y * TILE_SIZE), TILE_SIZE, TILE_SIZE))

				x += 1
			y += 1

		
		

		if screen_shake:
			shake_timer += 1
			true_scroll[0] += random.randint(-5, 5)
			true_scroll[1] += random.randint(-5, 5)

		if shake_timer >= 15:
			screen_shake = False
			shake_timer = 0


		player_movement = [0, 0]
		
		
		if player_acc < 9 and not slide:
			if movingright:
				player_acc += 0.4
				player_movement[0] += player_acc
			if movingleft:
				player_acc += 0.4
				player_movement[0] -= player_acc
		else:
			if movingright:
				player_movement[0] += 9
			if movingleft:
				player_movement[0] -= 9
		

		
		player_movement[1] += player_y_momentum
		player_y_momentum += 1


		if player_y_momentum > 10:
			player_y_momentum = 12


		if stomp:
			player_y_momentum = 15
			y_scroll_divider = 15


		if slide_jump and slide and not slide_dash:
			player_y_momentum = 0
			slide_sound_timer = 9


		if slide and not slide_jump and not slide_dash:
			slide_sound_timer += 1
			if slide_sound_timer > 10 and not collisions["bottom"]:
				slide_sound.play()
				slide_sound_timer = 0
			if player_y_momentum < 6:
				player_y_momentum += 0.001
			if player_y_momentum >= 6:
				player_y_momentum = 6
			stomp = False
		elif not slide:
			slide_sound_timer = 9


		if slide_dash and slide_timer <= 7:
			slide_timer += 1
			player_y_momentum = -8
			slide_sound_timer = 5
			player_acc = 9
	 

		if slide_timer > 7:
			player_acc = 9
			if player_y_momentum <= -8:
				player_y_momentum += 4
			elif player_y_momentum > 0:
				player_y_momentum = 0
				slide_dash = False
				slide_timer = 0


		if player_movement[0] < 0:
			player_flip = True
		if player_movement[0] > 0:
			player_flip = False



		if dash and dash_count <= 1:

			for x in range(17, 23):
				particle = Particles(player_rect.centerx, player_rect.centery, random.randint(-100, 100)/30, (random.randint(-30, 30)/30, random.randint(-10, 10)/10), random.randint(1, 10)/10, 0.01, (44, 104, 152))
				particles.add(particle) 

			jump = False
			dash_timer += 1
			#air_timer = 0
			if dash_timer < 10: 
				px = dx*dash_speed
				py = dy*dash_speed

				player_movement = [0, 0]
				player_movement[0] += int(px)
				player_movement[1] += int(py)
		

			else:
				player_action = ""
				end_dash = True
				dash_timer = 0
				player_y_momentum = py/8
				px, py = 0, 0
				dash_target = [0, 0]
				dash = False
				stomp = False

		if dash_count > 1:
			dash = False

		
		if recoil and not dash and dash_count <= 1:
			if recoil_timer < 5:
				dx, dy = (player_rect.x + random.randint(-100, 100)) - player_rect.x, (player_rect.y + random.randint(0, 100)) - player_rect.y
				dist = math.hypot(dx, dy)
				if dist != 0:
					dx, dy = dx / dist, dy / dist  # Normalize.

			    # Move along this normalized vector towards the player at current speed.
				dx, dy = dx*10, dy*10

				player_movement[0] -= dx
				player_y_momentum -= dy
				recoil_timer += 1
			elif recoil_timer >= 5:
				player_y_momentum = -5
				if not slide:
					player_acc = 0
				recoil_timer = 0
				recoil = False
		



		player_rect, collisions = move(player_rect, player_movement, tile_rects)



		if collisions["bottom"]:
			player_y_momentum = 0
			air_timer = 0
			stomp = False
			jump = False
			slide = False
			slide_timer = 0
			slide_jump = False
			dash_count = 0
			max_fall = False

			ground = True

			if player_movement[0] != 0:
				grass_sound_timer += 1

				if grass_sound_timer > 6:
					random.choice(grass_sound).play()
					grass_sound_timer = 0
			elif player_movement[0] == 0:
				grass_sound_timer = 5
		else:
			air_timer += 1

		if ground and player_acc == 9:
			player_acc = 3

		if air_timer > 2:
			ground = False



		if collisions["top"]:
			recoil_timer = 0
			recoil = False
			player_y_momentum = 0

		if collisions["right"] and movingright:
			slide = True
		elif collisions["left"] and movingleft:
			slide = True
		if collisions["right"] is False and collisions["left"] is False:
			slide = False




		mx, my = pygame.mouse.get_pos()
		pygame.mouse.set_visible(False)
		pointer_rect.x = mx*(displayx/WindowSize[0])
		pointer_rect.y = my*(displayy/WindowSize[1])




		#idle and running animation
		
		if movingright is False and movingleft is False and collisions["bottom"] and not slide and not dash:
			player_action, player_frame = change_action(player_action, player_frame, "idle")

		
		if player_movement[0] != 0 and not jump and not slide and not dash:
			player_action, player_frame = change_action(player_action, player_frame, "run")

		if jump and not dash and not slide:
			player_action, player_frame = change_action(player_action, player_frame, "jump")

		if (slide_jump or slide_dash or slide) and not collisions["bottom"] and not dash:
			max_fall = False
			player_action, player_frame = change_action(player_action, player_frame, "climb")

		if dash and dash_count <= 1:
			max_fall = False
			player_action, player_frame = change_action(player_action, player_frame, "dash")
		
		if end_dash:
			player_image = pygame.image.load("images/player_image.png").convert_alpha()




		if (air_timer > 5 and not dash and not slide and player_y_momentum > 9):
			max_fall = True
			player_action = ""

		if player_action != "":
			player_frame += 1
			if player_frame >= len(animation_database[player_action]):
				player_frame = 0
			player_image_id = animation_database[player_action][player_frame]
			player_image = animation_frames[player_image_id]

		if max_fall:
			player_image = pygame.image.load("animations/jump/jump_fall.png").convert_alpha()




		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				restart = True
			if event.type == KEYDOWN:
				if event.key == K_d:
					movingright = True

				if event.key == K_a:
					movingleft = True

				if event.key == K_w or event.key == K_SPACE:
					jump = True		
					if air_timer < 5:
						jump_sound.play()
						player_y_momentum = -10

						if not slide:
							#x, y, size, speed, min_size, rate, colour
							for x in range(random.randint(25, 35)):
								particle = Particles(player_rect.centerx, player_rect.centery + player_image.get_height(), random.randint(-100, 100)/15, (random.randint(-5, 30)/40, random.randint(-10, 10)/20), 1, 0.25, (105, 105, 105))
								particles.add(particle)



				if event.key == K_s and collisions["bottom"] is False:
					stomp = True

				if event.key == K_LSHIFT:
					slide_jump = True

				if (event.key == K_w or event.key == K_SPACE) and slide:
					slide_dash = True
					slide_timer = 0
					slide_jump_sound.play()
					for x in range(random.randint(25, 35)):
						particle = Particles(player_rect.centerx, player_rect.y + player_image.get_height(), random.randint(-100, 100)/15, (random.randint(-5, 30)/40, random.randint(-10, 10)/20), 1, 0.25, (105, 105, 105))
						particles.add(particle)

			if event.type == MOUSEBUTTONDOWN:
				if pygame.mouse.get_pressed()[0] and dash_count == 0:
					screen_shake = True
					dash_sound.play()
					dash = True
					dash_timer = 0
					dash_count += 1
					px = player_rect.centerx
					py = player_rect.centery
					dash_target = [pointer_rect.x + scroll[0], pointer_rect.y + scroll[1]]
					angle = math.atan2(dash_target[1] - player_rect.centery, dash_target[0] - player_rect.centerx)
					dx, dy = math.cos(angle), math.sin(angle)


			if event.type == MOUSEBUTTONUP:
				if pygame.mouse.get_pressed()[0]:
					shooting = False


			if event.type == KEYUP:
				if event.key == K_d:
					movingright = False
					if not slide:			
						player_acc = 0

				if event.key == K_a:
					movingleft = False
					if not slide:
						player_acc = 0

				if event.key == K_LSHIFT:
					slide_jump = False



		#checks if enemy is hit
		enemy_hits = pygame.sprite.groupcollide(enemies, bullets, True, True)

		#update bullet group (sprites)
		bullets.update(tile_rects, scroll, player_rect, (dash and dash_count <= 1))
		for bullet in bullets:
			if bullet.hit_player:
				life -= 1
				damage_sound.play()
			if pygame.Rect.colliderect(bullet.rect, player_rect) and not dash and dash_count <= 1:	
				pass
				


		#update dash box
		#animate dash box
		for db in db_group:
			db_action, db.frame = change_action(db_action, db.frame, "dash_box")
			db.frame += 1
			if db.frame >= len(animation_database[db_action]):
				db.frame = 0
			db_image_id = animation_database[db_action][db.frame]
			db.image = animation_frames[db_image_id]

			db.dash_box() 


			if pygame.Rect.colliderect(db.rect, player_rect) and not dash and not recoil and db_dash is False:
				#recoil = True
				player_movement[0] = player_movement[0]/1.25
				player_y_momentum = player_y_momentum/1.25

			if pygame.Rect.colliderect(db.rect, player_rect) and dash and dash_count <= 1 and recoil is False:
				db_dash = True
				recoil = False
				if dash_count > 0:
					dash_count -= 1
					db_sound.play()
				screen_shake = True
				for x in range(random.randint(2, 4)):
					particle = Particles(db.rect.centerx, db.rect.centery, random.randint(-100, 100)/30, (random.randint(-30, 30)/30, random.randint(-10, 10)/10), random.randint(1, 10)/10, 0.01, (44, 104, 152))


					particles.add(particle)

		if db_dash and end_dash_timer < 10:
			end_dash_timer += 1
		if end_dash_timer >= 10:
			end_dash_timer = 0
			db_dash = False

		#update spikes
		for spike in spikes:
			spike.spikes()

			if pygame.Rect.colliderect(spike.rect, player_rect):
				collisions["bottom"] = False
				hit = True


		#update cannons
		for cannon in cannons:
			if pygame.Rect.colliderect(cannon.rect, player_rect) and dash and dash_count == 0:
				for x in range(random.randint(120, 150)):
					particle = Particles(cannon.rect.x + 15, cannon.rect.y + 15, random.randint(0, 100)/5, (random.randint(-100, 100)/95, random.randint(-100, 100)/100), 3, 0.5, random.choice(bp_colours))
					particles.add(particle)
				cannon.kill()

			cannon.cannon(get_distance(cannon.rect, player_rect), player_rect.centerx, player_rect.centery)



		#update leaf enemies
		for leaf in leaf_enemies:

			leaf_action, leaf.frame = change_action(leaf_action, leaf.frame, "leaf_run")
			leaf.frame += 1
			if leaf.frame >= len(animation_database[leaf_action]):
				leaf.frame = 0
			leaf_image_id = animation_database[leaf_action][leaf.frame]
			leaf.image = animation_frames[leaf_image_id]

			if leaf.leaf_dash and leaf.timer2 <= 1:
				leaf_e_dash_sound.play()


			if pygame.Rect.colliderect(leaf.rect, player_rect) and ((leaf.leaf_dash and dash) or not dash):
					hit = True

			if pygame.Rect.colliderect(leaf.rect, player_rect) and dash and not leaf.leaf_dash:
				leaf_enemies.remove(leaf)
	

			leaf.leaf_enemy(2, 30, player_rect, tile_rects)


		#update enemies
		for e in enemies:
			e.update(player_rect.x, player_rect.y, enemy_speed, get_distance([player_rect.x, player_rect.y], [e.rect.x, e.rect.y]), tile_rects, scroll)
		
			enemy_action, enemy_frame = change_action(enemy_action, enemy_frame, "algae_enemy")


			if enemy_action != "":
				enemy_frame += 1
				if enemy_frame >= len(animation_database[enemy_action]):
					enemy_frame = 0
				enemy_image_id = animation_database[enemy_action][enemy_frame]
				e.image = animation_frames[enemy_image_id]

			if pygame.Rect.colliderect(e.rect, player_rect) and not dash:	
				hit = True
				

			if pygame.Rect.colliderect(e.rect, player_rect) and dash and dash_count <= 1:
				if dash_count > 0:
					dash_count -= 1
					enemy_hit_sound.play()

				screen_shake = True

				e.hit_timer += 1


				if e.hit_timer >= 3:
					for x in range(random.randint(20, 25)):
						particle = Particles(e.rect.centerx, e.rect.centery, random.randint(-100, 100)/15, (random.randint(-30, 30)/50, random.randint(-10, 10)/5), random.randint(1, 10)/10, 0.4, random.choice(ep_colours))
						particles.add(particle)

					e.hit_count += 1
					e.hit_timer = 0

			else:
				e.hit_timer = 0


		if hit:
			life_timer += 1
			if life_timer <= 1:
				life -= 1
				recoil = True
				damage_sound.play()

			if life_timer > 10:
				life_timer = 0
				hit = False

		if player_rect.x <= -5:
			movingleft = movingright = False
			player_rect.x += 20

		if player_rect.y > max_depth + 300:
			restart = True



		#update particles
		particles.update(scroll)


		#update leaves
		for leaf in leaves:
			leaf.leaf(0.5)

			if pygame.Rect.colliderect(leaf.rect, player_rect):
				leaf_count += 1
				leaf_sound.play()
				leaves.remove(leaf)

			particle_timer += 1
			if particle_timer == 10:
				for x in range(random.randint(5, 10)):
					#x, y, size, (speed.x, speed.y), min_size, rate, colour
					particle = Particles(leaf.rect.centerx, leaf.rect.centery, random.randint(10, 20)/2, (random.randint(-5,5)/5, random.randint(0, 10)/5), 4, 0.4, random.choice(ep_colours))
					particles.add(particle)
				particle_timer = 0


		#display player
		player_image.set_colorkey((255,255,255))
		player_image = pygame.transform.scale(player_image, (30, 30))
		display.blit(pygame.transform.flip(player_image, player_flip, False), (player_rect.x - scroll[0], player_rect.y - scroll[1]))

		#display pointer
		display.blit(pointer_image, (pointer_rect.x, pointer_rect.y))
				

		surface = pygame.transform.scale(display, WindowSize)



		if life == 0:
			restart = True

		if len(leaves) == 0:
			level += 1
			restart = True



		if restart:
			for x in range(100):
				pygame.time.delay(5)
			for bullet in bullets:
				bullet.kill()

			try:
				main(pygame.Rect((WindowSize[0]/displayx) + 100 + (WindowSize[0]/displayx)/6, WindowSize[1]//2 + 150, player_image.get_width(), player_image.get_height()), False, 0, 0, False, False, 0, False,
	 		False, False, False, 0, False, 0, False, 0, False, False, "", False, "", 0, "", False, False, "", pygame.image.load("animations/run/run_0.png").convert(), False, 
	 		0, False, 0, 15, 0, 0, 0, pygame.sprite.Group(), [], pygame.sprite.Group(), [], pygame.sprite.Group(), [], pygame.sprite.Group(), [], 
	 		pygame.sprite.Group(), [], pygame.sprite.Group(), [], 1, 0, 0, 0, 0, False, load_map(f"levels/level_{level}_data"), level, 0, False, 0)
			except:
				pass



		screen.blit(surface, (0, 0))
		pygame.display.update()
		surface = pygame.display.set_mode((WindowSize[0], WindowSize[1]), pygame.FULLSCREEN)
		clock.tick(120)

try:
	main(pygame.Rect((WindowSize[0]/displayx) + 100 + (WindowSize[0]/displayx)/6, WindowSize[1]//2 + 150, player_image.get_width(), player_image.get_height()), False, 0, 0, False, False, 0, False,
	 False, False, False, 0, False, 0, False, 0, False, False, "", False, "", 0, "", False, False, "", pygame.image.load("animations/run/run_0.png").convert(), False, 
	 0, False, 0, 15, 0, 0, 0, pygame.sprite.Group(), [], pygame.sprite.Group(), [], pygame.sprite.Group(), [], pygame.sprite.Group(), [], pygame.sprite.Group(), [], 
	 pygame.sprite.Group(), [], 1, 0, 0, 0, 0, False, load_map("levels/level_-3_data"), -3, 0, False, 0)
except:
	pass







"""
DONE:
	GOALS:
	 - make drag on player movement
	 - fix wall jumps and double jumps aadd
	 - implement particles
	 - add other types of enemies
	 - create a story/goal for the game
	 - make boulder follow player

TO-DO: 
	GOALS:
	 - add other types of enemies
	 - create a story/goal for the game
	 - pixel art & animations!!
	 - code stamina mechanic
	 - create function for animations


	Current:
	 - make enemies (land, cannon, etc...)
	 - code stamina mechanic
	 - make levels (maybe using level editor, make levels both fun and hard)
	 - figure out level editor
	 - if level editor works good, consider making a hollow knight type game (bosses, exploration, etc) but different aesthetic and gameplay (more fast-paced)
	 
	 - instead of levels, make around 5 different maps
	 	- in each map you can explore and look for hidden gems
	 	- there will be bosses to fight and hard parkour to get to these gems
	 	- make a point system where you can make a megadash and break stuff





IDEAS:
  - make the rock grow so that you are able to shoot once it has grown enough
  - make animations and better pixelart
  - apply physics to particles

  - change whole game mechanic:

  		- underwater game
  		- player can dash using mouse when the character is converted into another form

  - make an object that the player can use to restore dash by hitting it
  - make more enemies (move in loop)
  - make spike type objects (e.g. corals, slimy stuff??)
  - figure out how to get position of a tile

  - make puzzles and figthing on different sections of map. Make the aim to collect these "coins" or "gems". When you have enough of them you can use a super dash to enter a different area of the level
  - add more enemies, shooting things and bosses (when new areas are unlocked)
  - add an indicator that you can no longer dash (visual)

  - use ideas from scourge bringer
  - art for boss and code it
  - do simple enemies and grass and art for aesthetics
  - do more tiles
  - start with SFX!! :)
  
"""