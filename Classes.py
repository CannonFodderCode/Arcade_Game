import pygame, time, random
from math import *
from pygame.locals import *

def angle_finder(start, end):   # returns angles in radians
    angle = atan2((end[1]-start[1]),(end[0]-start[0]))
    return(angle % (2*pi))

class player(pygame.sprite.Sprite):
    def __init__(self, map_offset):
        super().__init__()
        self.image = pygame.Surface((60,60), SRCALPHA)
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image,(0,255,100), (30,30), 30)
        self.rect = self.image.get_rect(topleft = (-map_offset[0], -map_offset[1]))
        self.speed = 6
        self.HP = 10
    
    def draw(self, disp, location):
        self.rect_on_screen = pygame.Rect(location[0], location[1], 60,60)
        disp.blit(self.image, location)

    def move(self, blocks, scr_wi, scr_hi, projectiles):  # currently map_offset is not used due to techincal incompetence
        
        self.debug = False  # adjust to True for colour-change on colision
        
        self.DX = 0
        self.DY = 0
        if self.debug:
            self.image.fill((0,255,0))
        pressed_keys = pygame.key.get_pressed()
        if pressed_keys[K_w]:
            self.DY -= self.speed
        if pressed_keys[K_s]:
            self.DY += self.speed
        if pressed_keys[K_a]:
            self.DX -= self.speed
        if pressed_keys[K_d]:
            self.DX += self.speed
        self.ghost_rectX = pygame.Rect(self.rect.left + scr_wi//2 + self.DX,self.rect.top + scr_hi//2, self.rect.width,self.rect.height)
        self.ghost_rectY = pygame.Rect(self.rect.left + scr_wi//2, self.rect.top + scr_hi//2 + self.DY, self.rect.width,self.rect.height)
        if self.rect.collidelist(blocks):
            for item in blocks:
                if self.ghost_rectX.colliderect(item):  # check if X movement is valid
                    if self.DX > 0:
                        self.DX = item.rect.left - (self.ghost_rectX.right - self.DX)
                    elif self.DX < 0:
                        self.DX = item.rect.right - (self.ghost_rectX.left - self.DX)
                    if self.debug:
                        self.image.fill((255,0,0))  
                if self.ghost_rectY.colliderect(item):  # check if Y movement is valid
                    if self.DY > 0:
                        self.DY = item.rect.top - (self.ghost_rectY.bottom - self.DY)
                    elif self.DY < 0:
                        self.DY = item.rect.bottom - (self.ghost_rectY.top - self.DY)
                    if self.debug:
                        self.image.fill((255,0,0))
        self.rect.centerx += self.DX  # update
        self.rect.centery += self.DY  # position

        for bullet in projectiles:
            if self.rect_on_screen.collidepoint(bullet.draw_location): #and bullet.aligance == "ENEMY":
                self.HP -= bullet.damage
                print(self.HP)
                bullet.kill()

        return [-self.DX, -self.DY]     # return movement update to allow map to adjust
    

class crossheir(pygame.sprite.Sprite):
    def __init__(self):
        self.image = pygame.Surface((80,80), SRCALPHA)
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, (180,180,180,150), (40,40), 35, 5)     # Draws a cool crossheir picture
        pygame.draw.line(self.image, (180,180,180,150), (0,40), (20,40), 3)
        pygame.draw.line(self.image, (180,180,180,150), (40,80), (40,60), 3)
        pygame.draw.line(self.image, (180,180,180,150), (80,40), (60,40), 3)
        pygame.draw.line(self.image, (180,180,180,150), (40,0), (40,20), 3)
        self.rect = self.image.get_rect()
    
    def draw(self, disp):
        self.rect.center = pygame.mouse.get_pos()
        disp.blit(self.image, self.rect)

class Bullet(pygame.sprite.Sprite):
    def __init__(self, start_pos, target, aligance, speed, damage):
        super().__init__()
        self.image = pygame.Surface((10,10), SRCALPHA)
        self.image.fill((0,0,0,0))
        self.alilgence = aligance
        self.start_pos = start_pos
        self.speed = speed
        self.damage = damage
        self.target_pos = target
        pygame.draw.circle(self.image, (255,255,0),(5,5), 5)
        self.rect = self.image.get_rect(center = start_pos)
        self.angle = angle_finder(self.rect.center, target)
        self.dx = self.speed * cos(self.angle)
        self.dy = self.speed * sin(self.angle)
        self.X_position = self.rect.centerx
        self.Y_position = self.rect.centery

    def update(self, blocks):
        self.X_position += self.dx   # done in 2 steps to avoid angles getting lost in int() conversion with coordinates
        self.Y_position += self.dy
        self.rect.centerx = self.X_position
        self.rect.centery = self.Y_position
        for item in blocks:
            if item.rect.colliderect(self.rect):
                self.kill()


    def draw(self, disp, map_position):
        self.draw_location = (self.rect[0] + map_position[0], self.rect[1] + map_position[1])
        disp.blit(self.image, self.draw_location)
        self.target_pos_debug = ((self.target_pos[0] + map_position[0], self.target_pos[1] + map_position[1]))
        #pygame.draw.line(disp, (255,0,0), (self.draw_location[0] + 5, self.draw_location[1] + 5), self.target_pos_debug, 2)

class enemy(pygame.sprite.Sprite):
    def __init__(self, location, resolution):
        super().__init__()

        self.image = pygame.Surface((40,40),SRCALPHA)   # image setup
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, (255,10,10), (20,20), 20)

        self.position = location
        self.rect = self.image.get_rect(center = location)
        self.bullet_speed = 6
        self.attack_damage = 2
        self.FR_Range = (1,1.2,1.4,1.6,1.8,2)   # a range of delays when shooting to choose from
        self.timer = 0
        self.range = 700   # the maximum range at which to target the player
        self.scrn = resolution  # keeps track of what adjustments need to be made for screensize
        self.cooldown = random.choice(self.FR_Range)
        self.movement_timer = 0
        self.movement_cooldown = random.randint(1,2)
        self.speed = 4
        self.moving = False
    
    def LoS(self, target, obstructions_list,):   # Returns True if target is in range, and unshielded by items in arg[2], meaning Line of sight can be made.
        if dist(self.rect.center, target) < self.range:  # filters 
            for item in obstructions_list:
                if (dist(self.rect.center, item.rect.center) < (self.range + 80)):
                    if item.rect.clipline(self.rect.center, target):
                        return False
            return True

    def attack(self, target, obstructions_list, bullets_group):
        #for item in obstructions_list:
        #    pygame.draw.rect(disp, (0,0,0), item.rect, 1)
        self.ready = ((time.time() - self.timer) > self.cooldown)
        pressed_keys = pygame.key.get_pressed()
        self.target_pos = target.rect.centerx + (self.scrn[0]//2), target.rect.centery + (self.scrn[1]//2)
        if self.LoS(self.target_pos, obstructions_list) and self.ready:
            bullet = Bullet(self.rect.center, self.target_pos, "ENEMY", self.bullet_speed, self.attack_damage)
            bullets_group.add(bullet)
            self.cooldown = random.choice(self.FR_Range)
            self.timer = time.time()

    def move(self, blocks):
        self.debug = False
        if ((time.time() - self.movement_timer) > self.movement_cooldown) and not self.moving:
            self.XMovement = random.randrange(-250,250)
            self.YMovement = random.randrange(-250,250)  # selects a random direction to move in + random distance
            self.movement_cooldown = random.randint(1,2) # set the delay to 1 or 2 seconds
            self.moving = True  # commence the movement
            #print("line 157 - moving set to True, X&YMovement set")
        self.DX = 0
        self.DY = 0
        if self.debug:
            self.image.fill((0,255,0))   # DEBUG
        if self.moving:
            if self.YMovement < 0:
                self.DY -= self.speed
            if self.YMovement > 0:
                self.DY += self.speed
            if self.XMovement < 0:
                self.DX -= self.speed
            if self.XMovement > 0:
                self.DX += self.speed
            # creating 2 ghost rectangles in the direction of movement to check if movement is possible
            self.ghost_rectX = pygame.Rect(self.rect.left + self.DX, self.rect.top          , self.rect.width, self.rect.height)
            self.ghost_rectY = pygame.Rect(self.rect.left          , self.rect.top + self.DY, self.rect.width, self.rect.height)
            if self.rect.collidelist(blocks) != -1:
                for item in blocks:
                    if self.ghost_rectX.colliderect(item):  # check if X movement is valid
                        #print(f"{self.ghost_rectX} is X movement, {self.ghost_rectY} is Y movement.\n{self.XMovement} is target movement, {self.YMovement} is target movement.\n{self.DX} = DX, {self.DY} = DY\n\n")
                        if self.DX != 0:
                            self.DX = 0 #self.DX * -1
                            self.XMovement = self.XMovement * -1
                            #print(f"X-collision detected: values updated to {self.DX}, {self.XMovement}")
                        if self.debug:
                            self.image.fill((255,0,0))  
                    if self.ghost_rectY.colliderect(item):  # check if Y movement is valid
                        if self.DY != 0:
                            self.DY = 0# self.DY * -1
                            self.YMovement = self.YMovement * -1
                            #print(f"Y-collision detected: values updated to {self.DY}, {self.YMovement}")
                        if self.debug:
                            self.image.fill((255,0,0))
            self.XMovement -= self.DX
            self.YMovement -= self.DY
            if -self.speed <= self.XMovement <= self.speed:
                self.XMovement = 0
            if -self.speed <= self.YMovement <= self.speed:
                self.YMovement = 0
            if (-self.speed <= self.XMovement <= self.speed) and (-self.speed <= self.YMovement <= self.speed):
                self.moving = False  # stop movement
                self.movement_timer = time.time()  # start the timer until next movement
        if self.debug:
            print(self.DX, self.DY, "self.DX self.DY")
            print(self.XMovement, self.YMovement, "self.XMovement self.YMovement")
        self.rect.centerx += self.DX  # update
        self.rect.centery += self.DY  # position
    
    def draw(self, disp, map_position, obstructions):
        self.draw_location = (self.rect[0] + map_position[0], self.rect[1] + map_position[1])  # turns location on map to location on screen
        disp.blit(self.image, self.draw_location)

        # BELOW: Draws a line between self and target. Black = Good LoS, Red = out of range. Purple = blocked by map-Block
        self.target_pos_debug = ((self.target_pos[0] + map_position[0], self.target_pos[1] + map_position[1]))
        if self.LoS(self.target_pos, obstructions):
            pygame.draw.line(disp, (0,0,0), (self.draw_location[0] + 20, self.draw_location[1] + 20), self.target_pos_debug, 3)
        elif dist(self.rect.center, self.target_pos) < self.range:
            pygame.draw.line(disp, (155,0,255), (self.draw_location[0] + 20, self.draw_location[1] + 20), self.target_pos_debug, 3)
        else:
            pygame.draw.line(disp, (255,0,0), (self.draw_location[0] + 20, self.draw_location[1] + 20), self.target_pos_debug, 3)