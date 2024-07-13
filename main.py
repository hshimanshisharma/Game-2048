import pygame
import random
import math

pygame.init()

FPS = 60

WIDTH, HEIGHT = 800,800
ROWS = 4
COLS = 4

RECT_HEIGHT = HEIGHT//ROWS
RECT_WIDTH = WIDTH//COLS

OUTLINE_COLOR = (187, 173, 160)
BACKGROUND_COLOR = (205, 192, 180)
OUTLINE_THICKNESS = 10
FONT_COLOR = (119, 110, 101)
FONT_COLOR1 = (48, 25, 52)

FONT = pygame.font.SysFont('comicsans', 60, bold=True)
FONT1 = pygame.font.SysFont('comicsans', 80, bold=True)
FONT2 = pygame.font.SysFont('comicsans', 40, bold=True)
MOV_VEL = 20

WINDOW = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("2048")

class Tile:
    COLOR = [
        (237, 229, 218),
        (238, 225, 201),
        (243, 178, 122),
        (246, 150, 101),
        (247, 124, 95),
        (247, 95, 59),
        (237, 208, 115),
        (237, 204, 99),
        (236, 202, 80),]

    def __init__(self, value, row, col):
        self.value = value
        self.row = row
        self.col = col
        self.x = col * RECT_WIDTH
        self.y = row * RECT_HEIGHT

    def get_color(self):
        #for value 2 we need index 0
        #for       4               1
        #for       8               2
        #so use log with base 2
        color_index = int(math.log2(self.value)) - 1
        color = self.COLOR[color_index]
        return color

    def draw(self, window):
        color = self.get_color()
        pygame.draw.rect(window, color, (self.x, self.y, RECT_WIDTH, RECT_HEIGHT))

        text = FONT.render(str(self.value), 1, FONT_COLOR)
        window.blit(
            text,
             (
                self.x + (RECT_WIDTH/2 - text.get_width()/2), 
                self.y + (RECT_HEIGHT/2 - text.get_height()/2),
             ),
            )

    def set_pos(self, ceil=False):
        if ceil:
            self.row = math.ceil(self.y / RECT_HEIGHT)
            self.col = math.ceil(self.x / RECT_WIDTH)
        else:
            self.row = math.floor(self.y / RECT_HEIGHT)
            self.col = math.floor(self.x / RECT_WIDTH)

    def move(self, delta):
        self.x += delta[0]
        self.y += delta[1]

def draw_grid(window):
    for row in range(1, ROWS):
        y = row * RECT_HEIGHT
        pygame.draw.line(window, OUTLINE_COLOR, (0, y), (WIDTH,y), OUTLINE_THICKNESS)
    
    for col in range(1, COLS):
        x = col * RECT_WIDTH
        pygame.draw.line(window, OUTLINE_COLOR, (x,0), (x,HEIGHT), OUTLINE_THICKNESS)
    pygame.draw.rect(window, OUTLINE_COLOR, (0, 0, WIDTH, HEIGHT), OUTLINE_THICKNESS)   #OUTLINE_THICKNESS defines thickness of color so rectangle is not gonna be filled but have just a colored border

def draw(window, tiles):
    window.fill(BACKGROUND_COLOR)

    for tile in tiles.values():
        tile.draw(window)

    draw_grid(window)
    pygame.display.update()

def get_random_pos(tiles):
    row = None
    col = None
    while True:
        row = random.randrange(0, ROWS)
        col = random.randrange(0, COLS)
        if f"{row}{col}" not in tiles:
            break
    return row, col

def move_tiles(window, tiles, clock, direction):
    updated = True
    blocks = set()
    if direction == "left":
        sort_func = lambda x: x.col
        reverse = False
        delta = (-MOV_VEL, 0)
        boundary_check = lambda tile: tile.col == 0
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col-1}")
        merge_check = lambda tile, next_tile: tile.x > next_tile.x + MOV_VEL
        move_check = (lambda tile, next_tile: tile.x > next_tile.x + MOV_VEL + RECT_WIDTH)
        ceil = True 
    elif direction == "right":
        sort_func = lambda x: x.col
        reverse = True
        delta = (MOV_VEL, 0)
        boundary_check = lambda tile: tile.col == COLS - 1
        get_next_tile = lambda tile: tiles.get(f"{tile.row}{tile.col+1}")
        merge_check = lambda tile, next_tile: tile.x < next_tile.x - MOV_VEL
        move_check = lambda tile, next_tile: tile.x + RECT_WIDTH + MOV_VEL < next_tile.x 
        ceil = False
    elif direction == "up":
        sort_func = lambda x : x.row
        reverse = False
        delta = (0, -MOV_VEL)
        boundary_check = lambda tile : tile.row == 0
        get_next_tile = lambda tile : tiles.get(f"{tile.row-1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y > next_tile.y + MOV_VEL
        move_check = lambda tile, next_tile: tile.y > next_tile.y + MOV_VEL + RECT_HEIGHT
        ceil = True
    elif direction == "down":
        sort_func = lambda x : x.row
        reverse = True
        delta = (0, MOV_VEL)
        boundary_check = lambda tile : tile.row == ROWS-1
        get_next_tile = lambda tile : tiles.get(f"{tile.row+1}{tile.col}")
        merge_check = lambda tile, next_tile: tile.y < next_tile.y - MOV_VEL
        move_check = lambda tile, next_tile: tile.y + MOV_VEL + RECT_HEIGHT < next_tile.y 
        ceil = False
    
    while updated:
        clock.tick(FPS)
        updated = False
        sorted_tiles = sorted(tiles.values(), key=sort_func, reverse=reverse)
        for i, tile in enumerate(sorted_tiles):
            if boundary_check(tile):
                continue
            next_tile = get_next_tile(tile)
            if not next_tile:
                tile.move(delta)
            elif tile.value == next_tile.value and tile not in blocks and next_tile not in blocks:
                if merge_check(tile, next_tile):
                    tile.move(delta)
                else:
                    next_tile.value *= 2
                    sorted_tiles.pop(i)
                    blocks.add(next_tile)
            elif move_check(tile, next_tile):
                tile.move(delta)
            else:
                continue 
            tile.set_pos(ceil)
            updated = True

        update_tiles(window, tiles, sorted_tiles)
    return end_move(tiles)

def end_move(tiles):
    if len(tiles) == 16:
        return "lost"
    for  tile in tiles.values():
        if tile.value == 2048:
            return "win"
    row, col = get_random_pos(tiles)
    tiles[f"{row}{col}"] = Tile(random.choice([2,4]), row, col)
    return "continue"

def update_tiles(window, tiles, sorted_tiles):
    tiles.clear()
    for tile in sorted_tiles:
        tiles[f"{tile.row}{tile.col}"] = tile
    
    draw(window,tiles)

def generate_tiles():
    tiles = {}
    for i in range (0,2):
        row, col = get_random_pos(tiles)
        tiles[f"{row}{col}"] = Tile(2, row, col)
    return tiles

def game_lost(window, mess):
    # draw(window,tiles={})
    message = FONT1.render("Game Over", 1, FONT_COLOR1)
    window.blit(message, (WIDTH/2 - (message.get_width()/2), HEIGHT/2 - (message.get_height()/2)))
    restart_message = FONT2.render("Press Space To Restart The Game", 1, FONT_COLOR1)
    window.blit(restart_message, (WIDTH/2 - (restart_message.get_width()/2), HEIGHT/2 + (message.get_height()/2) - (restart_message.get_height()/2) +30 ))
    pygame.display.update()
    pygame.time.delay(5000)
    action(window)

def game_won(window):
    message = FONT1.render("YOU WON", 1, FONT_COLOR1)
    window.blit(message, (WIDTH/2 - (message.get_width()/2), HEIGHT/2 - (message.get_height()/2)))
    restart_message = FONT2.render("Press Space To Restart The Game", 1, FONT_COLOR1)
    window.blit(restart_message, (WIDTH/2 - (restart_message.get_width()/2), HEIGHT/2 + (message.get_height()/2) - (restart_message.get_height()/2) +30 ))
    pygame.display.update()
    pygame.time.delay(5000)
    action(window)

def action(window):
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                main(window)

def main(window):
    clock = pygame.time.Clock()
    run = True

    tiles = generate_tiles()
    flag = False
    while run:
        clock.tick(FPS)
 
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT:
                    mess = move_tiles(window, tiles, clock, "left")
                    
                    if mess == "lost":
                        game_lost(window, mess)
                    elif mess == "win":
                        game_won(window)
                        break

                if event.key == pygame.K_RIGHT:
                    mess = move_tiles(window, tiles, clock, "right")
                    if mess == "lost":
                        game_lost(window, mess)
                    elif mess == "win":
                        game_won(window)
                        break

                if event.key == pygame.K_UP:
                    mess = move_tiles(window, tiles, clock, "up")
                    if mess == "lost":
                        game_lost(window, mess)
                    elif mess == "win":
                        game_won(window)
                        break

                if event.key == pygame.K_DOWN:
                    mess = move_tiles(window, tiles, clock, "down")
                    if mess == "lost":
                        game_lost(window, mess)
                    elif mess == "win":
                        game_won(window)   
                        break
                
        draw(window, tiles)
    
    

    

if __name__ == '__main__':
    main(WINDOW)