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
decide on a GUI colour scheme & style...)
Enemy drops should be attracted to the player in a short range
add bullet skins that get accessed and set by __init__ args

add a "now placing: " pop-up to MapMaker to inform user of their selection
add function in mapMaker to add maps
Add mapmaker "forest" tile (draws empty with 80% chance for tree instead of 10%)
Add scrolling through maps in map maker: calculate the length of the list of maps, account for space in between then check that against screen size - if it will go off the screen then shift all aps to the left when the cursor is near the edge & left/right arrow key navigation
'''
# BUGS
'''
FIX MOVEMENT - player moves at 5/4 speed on 720, 4/4 speed at 1080, and 3/4 speed at 1440.   ----   potentially FPS based?   ----
Removing cards from weapons doesnt remove their effect
'''
# Kid's ideas I might use:
'''
Mythology themed
    special weapons such as mjolnir
    medusa: deals damage when you look at each other - look away to avoid getting hurt
    Certain areas such as egypt, Olympus, Valhalla, Helheim
Armour with set bonuses/ abilities
pets? Dog - fetch items for the player, bite attack
'''
# Checklist for later:
'''
Add abilities: sacrifice HP for temp damage boost
Add dangerous terrain
Encyclopidia of discovered cards, special cards, weapons and enemies with descriptions in the main + pause menu
    - Pull data from JSON file to recall previously discovered items
saving runs (write strings to file on save, extract data & decode on launch)
Enemies should pathfind towards the player if in range (avoiding blocks somehow (Djikstra?))
make an actual menu screen... (might include game title)
Different enemies - Enemy that cant be hit until it starts charging an attack - Melee enemy - flies at player through walls in big loops, - enemy that send out projectiles on death -
New maps
zones (list of zone numbers, wall + floor colours + enemy types)
    Egypt: Scarrab, aubis, dessert bandit
    Olympus:
    Valhalla:
    Atlantis:
    Helheim:
    Neifelheim:
    Rome:
bosses
Weapon drops
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

Use PyOpenGL for GPU acceleration!
'''
import pygame, sys, Launcher
from pygame.locals import *
from MapBuilding import *
from Classes import *
from GUI_Elements import *
from Cards import *

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

screen = pygame.display.get_surface()  # not currently used
screenrect = screen.get_rect()
screensize = (scr_wi, scr_hi)
BigFont = pygame.font.Font(None, 100)

enemies = pygame.sprite.Group()
projectiles = pygame.sprite.Group()
drops = pygame.sprite.Group()
obstacle_list = pygame.sprite.Group()
cards = pygame.sprite.Group()

gamestate = 0    # 0 = Menu, 1 = Playing, 2 = Pause, 

# Pause screen
pause_shading = pygame.Surface(screensize, SRCALPHA)
pause_shading.fill((0,0,0,120))
Pause_Text = BigFont.render("PAUSED", True, (200,200,200))
Pause_Text_rect = Pause_Text.get_rect(center = (scr_wi//2, scr_hi//4))

enemy_list = [enemy, enemy, melee]  # temporary (will eventually be bundles with area data in JSON) currently uses reppetition as weights

text_placeholder = BigFont.render("Press ESC to start!", True, (255,255,255))   # main menu bits
pickup_text = font.render("Press \"e\" to pickup", True, (0,0,0))
pickup_text_rect = pickup_text.get_rect(center = (scr_wi//2, scr_hi//1.5))

# set to 0 to force update for HP pannel on launch
player_HP = 0
player_MHP = 0
EnemyCount = 0
level = 0
levelUp = False
allSprites = pygame.sprite.Group()
bob = player()
levelUpLocations = [(scr_wi//2 - 150, scr_hi//2), (scr_wi//2 + 150, scr_hi//2)]

# weapon slot setup
pistol = weapon(bob, "Pistol")  # higher speed
pistol.basestats["Speed"] = 20
pistol.basestats["Pierce"] = 2
pistol.update_stats()

sMG = weapon(bob, "SMG")  # less damage, faster FR
sMG.basestats["Damage"] = 2
sMG.basestats["Fire rate"] = 5
sMG.cooldown = 1/sMG.stats["Fire rate"]
sMG.basestats["Spread"] = 8
sMG.update_stats()

shotgun = weapon(bob, "shotgun")  # slow, but fires lots of shells
shotgun.basestats["Damage"] = 1
shotgun.basestats["Fire rate"] = 1.5
shotgun.cooldown = 1/shotgun.stats["Fire rate"]
shotgun.basestats["Spread"] = 35
shotgun.basestats["Projectiles Per Shot"] = 12
shotgun.update_stats()

displayInventory = False
inventory = inventory_class(screensize)
dragging = False
weapons = weapon_slots_class()
#weaponSlots = weapon_slots_class()
weapons.set_slot(0, pistol)
weapons.set_slot(1, sMG)
weapons.set_slot(2, shotgun)
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
        for item in allSprites: # clears Enemies and projectiles
            item.kill()
        for item in obstacle_list:  # clears trees & chests
            item.kill()
        for item in cards: # clears cards that are still on the floor
            item.kill()

        blocks.clear()

        # Randomises and re-builds the map
        worlddata = random.choice(mapConfigurations)
        worlddata = mapConfigurations[3] # Debug mode full of chests

        area_map, map_position = SetUpMap(trim_data(worlddata), (150,120,40), (100,40,20), 80, screensize, enemy_list, enemies, obstacle_list)   # sets up the surface "area_map" with a world image from "worlddata" usign the specified colours
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
                disp.fill((0,0,30))
                disp.blit(text_placeholder, (200,200))
                if pressed_keys[K_ESCAPE]:
                    gamestate = 1
                    esc_registering = False

            elif gamestate == 1:  # Main game   ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
                disp.fill((150,120,40))

                # Moves the map/player & handles collisions with terrain, projectiles and chests
                map_DX, map_DY = bob.move(blocks, scr_wi, scr_hi, projectiles, drops, obstacle_list, cards, CardTypes)  # moves the player, and returns delta [X, Y]

                # Checks loose conditions & triggers extra life if availible
                if bob.HP <= 0:
                    if bob.BonusLives > 0:  # use bonus life (if available) to restore HP to 50% of max
                        bob.BonusLives -= 1
                        bob.HP = (bob.maxHP)//2
                    else:
                        print("Player Died")
                        gamestate = 3  # cut to death screen

                # Calculates the map drift towards the cursor & the speed at which it responds to the player aiming
                X_offset = int((cursor.rect.centerx - scr_wi // 2) / 10)  # denominator will become weapon-specific
                Y_offset = int((cursor.rect.centery - scr_hi // 2 ) / 8)  # close range weapons = low denom. vice versa
                X_drift += (X_offset - X_drift)/20  # gradually moves the camera offset towards the cursor
                Y_drift += (Y_offset - Y_drift)/20  # reduce the denominator to increase speed

                # Updates the maps location based on player & cursor location
                map_position = (map_position[0] + map_DX, map_position[1] + map_DY)  # updates the map position by player movement to keep them in sync
                drifted_map_pos = (map_position[0] - X_drift, map_position[1] - Y_drift)
                screenrect[0], screenrect[1] = drifted_map_pos

                # sets rect to display then update the screen with the area of map thats visible
                displayedArea = pygame.Rect(-drifted_map_pos[0], -drifted_map_pos[1], scr_wi, scr_hi)
                disp.blit(area_map, (0,0), displayedArea)  # only blits a small viewport of the map, instead of the entire thing

                for item in enemies:   # handling of enemy animations
                    item.save_map_pos(drifted_map_pos)
                    # only calculates when in a small range of the player to save performance
                    if dist((item.draw_location), (bob.rect_on_screen[0], bob.rect_on_screen[1])) <= (scr_hi * 1.2):
                        item.move(blocks, projectiles, drops)
                        item.draw(disp, drifted_map_pos, blocks)
                        item.attack(bob, blocks, projectiles)

                        # draws enemy rects for debugging
                        '''pygame.draw.rect(disp, (255,0,0), item.rect_on_screen, 1)'''
                    # allows for long range attacks even if outside the previous check's boundaries
                    elif dist((item.draw_location), (bob.rect_on_screen[0], bob.rect_on_screen[1])) <= (scr_hi * 1.8):
                        item.attack(bob, blocks, projectiles)

                    if pressed_keys[K_DELETE]:  # debug - press del to "win" the level - kills everything
                        item.kill()
                for drop in drops:
                    drop.draw(disp, drifted_map_pos)
                bob.draw(disp, (scr_wi//2 - X_drift, scr_hi//2 - Y_drift))  # draws player at the center of the screen, adjusted by cursor location
                
                for card in cards:  # CARD DRAWING TO MAP
                    if not card.stored:
                        card.draw(disp, drifted_map_pos)
                for card in cards:  # Card collide & pickup
                    if not card.stored:
                        if card.rect_on_screen.colliderect(bob.rect_on_screen):
                            disp.blit(pickup_text,pickup_text_rect)
                            if pressed_keys[K_e]:
                                for space in inventory.items:
                                    if space[1] == None:
                                        space[1] = card.type
                                        space[2] = pygame.Surface((100,100), SRCALPHA)
                                        space[2].fill((150,150,150,150))
                                        space[2].blit(card.image,(5,5))
                                        space[5] = card.description
                                        card.kill()
                                        break
                # draws obstacles (chests & trees)
                for item in obstacle_list:
                    item.draw(disp, drifted_map_pos, projectiles)

                if return_presed():  # Selects a weapon by pressing a number key
                    activeWeapon = (return_presed() - 1)
                    print(weaponSlots[activeWeapon].type)
                if pygame.mouse.get_pressed()[0] and not displayInventory:
                    weaponSlots[activeWeapon].shoot(projectiles, drifted_map_pos, pygame.mouse.get_pos())
                weaponSlots[activeWeapon].draw(disp, pygame.mouse.get_pos())

                for item in projectiles:   # handling of projectile animations
                    item.update(blocks, drifted_map_pos)
                    if dist((item.draw_location), (bob.rect_on_screen[0], bob.rect_on_screen[1])) <= (scr_hi * 1.2):
                        item.draw(disp)
                    if item not in allSprites:
                        allSprites.add(item)

                # Draws and updates the player HP counter on the display
                PlayerHP_Tab(disp, bob, ((player_HP != bob.HP) or (player_MHP != bob.maxHP)), scr_wi)
                player_HP = bob.HP
                player_MHP = bob.maxHP

                # Draws and updates the Enemy counter on the display & handles transitions when there are none left
                EnemyCount_Tab(disp, enemies, (len(enemies) != EnemyCount), scr_wi)
                EnemyCount = len(enemies)
                if EnemyCount == 0:
                    Playing = False
                    levelUp = True

                # Toggles the inventory
                if not pressed_keys[K_TAB]:
                    tab_registering = True
                elif pressed_keys[K_TAB] and tab_registering:
                    displayInventory = not displayInventory
                    tab_registering = False
                    for gun in weapons.slots:    
                        gun[1].update_self()
                
                # Inentory Management
                if displayInventory:
                    inventory.draw(disp)
                    weapons.draw_inventory(disp)
                    if not dragging:
                        for card in inventory.items:
                            # show description if hovered over
                            if card[3].collidepoint(pygame.mouse.get_pos()):
                                disp.blit(card[5], (pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1] + 20))
                            # enable users to drag
                            if card[1] != None:
                                if card[3].collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                                    dragging = True
                                    card_dragged = card[1](pygame.mouse.get_pos())  # Creates a new card, and sets its location to the mouse ponter
                                    print("Dragging a card")
                                    card[1] = None
                                    card[2] = inventory.empty_image
                                    card[5] = inventory.empty_message
                                    break
                        for gun in weapons.slots:
                            for slot in gun[1].firing_order:
                                if slot[2] != None:
                                    if slot[1].collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                                        dragging = True
                                        card_dragged = slot[5](pygame.mouse.get_pos())
                                        print("Dragging a card")
                                        # Resets the card slot to empty
                                        slot[0] = pygame.Surface((100,100),SRCALPHA)
                                        slot[0].fill((150,150,150,150))
                                        slot[2] = None
                                        slot[3] = None
                                        slot[4] = None
                                        slot[5] = None
                    elif dragging:
                        if not pygame.mouse.get_pressed()[0]:
                            if not inventory.assign(card_dragged): # If it cant drop into a slot in inventory
                                if not weapons.assign(card_dragged): # If it cant drop into a weapon slot
                                    card_dragged.place_to_map((bob.rect[0] + scr_wi//2, bob.rect[1] + scr_hi//2))
                                    card_dragged.stored = False
                                    card_dragged.draw(disp, drifted_map_pos)
                                    cards.add(card_dragged)
                            dragging = False
                        inventory.reset_images()
                        inventory.update()
                        weapons.update()
                        card_dragged.drag(pygame.mouse.get_pos(), disp)

                # Draws weapon slots if inventory is closed
                elif not displayInventory:
                    weapons.draw(disp)

                # toggle pause menu
                if not pressed_keys[K_ESCAPE]:  # stops flickering when trying to pause/unpause by only allowing new key-presses
                    esc_registering = True
                if pressed_keys[K_ESCAPE] and esc_registering:
                    gamestate = 2
                    esc_registering = False

            elif gamestate == 2:  # Pause  ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
                # Fills in the gaps around the edge of the map
                disp.fill((150,120,40))

                # draws the background
                disp.blit(area_map, drifted_map_pos)   # draws the map in the background
                bob.draw(disp, (scr_wi//2 - X_drift, scr_hi//2 - Y_drift))    # draws the player
                for item in enemies:
                    if dist((item.draw_location), (bob.rect_on_screen[0], bob.rect_on_screen[1])) <= (scr_hi * 1.2):
                        item.draw(disp, drifted_map_pos, blocks)   # draws the enemies
                for item in projectiles:
                    if dist((item.draw_location), (bob.rect_on_screen[0], bob.rect_on_screen[1])) <= (scr_hi * 1.2):
                        item.draw(disp)   # draws active bullets
                for item in obstacle_list:
                    if dist(item.draw_location, (bob.rect_on_screen[0], bob.rect_on_screen[1])) <= (scr_hi * 1.2):
                        item.draw(disp, drifted_map_pos, projectiles)

                # Shades the background slightly, and displayes the pause text
                disp.blit(pause_shading, (0,0))
                disp.blit(Pause_Text, Pause_Text_rect)

                # Displays and hanlding clicks on the quit button
                if Quit_Button((50, scr_hi-150), disp).collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    print("\nended\n")
                    pygame.quit()
                    sys.exit()

                # Displays and handles clicks on the refresh button
                if Refresh_Button((50, scr_hi-300), disp).collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    gamestate = 1
                    bob.refresh()
                    Playing = False # breaks from playing loop, returning the program to randomise and rebuild the map
                    inventory = inventory_class(screensize)

                # Toggle pause - unpause
                if not pressed_keys[K_ESCAPE]:  # stops flickering when trying to pause/unpause by only allowing new key-presses
                    esc_registering = True
                if pressed_keys[K_ESCAPE] and esc_registering:  # unpause the game when new keypress is registered
                    gamestate = 1
                    esc_registering = False
            
            elif gamestate == 3:   # Dead   ||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||
                disp.fill((100,0,0))

                # Display and get clicks on quit button
                if Quit_Button((50, scr_hi-150), disp).collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    print("\nended\n")
                    pygame.quit()
                    sys.exit()

                # Display and get click on refresh button
                if Refresh_Button((50, scr_hi-300), disp).collidepoint(pygame.mouse.get_pos()) and pygame.mouse.get_pressed()[0]:
                    gamestate = 0
                    bob.refresh()
                    inventory = inventory_class(screensize)
                    Playing = False
            
            if pressed_keys[K_g]:
                print(shotgun.firing_order)

            cursor.draw(disp)

            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    print("\nended\n")
                    pygame.quit()
                    sys.exit()
            pygame.time.Clock().tick(120)
