import sys
import pygame
import random
from snake_utility import Snake, Cherry, SnakeGameStatusFlags
import json

def set_new_cherry_pos(snake_lst):
    """
    Sets new cherry position.

    :param snake_lst: List, containing all snake instances present in the game. This is needed
                      to check that cherry will not be placed onto a snake.
    :type snake_lst: list of Snake
    """

    new_cherry_pos = random.randrange(0, width, Snake.block_size), random.randrange(0, height, Snake.block_size)

    # check if new cherry position is within any of the snakes and set new one
    for snk in snake_lst:
        while new_cherry_pos in snk.block_pos_lst:
            new_cherry_pos = random.randrange(0, width, Snake.block_size), random.randrange(0, height, Snake.block_size)

    return new_cherry_pos


def init_game(config_data):
    """
    Initializes the game with configuration, defined in config_data.

    :param config_data: Dictionary, which contains configuration for the game, such as
                        game window dimensions, number of snakes, keyboard keys, etc.
    :type config_data: dict

    :return: Lists of initialized snakes and cherries.
    :rtype: tuple of list
    """
    # colors for snakes
    snake_colors = [(0, 255, 0),  # player 1 is green
                    (0, 0, 255),  # player 2 is blue
                    (255, 255, 50),  # player 3 is yellow
                    (205, 0, 205)]  # player 4 is purple

    # create snake instances
    init_snake_lst = []
    for i in range(config_data["num_snakes"]):
        keys = config_data["keys"][i]
        snake = Snake(start_pos=config_data["start_pos"][i],
                      move_keys={'up': pygame.__getattribute__(keys[0]),
                                 'right': pygame.__getattribute__(keys[1]),
                                 'down': pygame.__getattribute__(keys[2]),
                                 'left': pygame.__getattribute__(keys[3])},
                      color=snake_colors[i],
                      block_size=config_data["block_size"],
                      num_of_start_blocks=config_data["initial_snake_length"])

        init_snake_lst.append(snake)

    # create cherry instances
    init_cherry_lst = []
    for i in range(config_data["num_cherries"]):
        cherry = Cherry(block_size)
        cherry.set_new_random_position(init_snake_lst, config_data["main_window_size"])
        init_cherry_lst.append(cherry)

    return init_snake_lst, init_cherry_lst

def redraw_screen(snake_lst, cherry_lst, block_size):
    """
    Redraws screen with updated snake and cherry positions.

    :param snake_lst: List of all snakes in the game.
    :type snake_lst: list of Snake

    :param cherry_lst: List of all cherries in the game.
    :type cherry_lst: list of Cherry

    :param block_size: Size of one block of snake or cherry in pixels.
    :type block_size: int
    """
    # clear screen
    screen.fill(BLACK)

    # draw snakes
    for snake in snake_lst:
        for block_pos in snake.block_pos_lst:
            pygame.draw.rect(screen,
                             snake.color,
                             (block_pos[0], block_pos[1], block_size, block_size))

    # draw cherries
    for cherry in cherry_lst:
        pygame.draw.rect(screen,
                         (255, 0, 0),
                         (cherry.position[0], cherry.position[1], block_size, block_size))

    # update display
    pygame.display.update()

def main_loop(snake_list, cherry_list):
    """
    Main loop of the game. This function returns only if snake collision occured.

    """
    while True:
        # capture events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # happens when user tries to close window
                sys.exit()  # exit from game
            elif event.type == pygame.KEYDOWN:
                # happens on key pressed
                # check which snake's key was pressed and add it to key stack
                for snake in snake_list:
                    if event.key in [val for _, val in snake.move_keys.items()]:
                        snake.key_stack.append(event.key)
            elif event.type == pygame.USEREVENT:  # happens on each timer tick

                for snake in snake_list:
                    snake.get_dir_from_keystack()
                    snake.set_new_state(size, snake_list)

                    # check if there is collision
                    if snake.collision:
                        return SnakeGameStatusFlags.COLLISION_OCCURENCE

                    # check if any of the cherries was eaten by the current snake
                    for cherry in cherry_list:
                        if snake.block_pos_lst[0] == cherry.position:
                            # append new block to snake that ate the cherry
                            snake.block_pos_lst.append(snake.block_pos_lst[-1])

                            # set new random position for the eaten cherry
                            cherry.set_new_random_position(snake_lst, size)

                # redraw screen with updated snake and cherry positions
                redraw_screen(snake_list, cherry_list, block_size)


if __name__ == '__main__':
    pygame.init()

    # load configuration data
    with open('config.json', 'r') as config_file:
        configuration_data = json.load(config_file)

    size = width, height = configuration_data["main_window_size"]
    BLACK = 0, 0, 0
    refresh_rate = configuration_data["refresh_rate"]
    start_pos = configuration_data["start_pos"]
    block_size = configuration_data["block_size"]

    # set display
    screen = pygame.display.set_mode(size)

    # set timer
    pygame.time.set_timer(pygame.USEREVENT, refresh_rate)

    timer = pygame.time.get_ticks()

    while True:
        # initialize new game
        snake_lst, cherry_pos = init_game(configuration_data)

        # main loop will exit only if collision occurs
        main_loop(snake_lst, cherry_pos)



