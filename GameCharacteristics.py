import pygame
from Utility.json_utility import load_sounds, read_default_characteristics, read_records, save_records

characteristics = read_default_characteristics()
display_width = characteristics["display_width"]
display_height = characteristics["display_height"]
white = characteristics["white"]
yellow = characteristics["yellow"]
black = characteristics["black"]
green = characteristics["green"]
player_size = characteristics["player_size"]
fd_fric = characteristics["fd_fric"]
bd_fric = characteristics["bd_fric"]
player_max_speed = characteristics["player_max_speed"]
player_max_rotate_speed = characteristics["player_max_rotate_speed"]
bullet_speed = characteristics["bullet_speed"]
saucer_speed = characteristics["saucer_speed"]
small_saucer_accuracy = characteristics["small_saucer_accuracy"]

gameDisplay = pygame.display.set_mode((display_width, display_height))
