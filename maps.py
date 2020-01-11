import pygame
from game_object import Wall, Ground


def load_map(path, all_sprites, walls, grounds, namespace: list):
    with open(path, 'r') as file:
        for object_def in file.read().split('\n'):
            if object_def == '':
                continue
            name, pos_x, pos_y = object_def.split()
            pos_x = float(pos_x) * 40
            pos_y = float(pos_y) * 40
            if name == 'wall':
                namespace.append(Wall(
                    (all_sprites, walls),
                    (pos_x, pos_y)
                ))
            elif name == 'ground':
                namespace.append(Ground(
                    (all_sprites, grounds),
                    (pos_x, pos_y)
                ))
