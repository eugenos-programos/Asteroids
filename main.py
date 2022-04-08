import math
import sys

import pygame.event

from GameCharacteristics import *
import random
from DeadPlayer import DeadPlayer
from Asteroids import Asteroid
from Player import Player
from Saucer import Saucer
from Bullet import Bullet

# Make surface and display
pygame.display.set_caption("Asteroids")
timer = pygame.time.Clock()


class GameProcess:
    def __init__(self, starting_state="Menu"):
        self.game_state = starting_state
        self.player_state = "Alive"
        self.player_blink = 0
        self.player_pieces = []
        self.player_dying_delay = 0
        self.player_invi_dur = 0
        self.hyperspace = 0
        self.next_level_delay = 0
        self.bullet_capacity = 4
        self.bullets = []
        self.asteroids = []
        self.stage = 3
        self.score = 0
        self.live = 2
        self.one_up_multiplier = 1
        self.play_one_up_sfx = 0
        self.intensity = 0
        self.player = Player(display_width / 2, display_height / 2)
        self.saucer = Saucer()
        self.sounds = load_sounds()

    @staticmethod
    def draw_text(msg, color, x, y, s, center=True, font="Calibri"):
        screen_text = pygame.font.SysFont(font, s).render(msg, True, color)
        if center:
            rect = screen_text.get_rect()
            rect.center = (x, y)
        else:
            rect = (x, y)
        gameDisplay.blit(screen_text, rect)

    @staticmethod
    def is_colliding(x, y, x_to, y_to, size):
        is_colliding_var = False
        if x_to - size < x < x_to + size and y_to - size < y < y_to + size:
            is_colliding_var = True
        return is_colliding_var

    def help(self):
        gameDisplay.fill(black)
        while self.game_state == "Help":
            x = display_width / 2
            y = display_height / 8
            GameProcess.draw_text("Help feedback", green, x, y, 100, font='cambria')
            GameProcess.draw_text("The goal of the game was to get as many points as possible by shooting asteroids and flying saucers and avoiding the debris.", white, x, y + 100, 20)
            GameProcess.draw_text("The player controls the intended spaceship, which can rotate left and right, but only also move and shoot, but forward.", white, x, y + 250, 20)
            GameProcess.draw_text("Each level begins with the discovery of several asteroids drifting at random points on the screen.", white, x, y + 400, 20)
            GameProcess.draw_text("The last screen is wrapped towards each other, When the player hits an asteroid, it breaks into pieces that are smaller but move faster.", white, x, y + 550, 20)
            GameProcess.draw_text("Periodically bright flying saucer; the large cymbal simply moves from one edge of the screen to the other, the smaller cymbals are aimed at the player.", white, x, y + 700, 20)
            GameProcess.draw_text("You can shoot by passing SPACE key and move to the random space point passing SHIFT key!", white, x, y + 850, 20)
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "Menu"
            timer.tick(5)

    def display_menu(self):
        while self.game_state == "Menu":
            gameDisplay.fill(black)
            x = display_width / 2
            y = display_height / 4
            GameProcess.draw_text("ASTEROIDS", yellow, x, y, 100, font='cambria')
            GameProcess.draw_text("Press SPACE to START", white, x, y + 150, 50)
            GameProcess.draw_text("Press F9 to see records", white, x, y + 250, 50)
            GameProcess.draw_text("Press CAPS to see game rules", white, x, y + 350, 50)
            GameProcess.draw_text("Press ESC to EXIT", white, x, y + 450, 50)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "Exit"
                    if event.key == pygame.K_SPACE:
                        self.game_state = "Playing"
                    if event.key == pygame.K_F9:
                        self.game_state = "Records"
                        self.records()
                    if event.key == pygame.K_CAPSLOCK:
                        self.game_state = "Help"
                        self.help()
            pygame.display.update()
            timer.tick(5)

    def records(self):
        gameDisplay.fill(black)
        while self.game_state == "Records":
            x = display_width / 2
            y = display_height / 4
            records = read_records()
            records_dict = dict(sorted(records.items(), key=lambda item: item[1]))
            GameProcess.draw_text("Game Records", green, x, y, 100)
            GameProcess.draw_text("Name                 Score", yellow, x, y + 100, 50)
            index = 1
            for name in reversed(records_dict.keys()):
                GameProcess.draw_text("{}. {}                   {}".format(index, name, records_dict[name]), white, x, y + 100 + 100 * index, 50)
                index += 1
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.game_state = "Menu"
            timer.tick(5)

    def record_box(self):
        font = pygame.font.Font(None, 32)
        clock = pygame.time.Clock()
        x = display_width / 2
        y = display_height / 2
        input_box = pygame.Rect(x - 50, y - 30, 140, 32)
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color = color_inactive
        active = False
        text = ''
        done = False
        pygame.display.update()

        while not done:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.MOUSEBUTTONDOWN:
                    # If the user clicked on the input_box rect.
                    if input_box.collidepoint(event.pos):
                        # Toggle the active variable.
                        active = not active
                    else:
                        active = False
                    # Change the current color of the input box.
                    color = color_active if active else color_inactive
                if event.type == pygame.KEYDOWN:
                    if active:
                        if event.key == pygame.K_RETURN:
                            self.name = text
                            gameDisplay.fill(black)
                            self.change_records()
                        elif event.key == pygame.K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode
            gameDisplay.fill((30, 30, 30))
            GameProcess.draw_text("Congrats! Yoy gain top-3 score! Enter you name!", green, x, y - 80, 50)
            # Render the current text.
            txt_surface = font.render(text, True, color)
            # Resize the box if the text is too long.
            width = max(200, txt_surface.get_width()+10)
            input_box.w = width
            # Blit the text.
            gameDisplay.blit(txt_surface, (input_box.x+5, input_box.y+5))
            # Blit the input_box rect.
            pygame.draw.rect(gameDisplay, color, input_box, 2)
            pygame.display.flip()
            clock.tick(30)

    def check_record(self):
        records = read_records()
        is_record = False
        for name, record in list(records.items()):
            if record < self.score:
                is_record = True
                gameDisplay.fill(black)
                x = display_width / 2
                y = display_height / 4
                GameProcess.draw_text("Congrats! Yoy gain top-3 score! Enter you name!", green, x, y, 60)
                self.record_box()

    def change_records(self):
        records = read_records()
        records[self.name] = self.score
        minimal_key = ""
        minimal_record = 100000
        for name, record in list(records.items()):
            if record < minimal_record:
                minimal_record = record
                minimal_key = name
        del records[minimal_key]
        save_records(records)
        pygame.quit()
        sys.exit()

    def game_loop(self, display_state="Menu"):
        self.__init__(display_state)
        while self.game_state != "Exit":
            self.display_menu()
            # User inputs
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_state = "Exit"
                if self.game_state == "Playing" and event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP:
                        self.player.thrust = True
                    if event.key == pygame.K_LEFT:
                        self.player.rotate_speed = -1 * player_max_rotate_speed
                    if event.key == pygame.K_RIGHT:
                        self.player.rotate_speed = player_max_rotate_speed
                    if event.key == pygame.K_SPACE and self.player_dying_delay == 0 and len(self.bullets) < self.bullet_capacity:
                        self.bullets.append(Bullet(self.player.x, self.player.y, self.player.dir))
                    # Play SFX
                        pygame.mixer.Sound.play(self.sounds["snd_fire"])
                    if self.game_state == "Game Over":
                        if event.key == pygame.K_r:
                            self.game_state = "Exit"
                            self.game_loop("Playing")
                    if event.key == pygame.K_LSHIFT:
                        self.hyperspace = 30
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_UP:
                        self.player.thrust = False
                    if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                        self.player.rotate_speed = 0

            # Update player
            self.player.update_player()

            # Checking player invincible time
            if self.player_invi_dur != 0:
                self.player_invi_dur -= 1
            elif self.hyperspace == 0:
                self.player_state = "Alive"

            # Reset display
            gameDisplay.fill(black)

            # Hyperspace
            if self.hyperspace != 0:
                self.player_state = "Died"
                self.hyperspace -= 1
                if self.hyperspace == 1:
                    self.player.x = random.randrange(0, display_width)
                    self.player.y = random.randrange(0, display_height)

        # Check for collision w/ asteroid
            for asteroid in self.asteroids:
                asteroid.update_asteroid()
                if self.player_state != "Died":
                    if GameProcess.is_colliding(self.player.x, self.player.y, asteroid.x, asteroid.y, asteroid.size):
                        # Create ship fragments
                        self.player_pieces.append(
                            DeadPlayer(
                                self.player.x, self.player.y, 5 * player_size /
                                                              (2 * math.cos(math.atan(1 / 3)))))
                        self.player_pieces.append(
                            DeadPlayer(
                                self.player.x, self.player.y, 5 * player_size /
                                                              (2 * math.cos(math.atan(1 / 3)))))
                        self.player_pieces.append(
                            DeadPlayer(self.player.x, self.player.y, player_size))

                        # Kill player
                        self.player_state = "Died"
                        self.player_dying_delay = 30
                        self.player_invi_dur = 120
                        self.player.kill_player()

                        if self.live != 0:
                            self.live -= 1
                        else:
                            self.game_state = "Game Over"

                        # Split asteroid
                        if asteroid.type == "Large":
                            self.asteroids.append(Asteroid(asteroid.x, asteroid.y, "Normal"))
                            self.asteroids.append(Asteroid(asteroid.x, asteroid.y, "Normal"))
                            self.score += 20
                            # Play SFX
                            pygame.mixer.Sound.play(self.sounds["snd_bangL"])
                        elif asteroid.type == "Normal":
                            self.asteroids.append(Asteroid(asteroid.x, asteroid.y, "Small"))
                            self.asteroids.append(Asteroid(asteroid.x, asteroid.y, "Small"))
                            self.score += 50
                            # Play SFX
                            pygame.mixer.Sound.play(self.sounds["snd_bangM"])
                        else:
                            self.score += 100
                            # Play SFX
                            pygame.mixer.Sound.play(self.sounds["snd_bangS"])
                        self.asteroids.remove(asteroid)

            # Update ship fragments
            for player_piece in self.player_pieces:
                player_piece.update_dead_player()
                if player_piece.x > display_width or player_piece.x < 0 or player_piece.y > display_height or player_piece.y < 0:
                    self.player_pieces.remove(player_piece)

            # Check for end of stage
            if len(self.asteroids) == 0 and self.saucer.state == "Dead":
                if self.next_level_delay < 30:
                    self.next_level_delay += 1
                else:
                    self.stage += 1
                    self.intensity = 0
                    # Spawn asteroid away of center
                    for stage_index in range(self.stage):
                        x_to = display_width / 2
                        y_to = display_height / 2
                        while x_to - display_width / 2 < display_width / 4 and y_to - display_height / 2 < display_height / 4:
                            x_to = random.randrange(0, display_width)
                            y_to = random.randrange(0, display_height)
                        self.asteroids.append(Asteroid(x_to, y_to, "Large"))
                    self.next_level_delay = 0

            # Update intensity
            if self.intensity < self.stage * 450:
                self.intensity += 1

            # Saucer
            if self.saucer.state == "Dead":
                if random.randint(0, 6000) <= (self.intensity * 2) / (
                        self.stage * 9) and self.next_level_delay == 0:
                    self.saucer.create_saucer()
                    # Only small saucers >40000
                    if self.score >= 400:
                        self.saucer.type = "Small"
            else:
                # Set saucer targer dir
                acc = small_saucer_accuracy * 4 / self.stage
                self.saucer.bdir = math.degrees(
                    math.atan2(-self.saucer.y + self.player.y, -self.saucer.x + self.player.x) +
                    math.radians(random.uniform(acc, -acc)))

                self.saucer.update_saucer()
                self.saucer.draw_saucer()

                # Check for collision w/ asteroid
                for asteroid in self.asteroids:
                    if GameProcess.is_colliding(self.saucer.x, self.saucer.y, asteroid.x, asteroid.y,
                                                asteroid.size + self.saucer.size):
                        # Set saucer state
                        self.saucer.state = "Dead"

                        # Split asteroid
                        if asteroid.type == "Large":
                            self.asteroids.append(Asteroid(asteroid.x, asteroid.y, "Normal"))
                            self.asteroids.append(Asteroid(asteroid.x, asteroid.y, "Normal"))
                            # Play SFX
                            pygame.mixer.Sound.play(self.sounds["snd_bangL"])
                        elif asteroid.type == "Normal":
                            self.asteroids.append(Asteroid(asteroid.x, asteroid.y, "Small"))
                            self.asteroids.append(Asteroid(asteroid.x, asteroid.y, "Small"))
                            # Play SFX
                            pygame.mixer.Sound.play(self.sounds["snd_bangM"])
                        else:
                            # Play SFX
                            pygame.mixer.Sound.play(self.sounds["snd_bangS"])
                        self.asteroids.remove(asteroid)

                # Check for collision w/ bullet
                for bullet in self.bullets:
                    if GameProcess.is_colliding(bullet.x, bullet.y, self.saucer.x, self.saucer.y, self.saucer.size):
                        # Add points
                        if self.saucer.type == "Large":
                            self.score += 200
                        else:
                            self.score += 1000

                        # Set saucer state
                        self.saucer.state = "Dead"

                        # Play SFX
                        pygame.mixer.Sound.play(self.sounds["snd_bangL"])

                        # Remove bullet
                        self.bullets.remove(bullet)

                # Check collision w/ player
                if GameProcess.is_colliding(self.saucer.x, self.saucer.y, self.player.x, self.player.y,
                                            self.saucer.size):
                    if self.player_state != "Died":
                        # Create ship fragments
                        self.player_pieces.append(
                            DeadPlayer(
                                self.player.x, self.player.y, 5 * player_size /
                                                              (2 * math.cos(math.atan(1 / 3)))))
                        self.player_pieces.append(
                            DeadPlayer(
                                self.player.x, self.player.y, 5 * player_size /
                                                              (2 * math.cos(math.atan(1 / 3)))))
                        self.player_pieces.append(
                            DeadPlayer(self.player.x, self.player.y, player_size))

                        # Kill player
                        self.player_state = "Died"
                        self.player_dying_delay = 30
                        self.player_invi_dur = 120
                        self.player.kill_player()

                        if self.live != 0:
                            self.live -= 1
                        else:
                            self.game_state = "Game Over"

                        # Play SFX
                        pygame.mixer.Sound.play(self.sounds["snd_bangL"])

                # Saucer's bullets
                for bullet in self.saucer.bullets:
                    # Update bullets
                    bullet.update_bullet()

                    # Check for collision w/ asteroids
                    for asteroid in self.asteroids:
                        if GameProcess.is_colliding(bullet.x, bullet.y, asteroid.x, asteroid.y, asteroid.size):
                            # Split asteroid
                            if asteroid.type == "Large":
                                self.asteroids.append(Asteroid(asteroid.x, asteroid.y, "Normal"))
                                self.asteroids.append(Asteroid(asteroid.x, asteroid.y, "Normal"))
                                # Play SFX
                                pygame.mixer.Sound.play(self.sounds["snd_bangL"])
                            elif asteroid.type == "Normal":
                                self.asteroids.append(Asteroid(asteroid.x, asteroid.y, "Small"))
                                self.asteroids.append(Asteroid(asteroid.x, asteroid.y, "Small"))
                                # Play SFX
                                pygame.mixer.Sound.play(self.sounds["snd_bangL"])
                            else:
                            # Play SFX
                                pygame.mixer.Sound.play(self.sounds["snd_bangL"])

                            # Remove asteroid and bullet
                            self.asteroids.remove(asteroid)
                            self.saucer.bullets.remove(bullet)

                            break

                    # Check for collision w/ player
                    if GameProcess.is_colliding(self.player.x, self.player.y, bullet.x, bullet.y, 5):
                        if self.player_state != "Died":
                            # Create ship fragments
                            self.player_pieces.append(
                                DeadPlayer(
                                    self.player.x, self.player.y, 5 * player_size /
                                                        (2 * math.cos(math.atan(1 / 3)))))
                            self.player_pieces.append(
                                DeadPlayer(
                                    self.player.x, self.player.y, 5 * player_size /
                                                        (2 * math.cos(math.atan(1 / 3)))))
                            self.player_pieces.append(
                                DeadPlayer(self.player.x, self.player.y, player_size))

                            # Kill player
                            self.player_state = "Died"
                            self.player_dying_delay = 30
                            self.player_invi_dur = 120
                            self.player.kill_player()

                            if self.live != 0:
                                self.live -= 1
                            else:
                                self.game_state = "Game Over"
                            # Play SFX
                            pygame.mixer.Sound.play(self.sounds["snd_bangL"])
                            # Remove bullet
                            self.saucer.bullets.remove(bullet)

                    if bullet.life <= 0:
                        try:
                            self.saucer.bullets.remove(bullet)
                        except ValueError:
                            continue

            # Bullets
            for bullet in self.bullets:
                # Update bullets
                bullet.update_bullet()

                # Check for bullets collide w/ asteroid
                for asteroid in self.asteroids:
                    if asteroid.x - asteroid.size < bullet.x < asteroid.x + asteroid.size and asteroid.y - asteroid.size < bullet.y < asteroid.y + asteroid.size:
                        # Split asteroid
                        if asteroid.type == "Large":
                            self.asteroids.append(Asteroid(asteroid.x, asteroid.y, "Normal"))
                            self.asteroids.append(Asteroid(asteroid.x, asteroid.y, "Normal"))
                            self.score += 20
                            # Play SFX
                            pygame.mixer.Sound.play(self.sounds["snd_bangL"])
                        elif asteroid.type == "Normal":
                            self.asteroids.append(Asteroid(asteroid.x, asteroid.y, "Small"))
                            self.asteroids.append(Asteroid(asteroid.x, asteroid.y, "Small"))
                            self.score += 50
                            # Play SFX
                            pygame.mixer.Sound.play(self.sounds["snd_bangM"])
                        else:
                            self.score += 100
                            # Play SFX
                            pygame.mixer.Sound.play(self.sounds["snd_bangS"])
                        self.asteroids.remove(asteroid)
                        self.bullets.remove(bullet)

                        break

            # Destroying bullets
                if bullet.life <= 0:
                    try:
                        self.bullets.remove(bullet)
                    except ValueError:
                        continue

        # Extra live
            if self.score > self.one_up_multiplier * 10000:
                self.one_up_multiplier += 1
                self.live += 1
                self.play_one_up_sfx = 60
            # Play sfx
            if self.play_one_up_sfx > 0:
                self.play_one_up_sfx -= 1
                pygame.mixer.Sound.play(self.sounds["snd_extra"], 60)

        # Draw player
            if self.game_state != "Game Over":
                if self.player_state == "Died":
                    if self.hyperspace == 0:
                        if self.player_dying_delay == 0:
                            if self.player_blink < 5:
                                if self.player_blink == 0:
                                    self.player_blink = 10
                                else:
                                    self.player.draw_player()
                            self.player_blink -= 1
                        else:
                            self.player_dying_delay -= 1
                else:
                    self.player.draw_player()
            else:
                self.check_record()
                gameDisplay.fill(black)
                GameProcess.draw_text("Game Over", white, display_width / 2,
                                      display_height / 2, 100)
                GameProcess.draw_text("Press \"R\" to restart!", white, display_width / 2,
                                      display_height / 2 + 100, 50)
                self.live = -1
            # Draw score
            GameProcess.draw_text(str(self.score), white, 60, 20, 40, False)
            # Draw Lives
            for live_ in range(self.live + 1):
                Player(75 + live_ * 25, 75).draw_player()
            # Update screen
            pygame.display.update()
            # Tick fps
            timer.tick(30)

# Start game
GameProcess().game_loop()

# End game
pygame.quit()
quit()
