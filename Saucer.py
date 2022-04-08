from GameCharacteristics import *
import math
import random
from Bullet import Bullet


class Saucer:
    def __init__(self):
        self.directory = None
        self.size = None
        self.x = 0
        self.y = 0
        self.state = "Dead"
        self.type = "Large"
        self.directory_choice = ()
        self.bullets = []
        self.cd = 0
        self.bdir = 0
        self.soundDelay = 0
        sounds = load_sounds()
        self.snd_saucerB = sounds["snd_saucerB"]
        self.snd_saucerS = sounds["snd_saucerS"]

    def update_saucer(self):
        # Move player
        self.x += saucer_speed * math.cos(self.directory * math.pi / 180)
        self.y += saucer_speed * math.sin(self.directory * math.pi / 180)

        # Choose random direction
        if random.randrange(0, 100) == 1:
            self.directory = random.choice(self.directory_choice)

        # Wrapping
        if self.y < 0:
            self.y = display_height
        elif self.y > display_height:
            self.y = 0
        if self.x < 0 or self.x > display_width:
            self.state = "Dead"

        # Shooting
        if self.type == "Large":
            self.bdir = random.randint(0, 360)
        if self.cd == 0:
            self.bullets.append(Bullet(self.x, self.y, self.bdir))
            self.cd = 30
        else:
            self.cd -= 1

        # Play SFX
        if self.type == "Large":
            pygame.mixer.Sound.play(self.snd_saucerB)
        else:
            pygame.mixer.Sound.play(self.snd_saucerS)

    def create_saucer(self):
        # Create saucer
        # Set state
        self.state = "Alive"

        # Set random position
        self.x = random.choice((0, display_width))
        self.y = random.randint(0, display_height)

        # Set random type
        if random.randint(0, 1) == 0:
            self.type = "Large"
            self.size = 20
        else:
            self.type = "Small"
            self.size = 10

        # Create random direction
        if self.x == 0:
            self.directory = 0
            self.directory_choice = (0, 45, -45)
        else:
            self.directory = 180
            self.directory_choice = (180, 135, -135)

        # Reset bullet cooldown
        self.cd = 0

    def draw_saucer(self):
        # Draw saucer
        pygame.draw.polygon(gameDisplay, white,
                            ((self.x + self.size, self.y),
                             (self.x + self.size / 2, self.y + self.size / 3),
                             (self.x - self.size / 2, self.y + self.size / 3),
                             (self.x - self.size, self.y),
                             (self.x - self.size / 2, self.y - self.size / 3),
                             (self.x + self.size / 2, self.y - self.size / 3)), 1)
        pygame.draw.line(gameDisplay, white,
                         (self.x - self.size, self.y),
                         (self.x + self.size, self.y))
        pygame.draw.polygon(gameDisplay, white,
                            ((self.x - self.size / 2, self.y - self.size / 3),
                             (self.x - self.size / 3, self.y - 2 * self.size / 3),
                             (self.x + self.size / 3, self.y - 2 * self.size / 3),
                             (self.x + self.size / 2, self.y - self.size / 3)), 1)
