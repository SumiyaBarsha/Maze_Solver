from time import sleep
import pygame
import pygame_menu
from pygame_menu import themes
import const

pygame.init()
w, h = 1000, 600
surface = pygame.display.set_mode((w+200, h))
difficulty_level = 1

def set_difficulty(value, difficulty):
    global difficulty_level
    difficulty_level = difficulty
    print(value)
    print(difficulty)

def start_the_game():
    if difficulty_level == 1:     
        const.set_initial_val(400, 400, 200, cell_size=40)
    elif difficulty_level == 2:     
        const.set_initial_val(700, 500, 600)
    elif difficulty_level == 3:     
        const.set_initial_val(1100, 600, 1100, cell_size=25)

    import maze
    maze.main(difficulty_level)

def level_menu():
    main_menu._open(level_menu)

# Main menu
main_menu = pygame_menu.Menu(
    'Maze Solver', w + 200, h, theme=themes.THEME_BLUE
)

main_menu = pygame_menu.Menu('Welcome', w+200, h, theme=themes.THEME_SOLARIZED)
main_menu.add.button('Play', start_the_game)
main_menu.add.button('Levels', level_menu)
main_menu.add.button('Quit', pygame_menu.events.EXIT)

level_menu = pygame_menu.Menu('Select a Difficulty', w+200, h, theme=themes.THEME_DARK)
level_menu.add.selector('Difficulty: ', [('Easy', 1), ('Medium', 2), ('Hard', 3)], onchange=set_difficulty)
level_menu.add.button('Back', pygame_menu.events.BACK)

while True:
    events = pygame.event.get()
    for event in events:
        if event.type == pygame.QUIT:
            pygame.quit()
            exit()

    if main_menu.is_enabled():
        main_menu.update(events)
        main_menu.draw(surface)

    pygame.display.update()
