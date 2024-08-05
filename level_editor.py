import pygame, sys
import csv, pickle


pygame.init()
clock = pygame.time.Clock()
font = pygame.font.SysFont("Futura", 30)

level = 0

class Button():
	def __init__(self, x, y, image, scale):
		width = image.get_width()
		height = image.get_height()
		self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
		self.rect = self.image.get_rect()
		self.rect.topleft = (x, y)
		self.clicked = False

	def draw(self, surface):
		action = False
		#get mouse position
		pos = pygame.mouse.get_pos()

		#check mouseover and clicked conditions
		if self.rect.collidepoint(pos):
			if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
				self.clicked = True
				action = True

		if pygame.mouse.get_pressed()[0] == 0:
			self.clicked = False

		#draw button on screen
		surface.blit(self.image, (self.rect.x, self.rect.y))

		return action

#setting screen variables
WindowSize = [800, 700]
MarginSize = [300, 200] #[lower margin, side margin]

screen = pygame.display.set_mode((WindowSize[0] + MarginSize[0], WindowSize[1] + MarginSize[1]))
pygame.display.set_caption("Level Editor")

"""
#load background image
bg_image = pygame.image.load("background/mountains_background.png").convert()
bg_image = pygame.transform.scale(bg_image, (WindowSize[0], WindowSize[1]))
bg_image.set_colorkey((255, 255, 255))
"""

#draw grid

TILE_SIZE = 32
rows = WindowSize[1]//TILE_SIZE + 10
cols = 60
def draw_grid():
	for i in range(cols + 1):
		pygame.draw.line(screen, (255, 255, 255), ((i*TILE_SIZE) - scroll[0], 0), ((i*TILE_SIZE) - scroll[0], WindowSize[1]))
 	
	for i in range(rows + 1):
		pygame.draw.line(screen, (255, 255, 255), (0, (i*TILE_SIZE - scroll[1])), (WindowSize[0], (i*TILE_SIZE) - scroll[1]))

#loading tiles
TILE_TYPES = 8
tile_list = []
current_tile = 0


for x in range(1, TILE_TYPES + 1):
	img = pygame.image.load(f"tiles/rock_tiles/rock_tile_{x}.png").convert()
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img.set_colorkey((255, 255, 255))
	tile_list.append(img)


filler_tile_img = pygame.image.load("tiles/rock_tiles/rock_ground_filler.png")
filler_tile_img = pygame.transform.scale(filler_tile_img, (TILE_SIZE, TILE_SIZE))
tile_list.append(filler_tile_img)

for x in range(TILE_TYPES+1):
	img = pygame.image.load(f"tiles/stone/stone_{x}.png").convert()
	img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img.set_colorkey((255, 255, 255))
	tile_list.append(img)

stone_filler = pygame.image.load("tiles/stone/stone_filler.png")
stone_filler = pygame.transform.scale(stone_filler, (TILE_SIZE, TILE_SIZE))
img.set_colorkey((255, 255, 255))
tile_list.append(stone_filler)

dash_box_img = pygame.image.load("tiles/dash_box_0.png").convert()
tile_list.append(dash_box_img)
coral_spikes = pygame.image.load("tiles/spike_tiles/spike_0.png").convert()
tile_list.append(coral_spikes)

algae_enemy = pygame.image.load("tiles/algae_enemy_0.png").convert()
tile_list.append(algae_enemy)

mana = pygame.image.load("tiles/leaf.png").convert()
mana.set_colorkey((255, 255, 255))
tile_list.append(mana)

cannon = pygame.image.load("tiles/cannon.png").convert()
cannon.set_colorkey((255, 255, 255))
tile_list.append(cannon)

leaf_e = pygame.image.load("animations/leaf_run/leaf_enemy_img.png").convert()
leaf_e.set_colorkey((255, 255, 255))
tile_list.append(leaf_e)

for x in range(1, 4):
	img = pygame.image.load(f"tiles/spike_tiles/spike_{x}.png").convert()
	#img = pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
	img.set_colorkey((255, 255, 255))
	tile_list.append(img)

#create empty tile list
world_data = []
for row in range(rows):
	#r = [-1] * cols
	r = [-1] * cols
	world_data.append(r)




def draw_world():
	for y, row in enumerate(world_data):
		for x, tile in enumerate(row):
			if tile >= 0:
				screen.blit(tile_list[tile], (x*TILE_SIZE - scroll[0], y*TILE_SIZE - scroll[1]))


#output text based map
def draw_text(text, font, text_col, x, y):
	img = font.render(text, True, text_col)
	screen.blit(img, (x, y))





#scrolling
scroll_left = False
scroll_right = False
scroll_up = scroll_down = False
scroll = [0, 0]
scroll_speed = 1
fast_scroll = 1

#create buttons

button_list = []
button_col = button_row = 0
for i in range(len(tile_list)):
	tile_button = Button(WindowSize[0] + (75 * button_col) + 50, 75* button_row + 50, tile_list[i], 1)
	button_list.append(tile_button)
	button_col += 1
	if button_col == 3:
		button_row += 1
		button_col = 0



while True:
	screen.fill((105, 219, 202))


	draw_grid()
	draw_world()
	draw_text(f"Level: {level}", font, (255, 255, 255), 10, WindowSize[1] + MarginSize[0] - 90)

	#scroll_map
	if scroll_left and scroll[0] > 0:
		scroll[0] -= 5 * fast_scroll
	if scroll_right and scroll[0] < (cols * TILE_SIZE) - WindowSize[0]:
		scroll[0] += 5 * fast_scroll
	if scroll_up:
		scroll[1] -= 5 * fast_scroll
	if scroll_down:
		scroll[1] += 5 * fast_scroll
	#adding tiles to the screen
	pos = pygame.mouse.get_pos()
	x = (pos[0] + scroll[0]) // TILE_SIZE
	y = (pos[1] + scroll[1]) // TILE_SIZE

	if pos[0] < WindowSize[0] and pos[1] < WindowSize[1]:
		if pygame.mouse.get_pressed()[0] == 1:
			if world_data[y][x] != current_tile:
				world_data[y][x] = current_tile

		if pygame.mouse.get_pressed()[2] == 1:
			world_data[y][x] = -1

	#draw tile panel
	pygame.draw.rect(screen, (105, 219, 202), (WindowSize[0], 0, MarginSize[1] + WindowSize[1], WindowSize[1]))

	for button_count, i in enumerate(button_list):
		if i.draw(screen):
			current_tile = button_count

	#highlight selected tile
	pygame.draw.rect(screen, (255, 0, 0), button_list[current_tile].rect, 3)

	#set colorkey for tiles (transparent)
	for x in tile_list:
		x.set_colorkey((255, 255, 255))

	for event in pygame.event.get():
		if 	event.type == pygame.QUIT:
			sys.exit()

		if event.type == pygame.KEYDOWN:

			if event.key == pygame.K_a:
				scroll_left = True
			if event.key == pygame.K_d:
				scroll_right = True
			if event.key == pygame.K_w:
				scroll_up = True
			if event.key == pygame.K_s:
				scroll_down = True
			if event.key == pygame.K_LSHIFT:
				fast_scroll = 4
			if event.key == pygame.K_UP:
				level += 1
				print("level", level)
			if event.key == pygame.K_DOWN and level > 0:
				level -= 1
				print("level", level)


			if event.key == pygame.K_k:
				#make csv
				with open(f"levels/level_{level}_data.txt", "w", newline="") as csvfile:
					writer = csv.writer(csvfile, delimiter = ",")
					for row in world_data:
						writer.writerow(row)

			if event.key == pygame.K_l:
				#load level data
				scroll = [0, 0]
				with open(f"levels/level_{level}_data.txt", "r", newline="") as csvfile:
					reader = csv.reader(csvfile, delimiter = ",")
					for x, row in enumerate(reader):
						for y, tile in enumerate(row):
							world_data[x][y] = int(tile)






						

		if event.type == pygame.KEYUP:

			if event.key == pygame.K_a:
				scroll_left = False
			if event.key == pygame.K_d:
				scroll_right = False
			if event.key == pygame.K_w:
				scroll_up = False
			if event.key == pygame.K_s:
				scroll_down = False
			if event.key == pygame.K_LSHIFT:
				fast_scroll = 1

	if level == 0:
		print("level", level)

	pygame.display.update()
	clock.tick(60)

