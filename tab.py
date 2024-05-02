import sys


import time
import random
import pygame


PLAYER_COLOR = (252, 186, 3)
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


def is_wall(x, y, wallX, wallY):
    return (
        x <= TILE_SIZE
        or y <= TILE_SIZE
        or x >= wallX - TILE_SIZE
        or y >= wallY - TILE_SIZE
    )


def create_map(height, width, posX, posY, screen):
    map_x = 0
    map_y = 0
    while map_y < height:
        while map_x < width:
            print(map_x, map_y, posX, posY)
            if is_player_pos(map_x, map_y, posX, posY):
                draw_rect(
                    screen, PLAYER_COLOR, (map_x, map_y), (PLAYER_SIZE, PLAYER_SIZE)
                )
            elif is_wall(map_x, map_y, height, width):
                draw_rect(
                    screen, WALL_COLOR, (map_x, map_y), (TILE_SIZE - 1, TILE_SIZE - 1)
                )
            else:
                draw_rect(
                    screen, TILE_COLOR, (map_x, map_y), (TILE_SIZE - 1, TILE_SIZE - 1)
                )
            map_x += TILE_SIZE
        map_x = 0
        map_y += TILE_SIZE


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


def main(height, width):
    tile_x = width / TILE_SIZE
    tile_y = height / TILE_SIZE

    playerPosX = random.randint(1, tile_x - 1) * TILE_SIZE
    playerPosY = random.randint(1, tile_y - 1) * TILE_SIZE

    stepX = 1 * PLAYER_SIZE
    stepY = 1 * PLAYER_SIZE
    playerDirX, playerDirY = generate_player_dir(stepX, stepY)

    screen = pygame.display.set_mode((height, width), pygame.RESIZABLE)
    clock = pygame.time.Clock()
    pygame.init()
    pygame.display.set_caption("dekma.py")

    create_map(height, width, playerPosX, playerPosY, screen)

    while True:
        time.sleep(0.5)
        for event in pygame.event.get():
            hanlde_key_press(event)
        next_player_pos_x, next_player_pos_y = get_next_pos(
            playerPosX, playerPosY, playerDirX, playerDirY
        )

        while is_wall(next_player_pos_x, next_player_pos_y, width, height):
            playerDirX, playerDirY = generate_player_dir(stepX, stepY)
            while playerDirX == 0 and playerDirY == 0:
                playerDirX, playerDirY = generate_player_dir(stepX, stepY)
            next_player_pos_x, next_player_pos_y = get_next_pos(
                playerPosX, playerPosY, playerDirX, playerDirY
            )
        playerPosX = next_player_pos_x
        playerPosY = next_player_pos_y
        print(f"x:{playerPosX} y:{playerPosY} dirx:{playerDirX} diry:{playerDirY}")
        create_map(height, width, playerPosX, playerPosY, screen)
        pygame.display.flip()
        clock.tick(10)


main(400, 400)
