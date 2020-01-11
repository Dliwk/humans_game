import os
import pygame


class Frames:
    def __init__(self, *frames_list):
        for i in frames_list:
            exec(f"self.{i['name']} = i['frames']")


def _load_image(name):
    path = os.path.join('data', 'textures', name)
    image = pygame.image.load(path).convert_alpha()
    return image


def load_image(name):
    return pygame.transform.scale(_load_image(name), (40, 40))


def load_frames(name):
    path = name.split('_')
    return [load_image(os.path.join(*path, i))
            for i in sorted(os.listdir(os.path.join('data', 'textures', *path)))]


def init():
    global frames, stone_block_image
    frames = Frames(*[{
        "name": i,
        "frames": load_frames(i)
    } for i in (
        'player_normal', 'player_punching', 'player_confused', 'player_knockout', 'player_died'
    )])
    stone_block_image = load_image('stone.png')


frames = None

stone_block_image = None

