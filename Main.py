'''
A Stupidly ambitious top-down arcade shooter with the following features:
    side-scrolling map that focuses on the player
    Enemies that shoot back (coming in many varieties)
    customisable weapons (remix noita style wand-building)
    XP - level ups (Nuclear throne inspired)
    level editor in sepperate program that allows drawing in a GUI, then outputs data to a JSON file to construct the environment from
'''
#TO-DO:
'''
decide on a GUI colour scheme & style...
obsticles that block bullets, but have HP and can be destroyed! (can be drawn in map editor)
add function in mapMaker to add maps
Create lasting powerups
add bullet skins that get accessed and set by __init__ args
'''
# FIX MOVEMENT - player moves at 5/4 speed on 720, 4/4 speed at 1080, and 3/4 speed at 1440.   ----   potentially FPS based?   ----

# Checklist for later:
'''
Assign a weapon editor menu to the TAB key
Encyclopidia of discovered cards, special cards, weapons and enemies with descriptions in the main + pause menu
    - Pull data from JSON file to recall previously discovered items
saving runs (write strings to file on save, extract data & decode on launch)
Enemies should pathfind towards the player if in range (avoiding blocks somehow (Djikstra?))
make an actual menu screen... (might include game title)
Different enemies - Enemy that cant be hit until it starts charging an attack - Melee enemy - flies at player through walls in big loops, - enemy that send out projectiles on death -
New maps
zones (list of zone numbers, wall + floor colours + enemy types)
bosses
Weapon drops
chests spawns on map
weapon sub-types
card drops with pretty images
actually good art (praised be Stable Diffusion)
XP & level-ups
perks on level up
RMB abilities (radar, turrets, shield)
base to return to after boss-fights with extra card+weapon storage
crafting specials together for upgrading
Main menu statistics screen, showing data from previous runs including best run, enemies killed, bullets fired, total deaths, etc... (create new JSON file to store and retrieve run info from)
procedurally generated maps (blit circles to a graph - run pathfinder to check connections and blit lines to fix any unconnected areas, then encode the entire thing as binary matrix)
'''
import pygame, sys, Launcher
from pygame.locals import *
from MapBuilding import *
from Classes import *
from GUI_Elements import *

pygame.init()

if __name__ == "__main__":
    scr_hi, scr_wi, fullscreenBOOL = Launcher.Config() # Launches config window, and returns screen setup variables
if fullscreenBOOL:
    disp = pygame.display.set_mode((scr_wi, scr_hi), pygame.FULLSCREEN)
else:
    disp = pygame.display.set_mode((scr_wi, scr_hi))
pygame.display.set_caption("{Insert Creative Name Here}")  # sets display window name

cursor = crossheir()

X_drift = 0  # the amount the screen pans toward the cursor in the specified direction
Y_drift = 0

FPStimer = time.time()
screen = pygame.display.get_surface()  # not currently used
screenrect = screen.get_rect()
screensize = (scr_wi, scr_hi)
BigFont = pygame.font.Font(None, 100)

enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()

gamestate = 0    # 0 = Menu, 1 = Playing, 2 = Pause, 

# Pause screen
pause_shading = pygame.Surface(screensize, SRCALPHA)
pause_shading.fill((0,0,0,120))
Pause_Text = BigFont.render("PAUSED", True, (200,200,200))
Pause_Text_rect = Pause_Text.get_rect(center = (scr_wi//2, scr_hi//4))

enemy_list = [enemy, enemy, melee]  # temporary (will eventually be bundles with area data in JSON) currently uses reppetition as weights

text_placeholder = BigFont.render("Press ESC to start!", True, (255,255,255))   # main menu bits

# set to 0 to force update for HP pannel on launch
player_HP = 0
EnemyCount = 0
level = 0
levelUp = False
allSprites = pygame.sprite.Group()
bob = player()
levelUpLocations = [(scr_wi//2 - 150, scr_hi//2), (scr_wi//2 + 150, scr_hi//2)]

# weapon slot setup
pistol = weapon(bob, "Pistol")  # higher speed
pistol.speed = 20

sMG = weapon(bob, "SMG")  # less damage, faster FR
sMG.damage = 2
sMG.FR = 4
sMG.cooldown = 1/sMG.FR

shotgun = weapon(bob, "shotgun")  # slow, but fires lots of shells - !! add projectile spread !!
shotgun.damage = 1
shotgun.FR = 1.5
shotgun.cooldown = 1/shotgun.FR
shotgun.spread = 45
shotgun.projectiles = 15
    
weaponSlots = [pistol, sMG, shotgun]
activeWeapon = 0

def return_presed():
    pressed_keys = pygame.key.get_pressed()
    for num in range(10):
                key = getattr(pygame, f"K_{num}")    # updates the currently drawn tile to the selected number
                if pressed_keys[key]:
                    if num in range(0, len(weaponSlots) + 1):
                        return num
    return False

if __name__ == "__main__":
    # main loop for creating maps
    while True:
        for item in allSprites: # clears the list when changing map
            item.kill()

        blocks.clear()

        # Randomises and re-builds the map
        worlddata = random.choice(mapConfigurations)
        area_map, map_position = SetUpMap(trim_data(worlddata), (150,120,40), (100,40,20), 80, screensize, enemy_list, enemies)   # sets up the surface "area_map" with a world image from "worlddata" usign the specified colours
        bob.relocate(map_position)
        testGun = weapon(bob, None)
        # stores all sprites in a group to allow easy future resets
        allSprites.add(enemies)

        level += 1
        while levelUp:    # Level up screen / perk select screen   ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
            disp.fill((80,80,90))
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                    sys.exit()
            if Extra_HP_Button(levelUpLocations[0], disp).collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                bob.maxHP += 2
                bob.HP = bob.maxHP
                levelUp = False
            elif Extra_Life_Button(levelUpLocations[1], disp).collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                bob.BonusLives += 1
                levelUp = False
            pygame.display.flip()

        Playing = True
        # loop for playing the maps
        while Playing:
            pressed_keys = pygame.key.get_pressed()
            if gamestate == 0:  # Main Menu   ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
                disp.blit(text_placeholder, (200,200))
                if pressed_keys[K_ESCAPE]:
                    gamestate = 1
                    esc_registering = False

            elif gamestate == 1:  # Main game   ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
                disp.fill((150,120,40))

                map_DX, map_DY = bob.move(blocks, scr_wi, scr_hi, projectiles)  # moves the player, and returns delta [X, Y]

                if bob.HP <= 0:
                    if bob.BonusLives > 0:  # use bonus life (if available) to restore HP to 50% of max
                        bob.BonusLives -= 1
                        bob.HP = (bob.maxHP)//2
                    else:
                        gamestate = 3  # cut to death screen

                X_offset = int((cursor.rect.centerx - scr_wi // 2) / 10)  # denominator will become weapon-specific
                Y_offset = int((cursor.rect.centery - scr_hi // 2 ) / 8)  # close range weapons = low denom. vice versa
                X_drift += (X_offset - X_drift)/20  # gradually moves the camera offset towards the cursor
                Y_drift += (Y_offset - Y_drift)/20  # reduce the denominator to increase speed

                map_position = (map_position[0] + map_DX, map_position[1] + map_DY)  # updates the map position by player movement to keep them in sync
                drifted_map_pos = (map_position[0] - X_drift, map_position[1] - Y_drift)
                screenrect[0], screenrect[1] = drifted_map_pos

                displayed = pygame.Rect(-drifted_map_pos[0], -drifted_map_pos[1], scr_wi, scr_hi)
                disp.blit(area_map, (0,0), displayed)  # only blits a small viewport of the map, instead of the entire thing
                cursor.draw(disp)

                for item in enemies:   # handling of enemy animations
                    item.save_map_pos(drifted_map_pos)
                    if dist((item.draw_location), (bob.rect_on_screen[0], bob.rect_on_screen[1])) <= (scr_hi * 1.2):
                        item.move(blocks, projectiles)
                        item.draw(disp, drifted_map_pos, blocks)
                        item.attack(bob, blocks, projectiles)

                        # draws enemy rects for debugging
                        '''pygame.draw.rect(disp, (255,0,0), item.rect_on_screen, 1)'''

                    elif dist((item.draw_location), (bob.rect_on_screen[0], bob.rect_on_screen[1])) <= (scr_hi * 1.8):
                        item.attack(bob, blocks, projectiles)

                    if pressed_keys[K_DELETE]:  # debug - press del to "win" the level
                        item.kill()

                bob.draw(disp, (scr_wi//2 - X_drift, scr_hi//2 - Y_drift))  # draws player at the center of the screen, adjusted by cursor location
                
                if return_presed():
                    activeWeapon = (return_presed() - 1)
                    print(weaponSlots[activeWeapon].type)
                if pygame.mouse.get_pressed()[0]:
                    weaponSlots[activeWeapon].shoot(projectiles, drifted_map_pos, pygame.mouse.get_pos())
                weaponSlots[activeWeapon].draw(disp, pygame.mouse.get_pos())

                for item in projectiles:   # handling of projectile animations
                    item.update(blocks, drifted_map_pos)
                    if dist((item.draw_location), (bob.rect_on_screen[0], bob.rect_on_screen[1])) <= (scr_hi * 1.2):
                        item.draw(disp)
                    if item not in allSprites:
                        allSprites.add(item)

                PlayerHP_Tab(disp, bob, (player_HP != bob.HP), scr_wi)
                player_HP = bob.HP

                EnemyCount_Tab(disp, enemies, (len(enemies) != EnemyCount), scr_wi)
                EnemyCount = len(enemies)
                if EnemyCount == 0:
                    Playing = False
                    levelUp = True


                if not pressed_keys[K_ESCAPE]:  # stops flickering when trying to pause/unpause by only allowing new key-presses
                    esc_registering = True
                if pressed_keys[K_ESCAPE] and esc_registering:
                    gamestate = 2
                    esc_registering = False

            elif gamestate == 2:  # Pause  ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
                disp.fill((150,120,40))
                disp.blit(area_map, drifted_map_pos)   # draws the map in the background
                bob.draw(disp, (scr_wi//2 - X_drift, scr_hi//2 - Y_drift))    # draws the player
                for item in enemies:
                    if dist((item.draw_location), (bob.rect_on_screen[0], bob.rect_on_screen[1])) <= (scr_hi * 1.2):
                        item.draw(disp, drifted_map_pos, blocks)   # draws the enemies
                for item in projectiles:
                    if dist((item.draw_location), (bob.rect_on_screen[0], bob.rect_on_screen[1])) <= (scr_hi * 1.2):
                        item.draw(disp)   # draws active bullets
                disp.blit(pause_shading, (0,0))
                disp.blit(Pause_Text, Pause_Text_rect)

                if Quit_Button((50, scr_hi-150), disp).collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    print("\nended\n")
                    pygame.quit()
                    sys.exit()

                if Refresh_Button((50, scr_hi-300), disp).collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    gamestate = 0
                    Playing = False # breaks from playing loop, returning the program to randomise and rebuild the map

                if not pressed_keys[K_ESCAPE]:  # stops flickering when trying to pause/unpause by only allowing new key-presses
                    esc_registering = True
                if pressed_keys[K_ESCAPE] and esc_registering:  # unpause the game when new keypress is registered
                    gamestate = 1
                    esc_registering = False
            
            elif gamestate == 3:   # Dead   ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
                disp.fill((100,0,0))

                if Quit_Button((50, scr_hi-150), disp).collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    print("\nended\n")
                    pygame.quit()
                    sys.exit()

                if Refresh_Button((50, scr_hi-300), disp).collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    gamestate = 0
                    Playing = False
            
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("\nended\n")
                    pygame.quit()
                    sys.exit()
            pygame.time.Clock().tick(120)  # 120 FPS because I'm a snob (and current performance looks ok)
