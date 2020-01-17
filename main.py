import pygame
import sys
from game_object import LocalPlayer, Camera, GameObject, PlayerBot, AdvancedPlayerBot
from main_menu import show_main_menu
import images
from maps import load_map
import conf

# Инициализация...
pygame.init()
SIZE = WIDTH, HEIGHT = 800, 600
clock = pygame.time.Clock()
display = pygame.display.set_mode(SIZE)

if '-t' not in sys.argv:
    show_main_menu(display)

# Инициализация мира...
all_sprites = pygame.sprite.Group()
walls = pygame.sprite.Group()
grounds = pygame.sprite.Group()
entities = pygame.sprite.Group()
players = pygame.sprite.Group()
camera = Camera(WIDTH, HEIGHT)
center = pygame.sprite.Sprite(all_sprites)
center.image = pygame.Surface((0, 0))
center.rect = center.image.get_rect()
look_at = pygame.sprite.Sprite(all_sprites)
look_at.image = pygame.Surface((0, 0))
look_at.rect = pygame.Rect(0, 0, 0, 0)
GameObject.init(all_sprites, walls, grounds, entities, players, camera, center)
images.init()

player = LocalPlayer(
    (all_sprites, players, entities),
    (0, 0),
    "Первый игрок",
    (0, 0),
    (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_f)
)
# another_player = LocalPlayer(
#     (all_sprites, players, entities),
#     (0, 0),
#     "Второй игрок",
#     (0, 0),
#     (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_RCTRL)
# )
another_player = AdvancedPlayerBot(
    (all_sprites, entities),
    (0, 0),
    "Злой человек",
    (0, 0)
)
# bot2 = AdvancedPlayerBot(
#     (all_sprites, entities),
#     (0, 0),
#     "Второй злой человек",
#     (0, 0)
# )
blocks = []
with open('default_map.txt') as f:
    path_to_map = f.read().strip()
    load_map(path_to_map, all_sprites, walls, grounds, blocks)

# Конец инициализации...

_running = True
while _running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            _running = False
        all_sprites.update(event)

    display.fill(pygame.Color('gray'))
    all_sprites.draw(display)
    all_sprites.update()

    if conf.FPS != 60:
        conf.slowmo_time -= 1
    if conf.slowmo_time == 0:
        conf.FPS = 60

    w = another_player.rect.x - player.rect.x
    h = another_player.rect.y - player.rect.y
    if abs(w) > 1600 or abs(h) > 1600:
        w = player.rect.x
        h = player.rect.y
    look_at.rect = pygame.Rect(player.rect.x, player.rect.y, w, h)
    camera.update(look_at)
    camera.apply_all(all_sprites.sprites())

    pygame.display.flip()
    clock.tick(conf.FPS)
