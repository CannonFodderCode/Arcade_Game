from typing import Any
import pygame
from pygame.locals import *

pygame.init()

PlayerHP_Image = pygame.Surface((300,300), pygame.SRCALPHA)
HP_Font = pygame.font.SysFont("Rockwell Extra Bold", 80, True)
font = pygame.font.Font(None, 20)  # small font used in inventory descriptions

# The circle in the top-left that contains the Player's HP readout
def PlayerHP_Tab(display, player, updated, scr_wi):
    global PlayerHP_Surface
    if updated:  # if HP changed, then re-draw the pannel
        PlayerHP_Image.fill((0,0,0,0))
        pygame.draw.circle(PlayerHP_Image, (100,100,100), (100,100), 200)

        # player HP bar graphics
        percentageHP = (player.HP / player.maxHP)
        pygame.draw.rect(PlayerHP_Image, (50,50,50), (20, 50, 90, 180)) # black background
        pygame.draw.rect(PlayerHP_Image, (255,0,0), (20, (230 - (180 * percentageHP)), 90, (180 * percentageHP)))  # red current HP

        # player HP text
        HP_Text = HP_Font.render(str(player.HP), True, (255,255,255))
        HP_Text_rect = HP_Text.get_rect(center = (65, 140))
        PlayerHP_Image.blit(HP_Text, HP_Text_rect)
        updated = False

        # Scales the final image down to the size of the window
        gamescale = scr_wi / 2560
        PlayerHP_Surface = pygame.Surface((300 * gamescale, 300 * gamescale), pygame.SRCALPHA)
        pygame.transform.scale(PlayerHP_Image, (300 * gamescale, 300 * gamescale), PlayerHP_Surface)
    display.blit(PlayerHP_Surface, (0,0))

# The enemy count circle in the top right
EnemyCount_Image = pygame.Surface((300,300), pygame.SRCALPHA)
def EnemyCount_Tab(display, enemy_list, updated, scr_wi):
    global EnemyCount_Surface
    if updated:  # if EC changed, then re-draw the pannel
        EnemyCount_Image.fill((0,0,0,0))
        pygame.draw.circle(EnemyCount_Image, (100,100,100), (200,100), 200)

        # Enemy-Count text
        EC_Text = HP_Font.render(str(len(enemy_list)), True, (255,255,255))
        EC_Text_rect = EC_Text.get_rect(center = (65, 140))
        EnemyCount_Image.blit(EC_Text, EC_Text_rect)
        updated = False

        # Scales the final image down to the size of the window
        gamescale = scr_wi / 2560
        EnemyCount_Surface = pygame.Surface((300 * gamescale, 300 * gamescale), pygame.SRCALPHA)
        pygame.transform.scale(EnemyCount_Image, (300 * gamescale, 300 * gamescale), EnemyCount_Surface)
    display.blit(EnemyCount_Surface, (scr_wi-(EnemyCount_Surface.get_width()),0))


# Buttons
Quit_Image = pygame.Surface((200, 100))
Quit_Image.fill((255, 0, 0))
rendered_text = HP_Font.render('Quit', True, (255,255,255))
text_rect = rendered_text.get_rect(center = (100, 50))
Quit_Image.blit(rendered_text, text_rect)
Quit_Button_Rect = Quit_Image.get_rect()

def Quit_Button(location, end_surface):
    Quit_Button_Rect.topleft = (location)
    end_surface.blit(Quit_Image, Quit_Button_Rect)
    return Quit_Button_Rect


Refresh_Image = pygame.Surface((200, 100))
Refresh_Image.fill((255, 255, 0))
rendered_text = HP_Font.render('Refresh', True, (255,0,0))
text_rect = rendered_text.get_rect(center = (100, 50))
Refresh_Image.blit(rendered_text, text_rect)
Refresh_Button_Rect = Refresh_Image.get_rect()

def Refresh_Button(location, end_surface):
    Refresh_Button_Rect.topleft = (location)
    end_surface.blit(Refresh_Image, Refresh_Button_Rect)
    return Refresh_Button_Rect


# Level up buttons
Extra_HP_Image = pygame.Surface((200, 200))
Extra_HP_Image.fill((255, 0, 0))
rendered_text = HP_Font.render('Extra HP', True, (255,255,255))
text_rect = rendered_text.get_rect(center = (100, 100))
Extra_HP_Image.blit(rendered_text, text_rect)
Extra_HP_Button_Rect = Extra_HP_Image.get_rect()

def Extra_HP_Button(location, end_surface):
    Extra_HP_Button_Rect.center = (location)
    end_surface.blit(Extra_HP_Image, Extra_HP_Button_Rect)
    return Extra_HP_Button_Rect

Extra_Life_Image = pygame.Surface((200, 200))
Extra_Life_Image.fill((0, 255, 0))
rendered_text = HP_Font.render('Extra_Life', True, (255,255,255))
text_rect = rendered_text.get_rect(center = (100, 100))
Extra_Life_Image.blit(rendered_text, text_rect)
Extra_Life_Button_Rect = Extra_Life_Image.get_rect()

def Extra_Life_Button(location, end_surface):
    Extra_Life_Button_Rect.center = (location)
    end_surface.blit(Extra_Life_Image, Extra_Life_Button_Rect)
    return Extra_Life_Button_Rect


class inventory_class(pygame.sprite.Sprite):  # The class that handles storing all collected cards - opens with the tab key in game
    def __init__(self, resolution):
        super().__init__()
        self.empty_image = pygame.Surface((100,100), SRCALPHA)
        self.empty_image.fill((150,150,150,150))
        self.resolution = resolution
        self.coordinates = ((2* resolution[0]//3) - 325, (resolution[1]//2) - 325)
        self.empty_message = font.render(r"Empty - This slot can hold a card", True, (255,255,255), (100,0,0,150))
        self.items = []
        # Creates an array on empty boxes to diplay
        for x in range(6):
            for y in range(6):
                self.items.append([(self.coordinates[0] + x*110, self.coordinates[1] + y*110), None, self.empty_image])   # Location, Item_type, image, rect, is_coloured?
        for item in self.items:
            item.append(item[2].get_rect(topleft = item[0]))
            item.append(False)  # check if an item has been coloured as the closest to allow for re-colouring when it isnt
            item.append(self.empty_message)

    def draw(self,disp):
        for square in self.items:
            disp.blit(square[2], square[3])
    
    #Index: 0      1         2     3         4            5
    # Location, Item_type, image, rect, is_coloured?, description

    def update(self):  # Highlights a square closest to the draged sprite, showing which box it will end up in on release
        for item in self.items:
            if item[1] == None:
                if item[3].collidepoint(pygame.mouse.get_pos()):
                    item[2] = pygame.Surface((100,100), SRCALPHA)
                    item[2].fill((200,200,200,150))
                    item[4] = True
                else:
                    # Refill with the main colour
                    item[4] = False
                    item[2].fill((150,150,150,150))
    
    def assign(self, dragged_card):
        # Checks which slot is highlighted (touching the mouse) and if its empty, place the card in there
        for item in self.items:
            if item[1] == None:
                if item[4]:  # assigned in the "update" method, claiming that its the square that should be dropped into
                    item[1] = dragged_card.type # Assign type (will need updating)
                    item[2].blit(dragged_card.image, (5,5))
                    item[4] = False
                    item[5] = dragged_card.description
                    return True
        print("No location was found")
        return False  # Used to create a new card drop on the map if the card wasnt on an empty square

    def reset_images(self):  # returns any highlighted squares to  normal colour - called after dragging an item
        for item in self.items:
            if item[4]:
                item[2].fill((150,150,150,150))
                item[4] = False

# Stores weapons and displays their slots on the screen when playing & editing
class weapon_slots_class(pygame.sprite.Sprite):
    def __init__(self):
        self.empty_image = pygame.Surface((100,100), SRCALPHA)
        self.empty_image.fill((150,150,150,150))
        self.slots = []

        # Slot creation
        for item in range(3):
            self.slots.append([(10 + item*110, 10), None, None, self.empty_image])
        for item in self.slots:
            item.append(self.empty_image.get_rect(topleft = item[0]))
    # Location, Object, Item_type, image, rect
    def draw(self, disp):
        for item in self.slots:
            disp.blit(item[3], item[4])

    # Used to draw the slots & their contents in the inventory, to allow editing of each of the slots of all weapons
    def draw_inventory(self, disp):#, location):
        for slot in self.slots:
            disp.blit(slot[3], slot[4]) # Displays weapons
            X_coord = slot[0][0]
            Y_coord = slot[0][1] + slot[4][3] + 10 # drops down by the height of the rect + 10
            for item in slot[1].firing_order: # slot[1] == weapon object
                item[1].topleft = (X_coord, Y_coord)
                disp.blit(item[0], item[1])
                Y_coord += item[0].get_height() + 10

    def update(self):  # Highlights a square closest to the draged sprite, showing which box it will end up in on release
        for weapon in self.slots:
            for item in weapon[1].firing_order:
                if item[5] == None:
                    if item[1].collidepoint(pygame.mouse.get_pos()):
                        item[0] = pygame.Surface((100,100), SRCALPHA)
                        item[0].fill((200,200,200,150))
                        item[4] = True
                    else:
                        # Refill with the main colour
                        item[4] = False
                        item[0].fill((150,150,150,150))

    def assign(self, dragged_card):
        for slot in self.slots:
            for weapon_slot in slot[1].firing_order:
                if weapon_slot[4] and weapon_slot[2] == None:
                    weapon_slot[0] = dragged_card.image
                    weapon_slot[2] = dragged_card.effect_type
                    weapon_slot[3] = dragged_card.effect_strength
                    weapon_slot[5] = dragged_card.type
                    return True
        print("not on a weapon")
        return False

    def set_slot(self, slot_number, item):
        self.slots[slot_number][1] = item
        self.slots[slot_number][2] = item.type
        self.slots[slot_number][3] = item.image

    def update_cards(self, dragged_weapon):
        count = 0
        for item in self.slots:
            if item[4].collidepoint(pygame.mouse.get_pos()):
                self.assign(count, dragged_weapon)
            count += 1

# Outputs a button function in the terminal to save writing it from scratch...
def create_button(text, width, height, colour):
    name = text + "_Button"
    image = text + "_Image"
    rect = name + "_Rect"
    print("\n")
    print(f"{image} = pygame.Surface(({width}, {height}))")
    print(f"{image}.fill({colour})")
    print(f"rendered_text = HP_Font.render('{text}', True, (255,255,255))")
    print(f"text_rect = rendered_text.get_rect(center = ({width//2}, {height//2}))")
    print(f"{image}.blit(rendered_text, text_rect)")
    print(f"{rect} = {image}.get_rect()")
    print()
    print(f"def {name}(location, end_surface):")
    print(f"    {rect}.center = (location)")
    print(f"    end_surface.blit({image}, {rect})")
    print(f"    return {rect}")
    print("\n")

#create_button("Extra_Life", 200, 200, (0, 255, 0))