'''
A Stupidly ambitious top-down arcade shooter with the following features:
    side-scrolling map that focuses on the player (blit to huge surface, center screen on the player with the rest out of view)
    Enemies that shoot back (coming in many varieties)
    customisable weapons (blend Noita with MGB?)
    XP - level ups (Nuclear throne inspired)
    level editor in sepperate program that allows drawing maps like in paint, then outputs data to a JSON file to construct the environment from

Later to include:
    procedurally generated maps (blit circles to a graph - plot points at indecies, run pathfinder/maze solver to check connections and blit lines to fix any unconnected areas, then encode the entire thing as binary matrix)
    actually good art (praised be Stable Diffusion)
    saving runs (write strings to file on save, extract data & decode on launch)
    Melee enemy - flies at player through walls in big loops
    Enemy that cant be hit until it starts charging an attack
'''
#TO-DO:
'''
Fix enemy collision with walls
'''
import pygame, sys, Launcher
from pygame.locals import *
from MapBuilding import *
from Classes import *

pygame.init()

if __name__ == "__main__":
    scr_hi, scr_wi, fullscreenBOOL = Launcher.Config() # Launches config window, and stores screen variables
if fullscreenBOOL:
    disp = pygame.display.set_mode((scr_wi, scr_hi), pygame.FULLSCREEN)
else:
    disp = pygame.display.set_mode((scr_wi, scr_hi))
pygame.display.set_caption("{Insert Creative Name Here}")  # sets display window name

map_position = (100,-500)

player_speed = 8

cursor = crossheir() # type: ignore
bob = player(map_position) # type: ignore

X_drift = 0  # the amount the screen pans toward the cursor in the specified direction
Y_drift = 0

screen = pygame.display.get_surface()  # not currently used  -  will be needed for efficient rendering later
screenrect = screen.get_rect()
screensize = (scr_wi, scr_hi)

enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
#dave = enemy((670, 1120), screensize)
#print(f"main enemy created at {dave.rect.center}")
#enemies.add(dave)

gamestate = 1    # 0 = Menu, 1 = Playing, 2 = Pause, 

if __name__ == "__main__":
    SetUpMap(area_map, trim_data(worlddata), (150,120,40), (100,40,20), 80, screensize, enemy, enemies)   # sets up the surface "area_map" with a world image from "worlddata" usign the specified colours
    while True:
        if gamestate == 0:  # Main Menu
            pass
        elif gamestate == 1:  # Main game
            pressed_keys = pygame.key.get_pressed()
            disp.fill((150,120,40))

            map_DX, map_DY = bob.move(blocks, scr_wi, scr_hi, projectiles)  # moves the player, and returns delta [X, Y]

            X_offset = int(((cursor.rect.centerx)-scr_wi//2) /5)  # denominator will become weapon-specific
            Y_offset = int(((cursor.rect.centery)-scr_hi//2) /4)  # close range weapons = low denom. vice versa
            X_drift += (X_offset - X_drift)/40  # gradually moves the camera offset towards the cursor
            Y_drift += (Y_offset - Y_drift)/40  # reduce the denominator to increase speed

            map_position = (map_position[0] + map_DX, map_position[1] + map_DY)  # updates the map position by player movement to keep them in sync
            drifted_map_pos = (map_position[0] - X_drift, map_position[1] - Y_drift)

            disp.blit(area_map, drifted_map_pos)
            cursor.draw(disp)

            for item in enemies:   # handling of enemy animations
                item.move(blocks)
                item.attack(bob, blocks, projectiles)
                item.draw(disp, drifted_map_pos, blocks)

            bob.draw(disp, (scr_wi//2 - X_drift, scr_hi//2 - Y_drift))  # draws player at the center of the screen, adjusted by cursor location

            for item in projectiles:   # handling of projectile animations
                item.update(blocks)
                item.draw(disp, drifted_map_pos)
        elif gamestate == 2:  # Pause
            pass
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                print("\n ended \n")
                pygame.quit()
                sys.exit()
        pygame.time.Clock().tick(120)  # 120 FPS because I'm a snob
