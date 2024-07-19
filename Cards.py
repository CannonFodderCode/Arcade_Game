import pygame, random
from pygame.locals import *

font = pygame.font.Font(None, 20)

class Card(pygame.sprite.Sprite): # a parent class of new cards
    def __init__(self):
        super().__init__()
        self.stored = False  # Is this card in the inventory?

    def set_image(self, colour):
        self.image_template = pygame.Surface((90,90), SRCALPHA)
        pygame.draw.rect(self.image_template,colour, (self.image_template.get_rect()), 0, 5)
        return self.image_template

    def drag(self, mouse, disp):
        self.rect_on_screen.center = mouse
        disp.blit(self.image, self.rect_on_screen)

    def place_to_map(self, location):
        self.location = (location[0] + random.randint(-10, 10), location[1] + random.randint(-10,10))

    def draw(self, disp, map_position):
        self.draw_location = (self.location[0] + map_position[0], self.location[1] + map_position[1])  # turns location on map to location on screen
        self.rect_on_screen.topleft = self.draw_location
        disp.blit(self.image, self.rect_on_screen)


#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||

'''SPECIAL CARDS'''
#Add some sparkles or something to make them look special

class slotsUP(Card):
    def __init__(self, location):
        super().__init__()
        self.special = True
        self.type = slotsUP
        self.image = self.set_image((255,255,0))
        self.rect = self.image.get_rect(center = (location[0],location[1]))
        self.rect.width = 100
        self.rect.height = 100
        self.text = font.render("Capacity", True, (255,255,255))
        self.image.blit(self.text, (5,5))
        self.location = location
        self.rect_on_screen = self.rect
        self.effect_type = "Capacity"
        self.effect_strength = 1
        self.description = font.render(f"Increaces the weapons spell capacity by {self.effect_strength}", True, (255,255,255), (0,0,0,150))

class rangeUP(Card):    # restrict to melee weapons only
    def __init__(self, location):
        super().__init__()
        self.special = True
        self.type = rangeUP
        self.image = self.set_image((255,255,0))
        self.rect = self.image.get_rect(center = (location[0],location[1]))
        self.rect.width = 100
        self.rect.height = 100
        self.text = font.render("Range", True, (255,255,255))
        self.image.blit(self.text, (5,5))
        self.location = location
        self.rect_on_screen = self.rect
        self.effect_type = "Range"
        self.effect_strength = 1
        self.description = font.render(f"Increaces the weapons hit range by {self.effect_strength}", True, (255,255,255), (0,0,0,150))


#|||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||||


class Homing(Card):
    def __init__(self, location):
        super().__init__()
        self.special = False
        self.type = Homing
        self.image = self.set_image((0,0,40))
        self.rect = self.image.get_rect(center = (location[0],location[1]))
        self.rect.width = 100
        self.rect.height = 100
        self.text = font.render("Homing", True, (255,255,255))
        self.image.blit(self.text, (5,5))
        self.location = location
        self.rect_on_screen = self.rect
        self.effect_type = "Homing"
        self.effect_strength = 10
        self.description = font.render(r"Projectile's path curves towards nearby enemies", True, (255,255,255), (0,0,0,150))

class Poison(Card):
    def __init__(self, location):
        super().__init__()
        self.special = False
        self.type = Poison
        self.image = self.set_image((0,120,0))
        self.rect = self.image.get_rect(center = (location[0],location[1]))
        self.rect.width = 100
        self.rect.height = 100
        self.text = font.render("Poison", True, (255,255,255))
        self.image.blit(self.text, (5,5))
        self.location = location
        self.rect_on_screen = self.rect
        self.effect_type = "DoT"
        self.effect_strength = 1
        self.description = font.render(r"Projectile poisons enemies for damage over time", True, (255,255,255), (0,0,0,150))

class DamageUP(Card):
    def __init__(self, location):
        super().__init__()
        self.special = False
        self.type = DamageUP
        self.image = self.set_image((140,0,0))
        self.rect = self.image.get_rect(center = (location[0],location[1]))
        self.rect.width = 100
        self.rect.height = 100
        self.text = font.render("DamageUP", True, (255,255,255))
        self.image.blit(self.text, (5,5))
        self.location = location
        self.rect_on_screen = self.rect
        self.effect_type = "Damage"
        self.effect_strength = 1
        self.description = font.render(f"Increases the projectiles damage by {self.effect_strength}", True, (255,255,255), (0,0,0,150))

class Pierce(Card):
    def __init__(self, location):
        super().__init__()
        self.special = False
        self.type = Pierce
        self.image = self.set_image((0,100,100))
        self.rect = self.image.get_rect(center = (location[0],location[1]))
        self.rect.width = 100
        self.rect.height = 100
        self.text = font.render("Pierce", True, (255,255,255))
        self.image.blit(self.text, (5,5))
        self.location = location
        self.rect_on_screen = self.rect
        self.effect_type = "Pierce"
        self.effect_strength = 1
        self.description = font.render(r"Adds , Pierce to the projectile", True, (255,255,255), (0,0,0,150))

class CritChance(Card):
    def __init__(self, location):
        super().__init__()
        self.special = False
        self.type = CritChance
        self.image = self.set_image((140,0,0))
        self.rect = self.image.get_rect(center = (location[0],location[1]))
        self.rect.width = 100
        self.rect.height = 100
        self.text = font.render("CritChance", True, (255,255,255))
        self.image.blit(self.text, (5,5))
        self.location = location
        self.rect_on_screen = self.rect
        self.effect_type = "Crit Chance"
        self.effect_strength = 10
        self.description = font.render(f"Adds {self.effect_strength}% chance to crit for higher damage", True, (255,255,255), (0,0,0,150))

CardTypes = [Homing, Poison, DamageUP, Pierce, CritChance]
CardTypes = [Pierce] # for debugging - only [x] cards spawn
SpecialCards = [slotsUP, rangeUP]