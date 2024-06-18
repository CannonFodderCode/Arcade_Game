import pygame, sys
from pygame.locals import *

pygame.init()

PlayerHP_Image = pygame.Surface((300,300), pygame.SRCALPHA)
HP_Font = pygame.font.SysFont("Rockwell Extra Bold", 80, True)

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

        gamescale = scr_wi / 2560
        PlayerHP_Surface = pygame.Surface((300 * gamescale, 300 * gamescale), pygame.SRCALPHA)
        pygame.transform.scale(PlayerHP_Image, (300 * gamescale, 300 * gamescale), PlayerHP_Surface)
    display.blit(PlayerHP_Surface, (0,0))

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

        gamescale = scr_wi / 2560
        EnemyCount_Surface = pygame.Surface((300 * gamescale, 300 * gamescale), pygame.SRCALPHA)
        pygame.transform.scale(EnemyCount_Image, (300 * gamescale, 300 * gamescale), EnemyCount_Surface)
    display.blit(EnemyCount_Surface, (scr_wi-(EnemyCount_Surface.get_width()),0))


# image and rect setup for
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
    print(f"    {rect}.topleft = (location)")
    print(f"    end_surface.blit({image}, {rect})")
    print(f"    return {rect}")
    print("\n")

create_button("Quit", 200, 100, (255, 0, 0))