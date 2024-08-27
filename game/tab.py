import sys


import time
import random
import pygame


PLAYER_COLOR = (200, 10, 50)
WALL_COLOR = (200, 200, 200)
TILE_COLOR = (255, 255, 255)

TILE_SIZE = 20
PLAYER_SIZE = 5


def is_player_pos(x, y, posX, posY):
    # return x == posX and y == posY

    return (
        posX >= x * TILE_SIZE
        and posX <= (x + 1) * TILE_SIZE
        and posY >= y * TILE_SIZE
        and posY <= (y + 1) * TILE_SIZE
    )


def is_wall(x_pxl, y_pxl, height_pxl, width_pxl):
    return (
        x_pxl < TILE_SIZE
        or y_pxl < TILE_SIZE
        or x_pxl >= width_pxl - TILE_SIZE 
        or y_pxl >= height_pxl - TILE_SIZE
    )


def create_map(height, width, posX, posY, screen):
    map_x = 0
    map_y = 0
    while map_y < height / TILE_SIZE:
        while map_x < width / TILE_SIZE:
            map_x_pxl = map_x * TILE_SIZE
            map_y_pxl = map_y * TILE_SIZE

            if is_wall(map_x_pxl, map_y_pxl, height, width):
                draw_rect(
                    screen, WALL_COLOR, (map_x_pxl, map_y_pxl), (TILE_SIZE, TILE_SIZE)
                 )
            else:
                draw_rect(
                    screen, TILE_COLOR, (map_x_pxl, map_y_pxl), (TILE_SIZE, TILE_SIZE)
                )
            if is_player_pos(map_x, map_y, posX, posY):
                draw_rect(
                    screen, PLAYER_COLOR, (posX, posY), (PLAYER_SIZE, PLAYER_SIZE)
                )
            map_x += 1
        
        map_x = 0
        map_y += 1


def get_next_pos(posX, posY, dirX, dirY):
    return (posX + dirX, posY + dirY)


def generate_player_dir(stepX, stepY):
    return (random.randint(-stepX, stepX), random.randint(-stepY, stepY))




def quit_program():
    pygame.quit()
    sys.exit()


def hanlde_key_press(event):
    if event.type == pygame.KEYDOWN:
        if event.key == pygame.K_ESCAPE:
            quit_program()


def draw_rect(screen, color, pos, rectDimensions):
    pygame.draw.rect(
        screen,
        color,
        pygame.Rect(pos, rectDimensions),
    )

def is_player_in_wall(player_min_x, player_min_y, height_pxl, width_pxl):
    player_min_posX = player_min_x
    player_min_posY = player_min_y
    
    player_max_posX = player_min_x + PLAYER_SIZE
    player_max_posY = player_min_y + PLAYER_SIZE
    
    floor_min = 0 + TILE_SIZE

    floor_max_y =  height_pxl - TILE_SIZE
    floor_max_x = width_pxl - TILE_SIZE
    
    if player_min_posX <= floor_min or player_min_posY <= floor_min:
        return True
    if player_max_posX >= floor_max_x or player_max_posY >= floor_max_y:
        return True
    
def is_player_size(player_next_size):
    player_next_size != PLAYER_SIZE


def main(height, width):
    tiles_amount_x = width / TILE_SIZE
    tiles_amount_y = height / TILE_SIZE

    playerPosX = random.randint(1, tiles_amount_x - 1) * TILE_SIZE
    playerPosY = random.randint(1, tiles_amount_y - 1) * TILE_SIZE

    stepX = 1 
    stepY = 1
    playerDirX, playerDirY = generate_player_dir(stepX, stepY)

    screen = pygame.display.set_mode((height, width), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    pygame.init()
    pygame.display.set_caption("dekma.py")

    create_map(height, width, playerPosX, playerPosY, screen)


    while True:
        for event in pygame.event.get():
            hanlde_key_press(event)

        next_player_pos_x, next_player_pos_y = get_next_pos(playerPosX, playerPosY, playerDirX, playerDirY)

        while is_player_in_wall(playerPosX, playerPosY, height, width) or playerDirX == 0 and playerDirY == 0:
            playerDirX, playerDirY = generate_player_dir(stepX, stepY)
            next_player_pos_x, next_player_pos_y = get_next_pos(playerPosX, playerPosY, playerDirX, playerDirY)
            playerPosX = next_player_pos_x
            playerPosY = next_player_pos_y 
        else:
            playerPosX = next_player_pos_x
            playerPosY = next_player_pos_y
            is_player_size(player_next_size = PLAYER_SIZE)

        create_map(height, width, playerPosX, playerPosY, screen)
        
        
        pygame.display.flip()
        clock.tick(60)


main(400, 400)
