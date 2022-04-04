import math
from GameDisplay import *
import random
from DeadPlayer import DeadPlayer
from Asteroids import Asteroid
from Player import Player
from Saucer import Saucer
from Bullet import Bullet

# Make surface and display
pygame.display.set_caption("Asteroids")
timer = pygame.time.Clock()

# Import sound effects
snd_fire = pygame.mixer.Sound("Sounds/fire.wav")
snd_bangL = pygame.mixer.Sound("Sounds/bangLarge.wav")
snd_bangM = pygame.mixer.Sound("Sounds/bangMedium.wav")
snd_bangS = pygame.mixer.Sound("Sounds/bangSmall.wav")
snd_extra = pygame.mixer.Sound("Sounds/extra.wav")
snd_saucerB = pygame.mixer.Sound("Sounds/saucerBig.wav")
snd_saucerS = pygame.mixer.Sound("Sounds/saucerSmall.wav")


# Create function to draw texts
def draw_text(msg, color, x, y, s, center=True):
    screen_text = pygame.font.SysFont("Calibri", s).render(msg, True, color)
    if center:
        rect = screen_text.get_rect()
        rect.center = (x, y)
    else:
        rect = (x, y)
    gameDisplay.blit(screen_text, rect)


# Create funtion to chek for collision
def is_colliding(x, y, xTo, yTo, size):
    if x > xTo - size and x < xTo + size and y > yTo - size and y < yTo + size:
        return True
    return False


def game_loop(startingState):
    # Init variables
    game_state = startingState
    player_state = "Alive"
    player_blink = 0
    player_pieces = []
    player_dying_delay = 0
    player_invi_dur = 0
    hyperspace = 0
    next_level_delay = 0
    bullet_capacity = 4
    bullets = []
    asteroids = []
    stage = 3
    score = 0
    live = 2
    one_up_multiplier = 1
    play_one_up_sfx = 0
    intensity = 0
    player = Player(display_width / 2, display_height / 2)
    saucer = Saucer()

    # Main loop
    while game_state != "Exit":
        # Game menu
        while game_state == "Menu":
            gameDisplay.fill(black)
            draw_text("ASTEROIDS", white, display_width / 2, display_height / 2, 100)
            draw_text("Press any key to START", white, display_width / 2, display_height / 2 + 100, 50)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_state = "Exit"
                if event.type == pygame.KEYDOWN:
                    game_state = "Playing"
            pygame.display.update()
            timer.tick(5)

        # User inputs
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_state = "Exit"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    player.thrust = True
                if event.key == pygame.K_LEFT:
                    player.rtspd = -player_max_rtspd
                if event.key == pygame.K_RIGHT:
                    player.rtspd = player_max_rtspd
                if event.key == pygame.K_SPACE and player_dying_delay == 0 and len(bullets) < bullet_capacity:
                    bullets.append(Bullet(player.x, player.y, player.dir))
                    # Play SFX
                    pygame.mixer.Sound.play(snd_fire)
                if game_state == "Game Over":
                    if event.key == pygame.K_r:
                        game_state = "Exit"
                        game_loop("Playing")
                if event.key == pygame.K_LSHIFT:
                    hyperspace = 30
            if event.type == pygame.KEYUP:
                if event.key == pygame.K_UP:
                    player.thrust = False
                if event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    player.rtspd = 0

        # Update player
        player.update_player()

        # Checking player invincible time
        if player_invi_dur != 0:
            player_invi_dur -= 1
        elif hyperspace == 0:
            player_state = "Alive"

        # Reset display
        gameDisplay.fill(black)

        # Hyperspace
        if hyperspace != 0:
            player_state = "Died"
            hyperspace -= 1
            if hyperspace == 1:
                player.x = random.randrange(0, display_width)
                player.y = random.randrange(0, display_height)

        # Check for collision w/ asteroid
        for a in asteroids:
            a.update_asteroid()
            if player_state != "Died":
                if is_colliding(player.x, player.y, a.x, a.y, a.size):
                    # Create ship fragments
                    player_pieces.append(DeadPlayer(player.x, player.y, 5 * player_size / (2 * math.cos(math.atan(1 / 3)))))
                    player_pieces.append(DeadPlayer(player.x, player.y, 5 * player_size / (2 * math.cos(math.atan(1 / 3)))))
                    player_pieces.append(DeadPlayer(player.x, player.y, player_size))

                    # Kill player
                    player_state = "Died"
                    player_dying_delay = 30
                    player_invi_dur = 120
                    player.kill_player()

                    if live != 0:
                        live -= 1
                    else:
                        game_state = "Game Over"

                    # Split asteroid
                    if a.t == "Large":
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        score += 20
                        # Play SFX
                        pygame.mixer.Sound.play(snd_bangL)
                    elif a.t == "Normal":
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        score += 50
                        # Play SFX
                        pygame.mixer.Sound.play(snd_bangM)
                    else:
                        score += 100
                        # Play SFX
                        pygame.mixer.Sound.play(snd_bangS)
                    asteroids.remove(a)

        # Update ship fragments
        for f in player_pieces:
            f.update_dead_player()
            if f.x > display_width or f.x < 0 or f.y > display_height or f.y < 0:
                player_pieces.remove(f)

        # Check for end of stage
        if len(asteroids) == 0 and saucer.state == "Dead":
            if next_level_delay < 30:
                next_level_delay += 1
            else:
                stage += 1
                intensity = 0
                # Spawn asteroid away of center
                for i in range(stage):
                    xTo = display_width / 2
                    yTo = display_height / 2
                    while xTo - display_width / 2 < display_width / 4 and yTo - display_height / 2 < display_height / 4:
                        xTo = random.randrange(0, display_width)
                        yTo = random.randrange(0, display_height)
                    asteroids.append(Asteroid(xTo, yTo, "Large"))
                next_level_delay = 0

        # Update intensity
        if intensity < stage * 450:
            intensity += 1

        # Saucer
        if saucer.state == "Dead":
            if random.randint(0, 6000) <= (intensity * 2) / (stage * 9) and next_level_delay == 0:
                saucer.create_saucer()
                # Only small saucers >40000
                if score >= 40000:
                    saucer.type = "Small"
        else:
            # Set saucer targer dir
            acc = small_saucer_accuracy * 4 / stage
            saucer.bdir = math.degrees(math.atan2(-saucer.y + player.y, -saucer.x + player.x) + math.radians(random.uniform(acc, -acc)))

            saucer.update_saucer()
            saucer.draw_saucer()

            # Check for collision w/ asteroid
            for a in asteroids:
                if is_colliding(saucer.x, saucer.y, a.x, a.y, a.size + saucer.size):
                    # Set saucer state
                    saucer.state = "Dead"

                    # Split asteroid
                    if a.t == "Large":
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        # Play SFX
                        pygame.mixer.Sound.play(snd_bangL)
                    elif a.t == "Normal":
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        # Play SFX
                        pygame.mixer.Sound.play(snd_bangM)
                    else:
                        # Play SFX
                        pygame.mixer.Sound.play(snd_bangS)
                    asteroids.remove(a)

            # Check for collision w/ bullet
            for b in bullets:
                if is_colliding(b.x, b.y, saucer.x, saucer.y, saucer.size):
                    # Add points
                    if saucer.type == "Large":
                        score += 200
                    else:
                        score += 1000

                    # Set saucer state
                    saucer.state = "Dead"

                    # Play SFX
                    pygame.mixer.Sound.play(snd_bangL)

                    # Remove bullet
                    bullets.remove(b)

            # Check collision w/ player
            if is_colliding(saucer.x, saucer.y, player.x, player.y, saucer.size):
                if player_state != "Died":
                    # Create ship fragments
                    player_pieces.append(DeadPlayer(player.x, player.y, 5 * player_size / (2 * math.cos(math.atan(1 / 3)))))
                    player_pieces.append(DeadPlayer(player.x, player.y, 5 * player_size / (2 * math.cos(math.atan(1 / 3)))))
                    player_pieces.append(DeadPlayer(player.x, player.y, player_size))

                    # Kill player
                    player_state = "Died"
                    player_dying_delay = 30
                    player_invi_dur = 120
                    player.kill_player()

                    if live != 0:
                        live -= 1
                    else:
                        game_state = "Game Over"

                    # Play SFX
                    pygame.mixer.Sound.play(snd_bangL)

            # Saucer's bullets
            for b in saucer.bullets:
                # Update bullets
                b.update_bullet()

                # Check for collision w/ asteroids
                for a in asteroids:
                    if is_colliding(b.x, b.y, a.x, a.y, a.size):
                        # Split asteroid
                        if a.t == "Large":
                            asteroids.append(Asteroid(a.x, a.y, "Normal"))
                            asteroids.append(Asteroid(a.x, a.y, "Normal"))
                            # Play SFX
                            pygame.mixer.Sound.play(snd_bangL)
                        elif a.t == "Normal":
                            asteroids.append(Asteroid(a.x, a.y, "Small"))
                            asteroids.append(Asteroid(a.x, a.y, "Small"))
                            # Play SFX
                            pygame.mixer.Sound.play(snd_bangL)
                        else:
                            # Play SFX
                            pygame.mixer.Sound.play(snd_bangL)

                        # Remove asteroid and bullet
                        asteroids.remove(a)
                        saucer.bullets.remove(b)

                        break

                # Check for collision w/ player
                if is_colliding(player.x, player.y, b.x, b.y, 5):
                    if player_state != "Died":
                        # Create ship fragments
                        player_pieces.append(DeadPlayer(player.x, player.y, 5 * player_size / (2 * math.cos(math.atan(1 / 3)))))
                        player_pieces.append(DeadPlayer(player.x, player.y, 5 * player_size / (2 * math.cos(math.atan(1 / 3)))))
                        player_pieces.append(DeadPlayer(player.x, player.y, player_size))

                        # Kill player
                        player_state = "Died"
                        player_dying_delay = 30
                        player_invi_dur = 120
                        player.kill_player()

                        if live != 0:
                            live -= 1
                        else:
                            game_state = "Game Over"

                        # Play SFX
                        pygame.mixer.Sound.play(snd_bangL)

                        # Remove bullet
                        saucer.bullets.remove(b)

                if b.life <= 0:
                    try:
                        saucer.bullets.remove(b)
                    except ValueError:
                        continue

        # Bullets
        for b in bullets:
            # Update bullets
            b.update_bullet()

            # Check for bullets collide w/ asteroid
            for a in asteroids:
                if b.x > a.x - a.size and b.x < a.x + a.size and b.y > a.y - a.size and b.y < a.y + a.size:
                    # Split asteroid
                    if a.t == "Large":
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        asteroids.append(Asteroid(a.x, a.y, "Normal"))
                        score += 20
                        # Play SFX
                        pygame.mixer.Sound.play(snd_bangL)
                    elif a.t == "Normal":
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        asteroids.append(Asteroid(a.x, a.y, "Small"))
                        score += 50
                        # Play SFX
                        pygame.mixer.Sound.play(snd_bangM)
                    else:
                        score += 100
                        # Play SFX
                        pygame.mixer.Sound.play(snd_bangS)
                    asteroids.remove(a)
                    bullets.remove(b)

                    break

            # Destroying bullets
            if b.life <= 0:
                try:
                    bullets.remove(b)
                except ValueError:
                    continue

        # Extra live
        if score > one_up_multiplier * 10000:
            one_up_multiplier += 1
            live += 1
            play_one_up_sfx = 60
        # Play sfx
        if play_one_up_sfx > 0:
            play_one_up_sfx -= 1
            pygame.mixer.Sound.play(snd_extra, 60)

        # Draw player
        if game_state != "Game Over":
            if player_state == "Died":
                if hyperspace == 0:
                    if player_dying_delay == 0:
                        if player_blink < 5:
                            if player_blink == 0:
                                player_blink = 10
                            else:
                                player.draw_player()
                        player_blink -= 1
                    else:
                        player_dying_delay -= 1
            else:
                player.draw_player()
        else:
            draw_text("Game Over", white, display_width / 2, display_height / 2, 100)
            draw_text("Press \"R\" to restart!", white, display_width / 2, display_height / 2 + 100, 50)
            live = -1

        # Draw score
        draw_text(str(score), white, 60, 20, 40, False)

        # Draw Lives
        for l in range(live + 1):
            Player(75 + l * 25, 75).draw_player()

        # Update screen
        pygame.display.update()

        # Tick fps
        timer.tick(30)


# Start game
game_loop("Menu")

# End game
pygame.quit()
quit()
