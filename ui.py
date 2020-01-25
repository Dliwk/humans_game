import pygame


class TextLabel(pygame.sprite.Sprite):
    def __init__(self, groups, rect, text, color):
        super().__init__(*groups)
        self.text = text
        self.rect = rect
        font = pygame.font.Font(None, rect.height - 5)
        self.image = font.render(text, 1, color)

    def set_value(self, color, text):
        self.text = text
        font = pygame.font.Font(None, self.rect.height - 5)
        self.image = font.render(self.text, 1, color)


class Button(pygame.sprite.Sprite):
    def __init__(self, groups, rect, action,
                 color_inactive, color_focus, color_active, text, text_color):
        super().__init__(*groups)
        self.rect = rect
        self.action = action
        self.color_inactive = color_inactive
        self.color_active = color_active
        self.color_focus = color_focus

        self.pressed_time = 0
        self.released_time = 0

        self.active = False
        self.in_focus = False

        self.image = pygame.Surface((self.rect.width, self.rect.height))
        self.image.fill(color_inactive)

        self.text = TextLabel(groups, rect, text, text_color)

    def update(self, event=None):
        if not event:
            return
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos) and not self.active and \
               (pygame.time.get_ticks() - self.released_time) > 20:
                self.image.fill(self.color_active)
                self.active = True
                self.pressed_time = pygame.time.get_ticks()
        elif event.type == pygame.MOUSEMOTION:
            if self.rect.collidepoint(event.pos) and not self.active and \
               not self.in_focus:
                self.image.fill(self.color_focus)
                self.in_focus = True
            elif (
                not self.rect.collidepoint(event.pos) and
                not self.active and
                self.in_focus
            ):
                self.in_focus = False
                self.image.fill(self.color_inactive)
        elif event.type == pygame.MOUSEBUTTONUP:
            if self.rect.collidepoint(event.pos) and self.active and \
               (pygame.time.get_ticks() - self.pressed_time) > 20:
                self.action()
                self.released_time = pygame.time.get_ticks()
            self.active = False
            self.image.fill(self.color_inactive)
