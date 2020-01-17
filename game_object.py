import threading
import random
import time
import pygame
import images
from enum import Enum
import conf

RESPAWN_TIME = 10
MAX_VELOCITY = 50
HEALTH_LINE_UP = 20


def do_slowmo(smtime):
    conf.FPS = 15
    conf.slowmo_time = smtime


class GameObject(pygame.sprite.Sprite):
    image = None
    all_sprites = None
    walls = None
    grounds = None
    entities = None
    players = None

    @classmethod
    def init(cls, all_sprites, walls, grounds, entities, players, camera, center):
        cls.all_sprites = all_sprites
        cls.walls = walls
        cls.grounds = grounds
        cls.entities = entities
        cls.players = players
        cls.camera = camera
        cls.center = center

    def __init__(self, groups, velocity):
        super().__init__(*groups)

        self.onground = False
        self.onwall = False
        self.last_onground_time = pygame.time.get_ticks()
        self.velocity = list(velocity)

    def _update(self):
        if isinstance(self, MaterialObject):
            if pygame.sprite.spritecollideany(self, GameObject.walls):
                if self.velocity[0]:
                    self.rect.x -= self.velocity[0]
                self.onwall = True
            else:
                self.onwall = False
            if pygame.sprite.spritecollideany(self, GameObject.grounds):
                if self.velocity[1] < 0:
                    self.rect.y -= self.velocity[1]
                self.onground = True
            else:
                self.onground = False
        if isinstance(self, GravitationalObject):
            self.velocity[1] += 0.4

        self.update_pos()

        if self.onground:
            if self.velocity[1] > 0:
                self.velocity[1] = 0
        if self.onwall:
            if self.velocity[0]:
                self.velocity[0] //= 2
        # if self.onwall:
        #     if abs(self.velocity[0]) > 0.5:
        #         self.velocity[0] = 0

        # Сила трения
        if self.onground:
            k = 1
        else:
            k = 0.2

        if abs(self.velocity[0]) < k:
            self.velocity[0] = 0
        if abs(self.velocity[1]) < 0.4:
            self.velocity[1] = 0
        if self.velocity[0] > 0:
            self.velocity[0] -= k
        if self.velocity[0] < 0:
            self.velocity[0] += k
        if self.velocity[1] > 0:
            self.velocity[1] -= 0.2
        if self.velocity[1] < 0:
            self.velocity[1] += 0.2

        if self.velocity[0] > MAX_VELOCITY:
            self.velocity[0] = MAX_VELOCITY
        if self.velocity[0] < -MAX_VELOCITY:
            self.velocity[0] = -MAX_VELOCITY
        if self.velocity[1] > MAX_VELOCITY:
            self.velocity[1] = MAX_VELOCITY
        if self.velocity[1] < -MAX_VELOCITY:
            self.velocity[1] = -MAX_VELOCITY

        self.rect = self.rect.move(self.velocity)

        if self.onground:
            self.last_onground_time = pygame.time.get_ticks()

    def update(self, event=None):
        if event:
            self.parse_event(event)  # Parse event (e.g. click on object)
        else:
            self._update()  # Обновляем в соответствии с законами физики))0)

    def parse_event(self, event):
        pass

    def update_pos(self):
        pass


class GravitationalObject:
    pass


class MaterialObject:
    pass


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    def apply_all(self, objects):
        for obj in objects:
            self.apply(obj)

    # позиционировать камеру на объекте target
    def update(self, target):
        self.dx = -(target.rect.x + target.rect.w // 2 - self.width // 2)
        self.dy = -(target.rect.y + target.rect.h // 2 - self.height // 2)


class Condition(Enum):
    Normal = 0
    Punching = 1
    Confused = 2
    Knockout = 3
    Died = 4


class Player(GameObject, GravitationalObject, MaterialObject):
    def __init__(self, groups, pos, name, velocity):
        super().__init__(groups, velocity)
        self.frames = images.frames.player_normal
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.blocks = []

        self.health_line = HealthLine(
            (GameObject.all_sprites,), (pos[0], pos[1] + HEALTH_LINE_UP))
        self.health_line.set(100)
        self.name = Text(
            (GameObject.all_sprites,),
            (pos[0], pos[1] + 30),
            name
        )
        self.condition = Condition.Normal
        self.condition_update_time = 0
        self.punch_time = 0
        self.respawn_time_text = None
        self.respawn_time = 0
        self.last_respawn_tick = 0
        self.knockout_time = 0

    def punch_all(self):
        power = 1
        if self.condition == Condition.Normal:  # Первый удар
            power *= 2
        power += abs(self.velocity[0]) + abs(self.velocity[1] * 2) * 2
        if self.condition == Condition.Punching:
            for entity in pygame.sprite.spritecollide(
                    self, GameObject.entities, False):
                if entity != self:
                    hitfrom_x = 1 if entity.rect.x > self.rect.x else -1
                    hitfrom_y = 1 if entity.rect.y > self.rect.y else -1
                    entity.hit(power, (
                        power * hitfrom_x,
                        power * hitfrom_y / 100
                    ))
        if self.condition == Condition.Normal:
            self.condition = Condition.Punching
            self.condition_update_time = pygame.time.get_ticks()

    def hit(self, val, vec=(0, 0), confusion=True):
        self.velocity[0] += vec[0]
        self.velocity[1] += vec[1]
        if self.condition == Condition.Died:
            return
        self.health_line.set(self.health_line.get() - val)
        if val >= 35:
            self.condition = Condition.Knockout
            self.knockout_time = val / 100 * 6000 * 60 / conf.FPS
            self.condition_update_time = pygame.time.get_ticks()
        if self.health_line.get() <= 0:
            if val >= 35:
                do_slowmo(60)
            self.die()

    def update_pos(self):
        self.health_line.rect.x = self.rect.x
        self.health_line.rect.y = self.rect.y

        self.name.rect.x = self.rect.x
        self.name.rect.y = self.rect.y - 12

        if self.respawn_time_text:
            self.respawn_time_text.rect.x = self.rect.x - 40
            self.respawn_time_text.rect.y = self.rect.y - 30

            if pygame.time.get_ticks() - self.last_respawn_tick > 660 * 60 / conf.FPS:
                self.last_respawn_tick = pygame.time.get_ticks()
                self.respawn_time -= 1
                self.respawn_time_text.set('Возрождение через: ' + str(self.respawn_time))
            if self.respawn_time == 0:
                self.respawn()

        if self.condition not in (Condition.Normal, Condition.Died, Condition.Knockout):
            if pygame.time.get_ticks() - self.condition_update_time > 600 * 60 / conf.FPS:
                self.condition = Condition.Normal
        elif self.condition == Condition.Knockout:
            if pygame.time.get_ticks() - self.condition_update_time > self.knockout_time:
                self.condition = Condition.Normal

        if self.condition == Condition.Normal:
            self.frames = images.frames.player_normal
        elif self.condition == Condition.Died:
            self.frames = images.frames.player_died
        elif self.condition == Condition.Knockout:
            self.frames = images.frames.player_knockout
        elif self.condition == Condition.Punching:
            if self.punch_time >= 1:
                self.punch_all()
                self.punch_time = 0
            self.punch_time += 0.1
            self.frames = images.frames.player_punching

        self.cur_frame = (self.cur_frame + 0.05 * len(self.frames)) % len(self.frames)
        self.image = self.frames[int(self.cur_frame)]

        if self.condition in (Condition.Knockout, Condition.Died):
            return

        if self.onground and self.velocity[1] > 10:
            self.hit(self.velocity[1] ** 2 / 10)
        if self.onwall and self.velocity[0] > 20:
            self.hit(self.velocity[0] ** 2 / 20)

        self.parse_input()

        self.health_line.rect.x = self.rect.x
        self.health_line.rect.y = self.rect.y

        if GameObject.center.rect.y - self.rect.y < -3000:
            self.die()

        self.hit(-0.02)
        if abs(self.velocity[0]) < 0.5 and abs(self.velocity[1]) < 0.5:
            self.hit(-0.18)

    def rise(self):
        if self.condition != Condition.Died:
            return
        self.health_line = HealthLine(
            (GameObject.all_sprites,),
            (self.rect.x, self.rect.y + 20)
        )
        self.health_line.set(100)
        self.condition = Condition.Normal
        self.condition_update_time = pygame.time.get_ticks()

    def respawn(self):
        self.rise()
        self.rect.x = GameObject.center.rect.x
        self.rect.y = GameObject.center.rect.y
        self.last_onground_time = pygame.time.get_ticks()
        self.velocity = [0, 0]
        if isinstance(self.respawn_time_text, pygame.sprite.Sprite):
            self.respawn_time_text.kill()
        self.respawn_time_text = None

    def auto_respawn(self, sec):
        self.respawn_time_text = Text((GameObject.all_sprites,), (self.rect.x - 40, self.rect.y - 40),
                                      'Возрождение через: ' + str(sec), 15)
        self.respawn_time = sec

    def die(self, auto_respawn=True):
        if self.condition == Condition.Died:
            return
        self.health_line.kill()
        self.condition = Condition.Died
        self.condition_update_time = pygame.time.get_ticks()
        if auto_respawn:
            self.auto_respawn(RESPAWN_TIME)

    def parse_event(self, event):
        pass

    def parse_input(self):
        pass


class LocalPlayer(Player):
    def __init__(self, groups, pos, name, velocity, keymap):
        super().__init__(groups, pos, name, velocity)
        self.keymap = keymap

    def parse_input(self):
        # DEBUG:
        if pygame.key.get_pressed()[pygame.K_m]:
            self.velocity[0] += 10
        if pygame.key.get_pressed()[pygame.K_b]:
            do_slowmo(15 * 5)

        if self.condition in (Condition.Died, Condition.Knockout):
            return
        if pygame.key.get_pressed()[self.keymap[0]] and self.velocity[0] > -10:
            self.velocity[0] -= 2
        if pygame.key.get_pressed()[self.keymap[1]] and self.velocity[0] < 10:
            self.velocity[0] += 2
        if pygame.key.get_pressed()[self.keymap[2]]:
            if self.onground:
                self.velocity[1] -= 15

    def parse_event(self, event):
        if event.type == pygame.KEYDOWN:
            if event.key == self.keymap[3] and self.condition != Condition.Punching:
                self.punch_all()


class Ground(GameObject):
    def __init__(self, groups, pos):
        super().__init__(groups, (0, 0))
        self.image = images.stone_block_image
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]


class Wall(GameObject):
    def __init__(self, groups, pos):
        super().__init__(groups, (0, 0))
        self.image = images.stone_block_image
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]


class HealthLine(pygame.sprite.Sprite):
    def __init__(self, groups, pos):
        super().__init__(*groups)
        self.image = pygame.Surface((40, 1))
        self.image.fill(pygame.Color('black'))
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]
        self.health = self.image.subsurface(
            pygame.Rect(0, 0, 40, 1))
        self.health.fill(pygame.Color('green'))
        self.val = 100

    def set(self, val):
        del self.health
        if val > 100:
            val = 100
        self.image.fill(pygame.Color('black'))
        self.health = self.image.subsurface(
            pygame.Rect(0, 0, val * 0.4, 1))
        self.health.fill(pygame.Color('green'))
        self.val = val

    def get(self):
        return self.val


class Text(pygame.sprite.Sprite):
    def __init__(self, groups, pos, name, size=12):
        super().__init__(*groups)
        self.size = size
        self.image = pygame.font.Font(None, size).render(
            name, 1, pygame.Color('black')
        )
        self.rect = self.image.get_rect()
        self.rect.x = pos[0]
        self.rect.y = pos[1]

    def set(self, text):
        self.image = pygame.font.Font(None, self.size).render(
            text, 1, pygame.Color('black')
        )


class PlayerBot(Player):
    def __init__(self, groups, pos, name, velocity):
        super().__init__(groups, pos, name, velocity)
        self.keys = [False, False, False, False]
        self.ai_thread = threading.Thread(target=self.ai, daemon=True)
        self.ai_thread.start()

    def ai(self):
        while True:
            key = random.randint(0, 3)
            self.keys[key] = True
            time.sleep(random.random() * 5)
            self.keys[key] = False

    def parse_input(self):
        if self.condition in (Condition.Died, Condition.Knockout):
            return
        if self.keys[0] and self.velocity[0] > -10:
            self.velocity[0] -= 2
        if self.keys[1] and self.velocity[0] < 10:
            self.velocity[0] += 2
        if self.keys[2]:
            if self.onground:
                self.velocity[1] -= 15
        if self.keys[3] and self.condition != Condition.Punching:
            self.punch_all()


class AdvancedPlayerBot(PlayerBot):
    def __init__(self, groups, pos, name, velocity, sleep_time=2):
        self.sleep_time = sleep_time
        super().__init__(groups, pos, name, velocity)
        self.punching_ai_thread = threading.Thread(target=self.punching_ai, daemon=True)
        self.punching_ai_thread.start()

    def ai(self):
        while True:
            player = random.choice(GameObject.players.sprites())
            if player.rect.x < self.rect.x:
                self.keys[0] = True
                self.keys[1] = False
            else:
                self.keys[0] = False
                self.keys[1] = True
            self.keys[2] = player.rect.y - 80 < self.rect.y
            time.sleep(random.random() * self.sleep_time)

    def punching_ai(self):
        while True:
            for player in GameObject.players.sprites():
                if (abs(player.rect.x - self.rect.x) < 40 or abs(80 < player.rect.x - self.rect.x) < 160) and \
                        self.condition != Condition.Punching:
                    self.punch_all()
            time.sleep(random.random() * self.sleep_time / 4)
