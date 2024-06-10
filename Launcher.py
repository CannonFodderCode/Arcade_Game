import pygame, sys
from pygame.locals import *

pygame.init()

scr_wi = 800
scr_hi = 600

pygame.display.set_caption("screen size config")
disp = pygame.display.set_mode((scr_wi, scr_hi))

font = pygame.font.Font(None, 50)
smallfont = pygame.font.Font(None, 30)

mousedown = [False, False, False]  # indexing a list avoids cross-talk issues when detecting objects that cna be clicked with LMB or RMB
def clicked(item, mousebutton): # only returns true when the mouse is released (used for things that shouldnt be pressed 120 times per second...)
    global mousedown
    if mousedown[mousebutton] and not pygame.mouse.get_pressed()[mousebutton] and item.collidepoint(mouse):
        mousedown[mousebutton] = False
        return True # if it was pressed, and has jkust been released
    if not pygame.mouse.get_pressed()[mousebutton] and item.collidepoint(mouse):
        mousedown[mousebutton] = False
        return False
    elif pygame.mouse.get_pressed()[mousebutton] and item.collidepoint(mouse):
        mousedown[mousebutton] = True


intructions = font.render("Click your desired resolution", True, (255,255,0))

# creates buttons for the 3 options of screen sizes:
button720 = pygame.Surface((200, 80))
button720.fill((120,0,0))
t720 = font.render("1280x720", True, (255,255,255))  # small screen
button720.blit(t720, (5,5))
button720_rect = button720.get_rect(topleft = (5,60))

button1080 = pygame.Surface((200, 80))
button1080.fill((120,0,0))
t1080 = font.render("1920x1080", True, (255,255,255))  # standard screen
button1080.blit(t1080, (5,5))
button1080_rect = button1080.get_rect(topleft = (5,160))

button1440 = pygame.Surface((200, 80))
button1440.fill((120,0,0))
t1440 = font.render("2560x1440", True, (255,255,255))  # big screen
button1440.blit(t1440, (5,5))
button1440_rect = button1440.get_rect(topleft = (5,260))


# Creating a fullscreen toggle button
fullscreen = pygame.Surface((200,100))
fullscreen.fill((255,0,0))
FS_text = font.render("Fullscreen", True, (255,255,255))
fullscreen.blit(FS_text, (2,2))
FS_text = smallfont.render("click to toggle", True, (255,255,255))
fullscreen.blit(FS_text, (2,53))
FS_Button = fullscreen.get_rect(topleft = (220, 60))
fullscreenBOOL = False

def Config():  # the program in function form for easy calling in other programs
    global FS_Button, fullscreenBOOL, mouse
    while True:
        mouse = pygame.mouse.get_pos()
        disp.fill((0,0,0))
        disp.blit(intructions, (5,5))
        disp.blit(button720, button720_rect)  # Creating all the buttons on the screen
        disp.blit(button1080, button1080_rect)
        disp.blit(button1440, button1440_rect)
        disp.blit(fullscreen, FS_Button)

        if clicked(FS_Button, 0):
            if fullscreenBOOL:  # disable fullscreen
                fullscreen.fill((255,0,0))    # Fill with red background
                FS_text = font.render("Fullscreen", True, (255,255,255))
                fullscreen.blit(FS_text, (2,2))
                FS_text = smallfont.render("click to toggle", True, (255,255,255))
                fullscreen.blit(FS_text, (2,53))
                FS_Button = fullscreen.get_rect(topleft = (220, 60))
                fullscreenBOOL = False
            elif not fullscreenBOOL:  # enable fulscreen
                fullscreen.fill((0,255,0))    # Fill with green background
                FS_text = font.render("Fullscreen", True, (255,255,255))
                fullscreen.blit(FS_text, (2,2))
                FS_text = smallfont.render("click to toggle", True, (255,255,255))
                fullscreen.blit(FS_text, (2,53))
                FS_Button = fullscreen.get_rect(topleft = (220, 60))
                fullscreenBOOL = True
        if button720_rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
            scr_hi = 720
            scr_wi = 1280
            break
        elif button1080_rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
            scr_hi = 1080
            scr_wi = 1920
            break
        elif button1440_rect.collidepoint(mouse) and pygame.mouse.get_pressed()[0]:
            scr_hi = 1440
            scr_wi = 2560
            break

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
    print(scr_hi, scr_wi, fullscreenBOOL)
    return [scr_hi, scr_wi, fullscreenBOOL]
#pygame.quit()