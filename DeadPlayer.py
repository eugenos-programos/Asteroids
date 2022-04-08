import random
from GameDisplay import *
import math


# Create class for shattered ship
class DeadPlayer:
    def __init__(self, x, y, length):
        self.angle = random.randrange(0, 360) * math.pi / 180
        self.dir = random.randrange(0, 360) * math.pi / 180
        self.rotate_speed = random.uniform(-0.25, 0.25)
        self.x = x
        self.y = y
        self.length = length
        self.speed = random.randint(2, 8)

    def update_dead_player(self):
        pygame.draw.line(gameDisplay, white,
                         (self.x + self.length * math.cos(self.angle) / 2,
                          self.y + self.length * math.sin(self.angle) / 2),
                         (self.x - self.length * math.cos(self.angle) / 2,
                          self.y - self.length * math.sin(self.angle) / 2))
        self.angle += self.rotate_speed
        self.x += self.speed * math.cos(self.dir)
        self.y += self.speed * math.sin(self.dir)
