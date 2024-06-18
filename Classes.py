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
        self.maxHP = 10
        self.HP = self.maxHP
        self.rect_on_screen = pygame.Rect(500,500, 60,60)
    
    def draw(self, disp, location):
        self.location = location
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
            if self.rect_on_screen.collidepoint(bullet.draw_location) and bullet.allegiance == "ENEMY":
                self.HP -= bullet.damage
                #print(self.HP)
                bullet.kill()

        return [-self.DX, -self.DY]     # return movement update to allow map to adjust
    
class weapon(pygame.sprite.Sprite):
    def __init__(self, owner, type):
        super().__init__()

        self.image = pygame.Surface((40, 10))   # Temporary until I can get some decent art
        self.image.fill((0,0,0))
        
        self.rect = self.image.get_rect()
        self.owner = owner
        self.speed = 15
        self.damage = 3
        self.FR = 2  # in shots per second
        self.cooldown = 1/self.FR  # wait time after each shot
        self.timer = 0

    def draw(self, disp, mouse_pos):
        if mouse_pos[0] <= self.owner.location[0]:
            self.rect.center = (self.owner.rect_on_screen.center[0] - self.image.get_width()//2, self.owner.rect_on_screen.center[1])
            disp.blit(self.image, self.rect)
        else:
            self.rect.center = (self.owner.rect_on_screen.center[0] + self.image.get_width()//2, self.owner.rect_on_screen.center[1])
            disp.blit(self.image, self.rect)
    
    def shoot(self, projectile_group, map_pos, target):
        self.ready = ((time.time() - self.timer) > self.cooldown)
        if self.ready:
            bullet = Bullet((self.rect.center[0] - map_pos[0], self.rect.center[1] - map_pos[1]), (target[0] - map_pos[0], target[1] - map_pos[1]), "PLAYER", self.speed, self.damage)
            projectile_group.add(bullet)
            self.timer = time.time()

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
    def __init__(self, start_pos, target, allegiance, speed, damage):
        super().__init__()
        self.radius = 8
        self.image = pygame.Surface((self.radius * 2, self.radius * 2), SRCALPHA)
        self.image.fill((0,0,0,0))
        self.allegiance = allegiance  # track who the shot belongs to, used to decide if it can collide with an entity
        self.start_pos = start_pos
        self.speed = speed
        self.damage = damage
        self.target_pos = target
        pygame.draw.circle(self.image, (255,255,0),(self.radius, self.radius), self.radius)             # FIX THE TARGET FOR PLAYER-FIRED SHOTS, ooh, maybe its because its not accounting for map drift...?
        self.rect = self.image.get_rect(center = start_pos)
        self.angle = angle_finder(self.rect.center, target)
        self.dx = self.speed * cos(self.angle)
        self.dy = self.speed * sin(self.angle)
        self.X_position = self.rect.centerx
        self.Y_position = self.rect.centery
        self.draw_location = (0,0)  # placeholder for distance checks
        #print(self.allegiance, self.start_pos, self.target_pos)

    def update(self, blocks, map_position):
        self.draw_location = (self.rect[0] + map_position[0], self.rect[1] + map_position[1])
        self.X_position += self.dx   # done in 2 steps to avoid angles getting lost in int() conversion with coordinates
        self.Y_position += self.dy
        self.rect.centerx = self.X_position
        self.rect.centery = self.Y_position
        for item in blocks:
            if item.rect.colliderect(self.rect):  # removes the bullet if it hits a wall
                self.kill()


    def draw(self, disp):
        disp.blit(self.image, self.draw_location)
        #self.target_pos_debug = ((self.target_pos[0] + map_position[0], self.target_pos[1] + map_position[1]))
        #pygame.draw.line(disp, (255,0,0), (self.draw_location[0] + 5, self.draw_location[1] + 5), self.target_pos_debug, 2)

class enemy(pygame.sprite.Sprite):
    def __init__(self, location, resolution):
        super().__init__()

        self.image = pygame.Surface((40,40),SRCALPHA)   # image setup
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, (255,10,10), (20,20), 20)

        self.MaxHP = 6
        self.HP = self.MaxHP
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
        
        self.rect_on_screen = pygame.Rect(0, 0, self.image.get_width(), self.image.get_height())
        
        self.collision = [False,False,False,False]   # [TL, TR, BL, BR]  will be updated to track where collisions are happening on the sprite, so it can adjust accordingly
    
    def get_collisions(self, item):
        if self.rect.colliderect(item):
            if item.rect.collidepoint(self.rect.topleft):
                self.collision[0] = True
            if item.rect.collidepoint(self.rect.topright):
                self.collision[1] = True
            if item.rect.collidepoint(self.rect.bottomleft):
                self.collision[2] = True
            if item.rect.collidepoint(self.rect.bottomright):
                self.collision[3] = True
    
    def shunt(self):  # moves the enemy towards an open direction
        #top left, top right, bottom left, bottom right
            # if item is true, collision detected in that direction
        if self.collision != [False, False, False, False]:

            # getting unstuck from a flat wall
            if (not (self.collision[0] and self.collision[1])) and self.collision[2] and self.collision[3]:
                self.rect.centery -= 2
            elif self.collision[0] and self.collision[1] and (not (self.collision[2] and self.collision[3])):
                self.rect.centery += 2
            elif (not self.collision[0]) and self.collision[1] and (not self.collision[2]) and self.collision[3]:
                self.rect.centerx -= 2
            elif self.collision[0] and (not self.collision[1]) and self.collision[2] and (not self.collision[3]):
                self.rect.centerx += 2

            # getting out of a corner
            elif (not self.collision[0]) and self.collision[1] and self.collision[2] and self.collision[3]:
                self.rect.centerx -= 2
                self.rect.centery -= 2
            elif self.collision[0] and (not self.collision[1]) and self.collision[2] and self.collision[3]:
                self.rect.centerx += 2
                self.rect.centery -= 2
            elif self.collision[0] and self.collision[1] and (not self.collision[2]) and self.collision[3]:
                self.rect.centerx -= 2
                self.rect.centery += 2
            elif self.collision[0] and self.collision[1] and self.collision[2] and (not self.collision[3]):
                self.rect.centerx += 2
                self.rect.centery += 2
                print("DEBUG PLACEHOLDER - INTERNAL CORNER", self.MaxHP)
            
            # getting unstuck from a single corner
            elif not ((not self.collision[0]) and self.collision[1] and self.collision[2] and self.collision[3]):
                self.rect.centerx += 2
                self.rect.centery += 2
                print("DEBUG PLACEHOLDER - EXTERNAL CORNER", self.MaxHP)
            elif not (self.collision[0] and (not self.collision[1]) and self.collision[2] and self.collision[3]):
                self.rect.centerx -= 2
                self.rect.centery += 2
            elif not (self.collision[0] and self.collision[1] and (not self.collision[2]) and self.collision[3]):
                self.rect.centerx += 2
                self.rect.centery -= 2
            elif not (self.collision[0] and self.collision[1] and self.collision[2] and (not self.collision[3])):
                self.rect.centerx -= 2
                self.rect.centery -= 2

            # error message for somehow getting stuck entirely within a wall...
            elif self.collision == [True, True, True, True]:
                print("Dude is stuck in a wall, its not fixed")
            self.collision = [False,False,False,False]  # resets the list for the next use

    def LoS(self, target, obstructions_list,):   # Returns True if target is in range, and unshielded by items in arg[2], meaning Line of sight can be made.
        if dist(self.rect.center, target) < self.range:
            for item in obstructions_list:
                if (dist(self.rect.center, item.rect.center) < (self.range + 80)):
                    if item.rect.clipline(self.rect.center, target):
                        return False
            return True

    def attack(self, target, obstructions_list, bullets_group):
        self.ready = ((time.time() - self.timer) > self.cooldown)
        if self.ready:   # done sepperatly for run speed
            self.target_pos = target.rect.centerx + (self.scrn[0]//2), target.rect.centery + (self.scrn[1]//2)
            if self.LoS(self.target_pos, obstructions_list):
                bullet = Bullet(self.rect.center, self.target_pos, "ENEMY", self.bullet_speed, self.attack_damage)
                bullets_group.add(bullet)
                #print(self.rect.center)
                self.cooldown = random.choice(self.FR_Range)
                self.timer = time.time()

    def move(self, blocks, projectiles):
        self.debug = False  # update to enable collision check visuals, LOS drawing, and rect drawing
        if ((time.time() - self.movement_timer) > self.movement_cooldown) and not self.moving:
            self.XMovement = random.randrange(-250,250)
            self.YMovement = random.randrange(-250,250)  # selects a random direction to move in + random distance
            self.movement_cooldown = random.randint(1,2) # set the delay to 1 or 2 seconds
            self.moving = True  # commence the movement
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
                    self.get_collisions(item)
                    if self.ghost_rectX.colliderect(item):  # check if X movement is valid
                        if self.DX != 0:
                            self.DX = 0
                            self.XMovement = self.XMovement * -1
                        if self.debug:
                            self.image.fill((255,0,0))  
                    if self.ghost_rectY.colliderect(item):  # check if Y movement is valid
                        if self.DY != 0:
                            self.DY = 0
                            self.YMovement = self.YMovement * -1
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
        self.shunt()
        self.rect.centerx += self.DX  # update
        self.rect.centery += self.DY  # position

        #Bullet damage
        self.rect_on_screen.topleft = self.draw_location
        for bullet in projectiles:
            if self.rect_on_screen.collidepoint(bullet.draw_location) and bullet.allegiance == "PLAYER":
                self.HP -= bullet.damage
                #print(self.HP)
                bullet.kill()
                if self.HP <= 0:
                    self.kill()
    
    def save_map_pos(self, map_position):
        self.map_position = map_position
        self.draw_location = (self.rect[0] + map_position[0], self.rect[1] + map_position[1])  # turns location on map to location on screen

    def draw(self, disp, map_position, obstructions):
        self.draw_location = (self.rect[0] + map_position[0], self.rect[1] + map_position[1])  # turns location on map to location on screen
        disp.blit(self.image, self.draw_location)

        # BELOW: Draws a line between self and target. Black = Good LoS, Red = out of range. Purple = blocked by map-Block
        if self.debug:
            self.target_pos_debug = ((self.target_pos[0] + map_position[0], self.target_pos[1] + map_position[1]))
            if self.LoS(self.target_pos, obstructions):
                pygame.draw.line(disp, (0,0,0), (self.draw_location[0] + 20, self.draw_location[1] + 20), self.target_pos_debug, 3)
            elif dist(self.rect.center, self.target_pos) < self.range:
                pygame.draw.line(disp, (155,0,255), (self.draw_location[0] + 20, self.draw_location[1] + 20), self.target_pos_debug, 3)
            else:
                pygame.draw.line(disp, (255,0,0), (self.draw_location[0] + 20, self.draw_location[1] + 20), self.target_pos_debug, 3)

class melee(pygame.sprite.Sprite):
    def __init__(self, location, resolution):
        super().__init__()

        self.image = pygame.Surface((40,40),SRCALPHA)   # image setup
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, (150,10,180), (20,20), 20)

        self.MaxHP = 8
        self.HP = self.MaxHP
        self.position = location
        self.rect = self.image.get_rect(center = location)
        self.attack_damage = 2
        self.attack_rate = 0.5
        self.timer = 0
        self.scrn = resolution  # keeps track of what adjustments need to be made for screensize
        self.range = 200  # range to head directly for player
        self.movement_timer = 0
        self.movement_cooldown = random.randint(1,2)
        self.speed = 5
        self.moving = False
        
        self.attack_rect = pygame.Rect(0, 0 , self.image.get_width(), self.image.get_height())

        self.collision = [False,False,False,False]   # [TL, TR, BL, BR]  will be updated to track where collisions are happening on the sprite, so it can adjust accordingly

    def get_collisions(self, item):
        if self.rect.colliderect(item):
            if item.rect.collidepoint(self.rect.topleft):
                self.collision[0] = True
            if item.rect.collidepoint(self.rect.topright):
                self.collision[1] = True
            if item.rect.collidepoint(self.rect.bottomleft):
                self.collision[2] = True
            if item.rect.collidepoint(self.rect.bottomright):
                self.collision[3] = True
    
    def shunt(self):  # moves the enemy towards an open direction
        #top left, top right, bottom left, bottom right
            # if item is true, collision detected in that direction
        if self.collision != [False, False, False, False]:

            # getting unstuck from a flat wall
            if (not (self.collision[0] and self.collision[1])) and self.collision[2] and self.collision[3]:
                self.rect.centery -= 2
            elif self.collision[0] and self.collision[1] and (not (self.collision[2] and self.collision[3])):
                self.rect.centery += 2
            elif (not self.collision[0]) and self.collision[1] and (not self.collision[2]) and self.collision[3]:
                self.rect.centerx -= 2
            elif self.collision[0] and (not self.collision[1]) and self.collision[2] and (not self.collision[3]):
                self.rect.centerx += 2

            # getting out of a corner
            elif (not self.collision[0]) and self.collision[1] and self.collision[2] and self.collision[3]:
                self.rect.centerx -= 2
                self.rect.centery -= 2
            elif self.collision[0] and (not self.collision[1]) and self.collision[2] and self.collision[3]:
                self.rect.centerx += 2
                self.rect.centery -= 2
            elif self.collision[0] and self.collision[1] and (not self.collision[2]) and self.collision[3]:
                self.rect.centerx -= 2
                self.rect.centery += 2
            elif self.collision[0] and self.collision[1] and self.collision[2] and (not self.collision[3]):
                self.rect.centerx += 2
                self.rect.centery += 2
                print("DEBUG PLACEHOLDER - INTERNAL CORNER", self.MaxHP)
            
            # getting unstuck from a single corner
            elif self.collision[0] and not (self.collision[1] or self.collision[2] or self.collision[3]):
                self.rect.centerx += 2
                self.rect.centery += 2
                print("DEBUG PLACEHOLDER - EXTERNAL CORNER", self.MaxHP)
            elif self.collision[1] and not (self.collision[0] or self.collision[2] or self.collision[3]):
                self.rect.centerx -= 2
                self.rect.centery += 2
            elif self.collision[2] and not (self.collision[0] or self.collision[1] or self.collision[3]):
                self.rect.centerx += 2
                self.rect.centery -= 2
            elif self.collision[3] and not (self.collision[0] or self.collision[1] or self.collision[2]):
                self.rect.centerx -= 2
                self.rect.centery -= 2

            # error message for somehow getting stuck entirely within a wall...
            elif self.collision == [True, True, True, True]:
                print("Dude is stuck in a wall, its not fixed")
            self.collision = [False,False,False,False]  # resets the list for the next use

    def move(self, blocks, projectiles):
        self.debug = False  # update to enable collision check visuals, LOS drawing, and rect drawing
        if ((time.time() - self.movement_timer) > self.movement_cooldown) and not self.moving:
            self.XMovement = random.randrange(-250,250)
            self.YMovement = random.randrange(-250,250)  # selects a random direction to move in + random distance
            self.movement_cooldown = random.randint(1,2) # set the delay to 1 or 2 seconds
            self.moving = True  # commence the movement
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
                    self.get_collisions(item)
                    if self.ghost_rectX.colliderect(item):  # check if X movement is valid
                        if self.DX != 0:
                            self.DX = 0
                            self.XMovement = self.XMovement * -1
                        if self.debug:
                            self.image.fill((255,0,0))  
                    if self.ghost_rectY.colliderect(item):  # check if Y movement is valid
                        if self.DY != 0:
                            self.DY = 0
                            self.YMovement = self.YMovement * -1
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
        self.shunt()
        self.rect.centerx += self.DX  # update
        self.rect.centery += self.DY  # position
        
        #Bullet damage
        self.attack_rect.topleft = self.draw_location
        for bullet in projectiles:
            if self.attack_rect.collidepoint(bullet.draw_location) and bullet.allegiance == "PLAYER":
                self.HP -= bullet.damage
                #print(self.HP)
                bullet.kill()
                if self.HP <= 0:
                    self.kill()

    def attack(self, target, Null, Null2):
        self.ready = ((time.time() - self.timer) > self.attack_rate)
        if self.ready:
            if self.attack_rect.colliderect(target.rect_on_screen):
                target.HP -= self.attack_damage
                self.timer = time.time()

    def save_map_pos(self, map_position):
        self.map_position = map_position
        self.draw_location = (self.rect[0] + map_position[0], self.rect[1] + map_position[1])  # turns location on map to location on screen
    
    def draw(self, disp, map_position, null):
        self.draw_location = (self.rect[0] + map_position[0], self.rect[1] + map_position[1])  # turns location on map to location on screen
        disp.blit(self.image, self.draw_location)