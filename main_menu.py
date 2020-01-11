import pygame
import ui


def show_main_menu(display):
    display.fill(pygame.Color('gray'))
    _running = True
    return_val = 0

    def stop(return_value):
        nonlocal _running, return_val
        _running = False
        return_val = return_value

    menu_ui = pygame.sprite.Group()
    btn_start = ui.Button(
        (menu_ui, ),
        pygame.Rect(300, 275, 200, 50),
        lambda: stop(0),
        (10, 200, 10),
        (0, 180, 0),
        (0, 80, 0),
        "Начать игру",
        (255, 255, 255)
    )
    color = (0, 0, 0)
    title = ui.TextLabel(
        (menu_ui, ),
        pygame.Rect(300, 50, 200, 50),
        "Человечки!!!",
        color
    )
    while _running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            menu_ui.update(event)

        color = ((color[0] + 1) % 255, (color[1] - 1) % 255, (color[2] + 2) % 255)
        title.set_color(color)
        menu_ui.update()
        menu_ui.draw(display)

        pygame.display.flip()

    return return_val
