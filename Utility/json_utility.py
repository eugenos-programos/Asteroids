import json
import pygame


def write_default_characteristics(path="../json/characteristics.json"):
    """
    Function for writing default characteristics into file
    :param path: path to the file for writing
    :return: None
    """
    default_characteristics = {
        "display_width": 1920,
        "display_height": 1080,
        "white": (255, 255, 255),
        "yellow": (255, 255, 0),
        "black": (0, 0, 0),
        "player_size": 10,
        "fd_fric": 0.5,
        "bd_fric": 0.1,
        "player_max_speed": 20,
        "player_max_rotate_speed": 10,
        "bullet_speed": 15,
        "saucer_speed": 5,
        "small_saucer_accuracy": 10
    }
    with open(path, "w") as outfile:
        json.dump(default_characteristics, outfile)


def read_default_characteristics(path="../json/characteristics.json"):
    """
    Read characteristics from JSON file
    :param path: path to the file for reading
    :return: None
    """
    with open(path, 'r') as readfile:
        characteristics = json.load(readfile)
    transform_to_tuple = ["white", "yellow", "black"]
    for color in transform_to_tuple:
        characteristics[color] = tuple(characteristics[color])
    return characteristics


def load_sounds():
    """
    Load sounds from Sounds directory, and return their into
    dictionary
    :return: dict
    """
    pygame.init()
    sounds = dict()
    add_path = "./Sounds/"
    sounds["snd_fire"] = pygame.mixer.Sound(add_path + "fire.wav")
    sounds["snd_bangL"] = pygame.mixer.Sound(add_path + "bangLarge.wav")
    sounds["snd_bangM"] = pygame.mixer.Sound(add_path + "bangMedium.wav")
    sounds["snd_bangS"] = pygame.mixer.Sound(add_path + "bangSmall.wav")
    sounds["snd_extra"] = pygame.mixer.Sound(add_path + "extra.wav")
    sounds["snd_saucerB"] = pygame.mixer.Sound(add_path + "saucerBig.wav")
    sounds["snd_saucerS"] = pygame.mixer.Sound(add_path + "saucerSmall.wav")
    return sounds


if __name__ == "__main__":
    print(load_sounds())
