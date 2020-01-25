import pygame
import ui


def show_main_menu(display):
    display.fill(pygame.Color('gray'))
    _running = True
    return_val = {
        'mode': 'two_players',
        'another_bot': False,
        'map': 'default'
    }

    def stop():
        nonlocal _running
        _running = False

    def set_mode():
        nonlocal return_val
        if return_val['mode'] == 'two_players':
            return_val['mode'] = 'with_bot'
            btn_mode.text.set_value(pygame.Color('white'), 'Против ИИ')
        elif return_val['mode'] == 'with_bot':
            return_val['mode'] = 'two_players'
            btn_mode.text.set_value(pygame.Color('white'), 'Против игрока')

    def set_bot_using():
        nonlocal return_val, btn_use_bot
        if not return_val['another_bot']:
            return_val['another_bot'] = True
            btn_use_bot.text.set_value(pygame.Color('white'), 'Использовать бота')
        else:
            return_val['another_bot'] = False
            btn_use_bot.text.set_value(pygame.Color('red'), 'Не использовать бота')

    def set_map():
        nonlocal return_val
        if return_val['map'] == 'default':
            return_val['map'] = '20x20'
            btn_map.text.set_value(pygame.Color('white'), 'Коробка 20x20')
        elif return_val['map'] == '20x20':
            return_val['map'] = '30x30'
            btn_map.text.set_value(pygame.Color('white'), 'Коробка 30x30')
        elif return_val['map'] == '30x30':
            return_val['map'] = '100x100'
            btn_map.text.set_value(pygame.Color('white'), 'Коробка 100x100')
        elif return_val['map'] == '100x100':
            return_val['map'] = 'default'
            btn_map.text.set_value(pygame.Color('white'), 'Карта по умолчанию')

    menu_ui = pygame.sprite.Group()
    btn_start = ui.Button(
        (menu_ui,),
        pygame.Rect(300, 475, 200, 50),
        stop,
        (10, 200, 10),
        (0, 180, 0),
        (0, 80, 0),
        "Начать игру",
        pygame.Color('white')
    )

    btn_use_bot = ui.Button(
        (menu_ui,),
        pygame.Rect(225, 175, 350, 50),
        set_bot_using,
        (10, 200, 10),
        (0, 180, 0),
        (0, 80, 0),
        "Не использовать бота",
        pygame.Color('red')
    )

    btn_mode = ui.Button(
        (menu_ui,),
        pygame.Rect(225, 125, 350, 50),
        set_mode,
        (10, 200, 10),
        (0, 180, 0),
        (0, 80, 0),
        'Против игрока',
        pygame.Color('white')
    )

    btn_map = ui.Button(
        (menu_ui,),
        pygame.Rect(225, 325, 350, 50),
        set_map,
        (10, 200, 10),
        (0, 180, 0),
        (0, 80, 0),
        'Карта по умолчанию',
        pygame.Color('white')
    )

    color = (0, 0, 0)
    title = ui.TextLabel(
        (menu_ui,),
        pygame.Rect(300, 50, 200, 50),
        "Человечки!!!",
        color
    )

    settings_title = ui.TextLabel(
        (menu_ui,),
        pygame.Rect(325, 100, 200, 30),
        "Настройки игры",
        pygame.Color('black')
    )
    while _running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                exit()
            menu_ui.update(event)

        color = ((color[0] + 1) % 255, (color[1] - 1) % 255, (color[2] + 2) % 255)
        title.set_value(color, 'Человечки!!!')
        menu_ui.update()
        menu_ui.draw(display)

        pygame.display.flip()

    return return_val
