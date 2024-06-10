'''
Allow the user to draw from top left, then press an output button to generate their drawing as a string of data, and write to an external JSON file
keyboard based menu. 2 for enemies, 1 for blocks, 0 for spaces, etc...
to do:
    Only paint updated blocks (requires 2 lists) to save performance
    Add a visual indication on what tiles are being drawn
    Add map panning to allow propper scaling on large maps
    Add a window to specify data to load, to eliminate terminal use

'''

import pygame, sys, time, json
from pygame.locals import *
import Launcher
import MapBuilding

pygame.init()

font = pygame.font.Font(None, 50)

scr_hi, scr_wi, fullscreenBOOL = Launcher.Config() # Launches config window, and stores screen variables


output_button = pygame.Surface((200,100))   # defines a button to output the map data
output_button.fill((0,255,255))
output_rect = output_button.get_rect(bottomright = (scr_wi,scr_hi))

draw = 0
scale = 25  # original zoom to load up at

scale_updated = True
def get_scale():    # displays the current zoom value to the user
    global scale, scale_updated, scalebutton, scalebuttonrect
    if scale_updated:
        scalebutton = pygame.Surface((100,100))
        scalebutton.fill((255,255,0))
        scalebuttonrect = scalebutton.get_rect(topright = output_rect.topleft)
        scaletext = font.render(str(scale), True, (255,0,0))
        scalebutton.blit(scaletext,(5,5))
        scale_updated = False
    disp.blit(scalebutton,scalebuttonrect)


def create_data(width, height):  # creates an array of 1s in the format required for map rendering
    data = [[1]]
    dataChanged = True
    while dataChanged:
        dataChanged = False
        if len(data)<height:
            data.append([1])
            dataChanged = True
        elif len(data)> height:
            data.remove(len(data))
            dataChanged = True
        for item in data:
            if len(item)<width:
                item.append(1)
                dataChanged = True
            elif len(item)>width:
                item.pop()
                dataChanged = True
    return data

load = input("input 'Yes' to load data: ")
if load.lower() == "yes":
    with open("SavedMapData.json","r") as file:    # load the saved list data into the "data" variable
        data = json.load(file)
else:
    print("Creating new map data:")
    data = create_data(int(input("set map width: ")),int(input("set map height: ")))   # ask the user to specify dimensions for the new map

surface = pygame.Surface((2560,1440))  # a blank surface that takes the blockmap to display

if fullscreenBOOL:        # Check if the user specified Fullscreen
    disp = pygame.display.set_mode((scr_wi, scr_hi), pygame.FULLSCREEN)
else:
    disp = pygame.display.set_mode((scr_wi, scr_hi))

def Paint_Map(surface, blueprint, wallcolour, floorcolour, scale):   # draws a grid of coloured boxes according to the "blueprint" arg
    surface.fill((0,0,0)) # temporary
    for Y_item in range(0,len(blueprint)):
        for X_item in range(0,len(blueprint[Y_item])):
            if blueprint[Y_item][X_item] == 1:
                block = MapBuilding.Block((X_item*scale,Y_item*scale), wallcolour, scale)
                surface.blit(block.image, block.rect)
            elif blueprint[Y_item][X_item] == 0:
                block = MapBuilding.Empty((X_item*scale,Y_item*scale), floorcolour, scale)
                surface.blit(block.image, block.rect)
            if blueprint[Y_item][X_item] == 2:
                block = MapBuilding.Block((X_item*scale,Y_item*scale), (255,0,0), scale)
                surface.blit(block.image, block.rect)

Paint_Map(surface, data, (100,100,20), (0,0,0), scale)  # create the initial map from the data input

while True:
    mouse = pygame.mouse.get_pos()
    disp.fill((0,0,0))
    pressed_keys = pygame.key.get_pressed()
    if pressed_keys[K_MINUS] and not (scale == 1):  # increases the "zoom" if above the minimum
        scale -= 1
        scale_updated = True
        Paint_Map(surface, data, (100,100,20), (0,0,0), scale)  # remakes the layout when the scale has been changed
    elif pressed_keys[K_EQUALS]:
        scale += 1
        scale_updated = True
        Paint_Map(surface, data, (100,100,20), (0,0,0), scale)
    for num in range(3):
        key = getattr(pygame, f"K_{num}")    # updates the currently drawn tile to the selected number
        if pressed_keys[key]:
            draw = num
    if pygame.mouse.get_pressed()[0]:
        X_value = (mouse[0]//scale)  # converts mouse coordinates into data index of the square hovered over
        Y_value = (mouse[1]//scale)
        if 0 <= X_value < len(data[0]) and 0 <= Y_value < len(data):
            data[Y_value][X_value] = draw
            Paint_Map(surface, data, (100,100,20), (0,0,0), scale)
    disp.blit(surface, (0,0))
    if pressed_keys[K_SPACE]:  # show the output button
        disp.blit(output_button, output_rect)
        get_scale()
        if output_rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
            print("Original Data:\n\n")
            output = MapBuilding.pad_data(MapBuilding.trim_data(data))
            for item in output:
                print(f"{item},")
            with open("SavedMapData.json","w") as file:  # writes data list to file
                try:
                    json.dump(output, file)
                    print("No exceptions raised")
                except:
                    print("Something went wrong with writing to a file")
            print("\n\n\n")
            print("Verifying JSON has been written properly:\n")
            with open("SavedMapData.json", "r", encoding="utf-8") as file:  # print out to check the file was written to properly
                try:
                    print(file.read())
                except:
                    pass
            time.sleep(0.5)  # prevent multiple triggers per second
    pygame.display.flip()
    for event in pygame.event.get():   # Quit detection
        if event.type == QUIT:
            pygame.quit()
            sys.exit()