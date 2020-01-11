import pygame
import sys
from game_object import LocalPlayer, Wall, Ground, Camera, GameObject
from main_menu import show_main_menu
import images

# Инициализация...
pygame.init()
FPS = 60
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
    (80, -80),
    "Первый игрок",
    (0, 0),
    (pygame.K_a, pygame.K_d, pygame.K_w, pygame.K_f)
)
another_player = LocalPlayer(
    (all_sprites, players, entities),
    (80, -80),
    "Второй игрок",
    (0, 0),
    (pygame.K_LEFT, pygame.K_RIGHT, pygame.K_UP, pygame.K_RCTRL)
)
blocks = []
for i in range(100):
    blocks.append(Ground(
        (all_sprites, grounds),
        (40 * i - 80, 80)
    ))
for i in range(100):
    blocks.append(Wall(
        (all_sprites, walls),
        (-80, -40 * i + 80)
    ))
for i in range(100):
    blocks.append(Wall(
        (all_sprites, walls),
        (4000 - 80, -40 * i + 80)
    ))
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

    w = player.rect.x - another_player.rect.x
    h = player.rect.y - another_player.rect.y
    look_at.rect = pygame.Rect(another_player.rect.x, another_player.rect.y, w, h)
    camera.update(look_at)
    camera.apply_all(all_sprites.sprites())

    pygame.display.flip()
    clock.tick(FPS)
