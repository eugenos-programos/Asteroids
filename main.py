import math
import sys
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

    def display_menu(self):
        while self.game_state == "Menu":
            gameDisplay.fill(black)
            x = display_width / 2
            y = display_height / 4
            GameProcess.draw_text("ASTEROIDS", yellow, x, y, 100, font='cambria')
            GameProcess.draw_text("Press SPACE to START", white, x, y + 150, 50)
            GameProcess.draw_text("Press SHIFT to see records", white, x, y + 250, 50)
            GameProcess.draw_text("Press TAB to see game rules", white, x, y + 350, 50)
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
                    if event.key == pygame.KMOD_SHIFT:
                        self.game_state = "Records"
                    if event.key == pygame.K_TAB:
                        self.game_state = "Help"
            pygame.display.update()
            timer.tick(5)

    def game_loop(self, display_state="Menu"):
        self.__init__(display_state)
        while self.game_state != "Exit":
            self.display_menu()
            # User inputs
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_state = "Exit"
                if event.type == pygame.KEYDOWN:
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
