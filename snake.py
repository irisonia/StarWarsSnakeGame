from collections import namedtuple
from dataclasses import dataclass
from enum import Enum, auto
from pygame.locals import *
import pygame.locals
import pygame
import random
import time
import sys
import os


class Color(Enum):
    yellow = (255, 255, 0)
    black = (0, 0, 0)
    red = (255, 0, 0)
    blue = (0, 0, 255)
    gray = (42, 42, 42)


class Move(Enum):
    quit_game = 0
    speed_down = -1
    speed_up = 1
    up = auto()
    down = auto()
    left = auto()
    right = auto()


@dataclass
class Graphics:
    __slots__ = ['orig_frames_per_sec',
                 'frames_per_sec',
                 'window_width',
                 'window_height',
                 'cell_border_sz', 'game_surf']

    def __init__(self):
        self.orig_frames_per_sec = 4
        self.frames_per_sec = self.orig_frames_per_sec
        self.window_width = 1260
        self.window_height = 675
        self.cell_border_sz = 45
        self.game_surf = None
_graphic_globals = Graphics()

_Edible = namedtuple('Edible', ('coords', 'pic'))


def main():
    global _graphic_globals
    pygame.init()

    os.environ['SDL_VIDEO_CENTERED'] = '1'
    pygame.display.set_caption('Star Wars Snake Game')
    pygame.display.set_icon(pygame.image.load('images/s1.gif'))
    _graphic_globals.game_surf = pygame.display.set_mode(
        (_graphic_globals.window_width, _graphic_globals.window_height))
    pygame.event.set_allowed([KEYDOWN, QUIT])

    greeting()
    while True:
        score = game()
        goodbye(score)
        _graphic_globals.frames_per_sec = _graphic_globals.orig_frames_per_sec


def greeting():
    idx = iter(range(9))
    roller([
            RollerLine('Gather The Jedi, Avoid The Sith!', next(idx)),
            RollerLine('', next(idx)),
            RollerLine('Move With Arrows Or A, W, D, X.', next(idx)),
            RollerLine('Adjust Speed With - +', next(idx)),
            RollerLine('The Sith Cuts The Snake.', next(idx)),
            RollerLine('', next(idx)),
            RollerLine('May The Force Be With You...', next(idx)),
            RollerLine('', next(idx)),
            RollerLine("Press Any Key To Start", next(idx))
           ]
          )


def goodbye(score):
    strs = ["You Are Still A Padawan, You Will Improve Soon!",
            "Good Game!",
            "Well Done!",
            "You Seem To Be Force Sensitive...",
            "Wow!! The Force Is Very Strong With You!"]
    score_str = (score > 9) + (score > 49) + (score > 299) + (score > 999)
    idx = iter(range(5))
    roller([
            RollerLine(f'{strs[score_str]}', next(idx)),
            RollerLine('', next(idx)),
            RollerLine(f'You earned {score} point{"" if score == 1 else "s"}'
                       f'{"." if score < 300 else "!"}', next(idx)),
            RollerLine('', next(idx)),
            RollerLine("Press Any Key...", next(idx))
           ]
          )


@dataclass
class RollerLine:
    __slots__ = ['txt', 'font', 'surf', 'rect']

    def __init__(self, txt, line_idx):
        self.txt = txt
        self.font = pygame.font.Font('fonts/verdana.ttf',
                                     24 if line_idx != 0 else 28)
        self.surf = self.font.render(self.txt, True, Color.yellow.value)
        self.rect = self.surf.get_rect()
        self.init_rect(line_idx)

    def init_rect(self, line_idx):
        global _graphic_globals
        self.rect.center = (_graphic_globals.window_width / 2,
                            _graphic_globals.window_height
                              - (self.rect.height * -(line_idx + 1)))


def roller(lines):
    global _graphic_globals

    next_move = get_next_event()
    while next_move is None:
        _graphic_globals.game_surf.fill(Color.black.value)
        if lines[-1].rect.bottom <= 0:
            for i in range(len(lines)):
                lines[i].init_rect(i)
        for line in lines:
            _graphic_globals.game_surf.blit(line.surf, line.rect)
            line.rect.center = (line.rect.centerx, line.rect.centery - 1)
        pygame.display.update()
        time.sleep(.008)
        next_move = get_next_event()
    if next_move == Move.quit_game:
        terminate()


def game():
    global _graphic_globals

    x, y = get_rand_coords(None)
    x = min(x, _graphic_globals.window_width
               - (5 * _graphic_globals.cell_border_sz))
    snake = [(x, y),
             (x - _graphic_globals.cell_border_sz, y),
             (x - (2 * _graphic_globals.cell_border_sz), y)]

    jedi_pics, sith_pics = get_pics()
    jedi, sith = get_edibles(snake, None, None, jedi_pics, sith_pics)

    score = 0
    cur_direction = Move.right
    clock = pygame.time.Clock()
    while True:
        move = get_next_event(cur_direction)

        if move == Move.quit_game:
            terminate()
        if not is_snake_legal(snake):
            return score

        if move in(Move.speed_up, Move.speed_down):
            _graphic_globals.frames_per_sec += move.value
            _graphic_globals.frames_per_sec = (
                max(1, _graphic_globals.frames_per_sec))
        elif move is not None:
            cur_direction = move

        new_head = calc_new_head_coords(snake, cur_direction)
        snake = [new_head] + snake
        if new_head == jedi.coords:
            score += 1
            jedi, sith = get_edibles(snake, jedi, sith, jedi_pics, sith_pics)
        elif sith and (new_head == sith.coords):
            del snake[max(2, (len(snake) - 1) // 3):]
            sith = None
        else:
            snake.pop()

        redraw(snake, jedi, sith, score)
        clock.tick(_graphic_globals.frames_per_sec)


def get_pics():
    def pics(c, n):
        return list(map(make_pic, map(lambda i: c + str(i + 1), range(n))))
    def make_pic(x):
        return pygame.transform.scale(
            pygame.image.load('/'.join(['images', '.'.join([x, 'gif'])])),
            (_graphic_globals.cell_border_sz - 2,
             _graphic_globals.cell_border_sz - 2
            )
        )
    return (pics('j', 5), pics('s', 5))


def get_edibles(snake, jedi, sith, jedi_pics, sith_pics):
    global _graphic_globals

    new_jedi = _Edible(get_rand_coords(snake), random.choice(jedi_pics))

    create_new_sith = ((not sith) and random.choice((True, False)))
    new_sith = _Edible(None,
                       random.choice(sith_pics)) if create_new_sith else sith
    if create_new_sith or (sith and random.choice(range(5))):
        new_sith = _Edible(get_rand_coords(snake), new_sith.pic)
        while new_sith.coords == new_jedi.coords:
            new_sith = _Edible(get_rand_coords(snake), new_sith.pic)

    return (new_jedi, new_sith)


def get_rand_coords(snake):
    global _graphic_globals

    def rand_coords():
        return (random.randrange(get_rand_coords.cells_in_window_width)
                                 * _graphic_globals.cell_border_sz,
                random.randrange(get_rand_coords.cells_in_window_height)
                                 * _graphic_globals.cell_border_sz)
    coords = rand_coords()
    if snake:
        while coords in snake:
            coords = rand_coords()
    return coords
get_rand_coords.cells_in_window_width = \
    _graphic_globals.window_width // _graphic_globals.cell_border_sz
get_rand_coords.cells_in_window_height = \
    _graphic_globals.window_height // _graphic_globals.cell_border_sz


def get_next_event(direction = None):
    global _graphic_globals

    for event in pygame.event.get():
        if event is not pygame.NOEVENT:
            if event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    return Move.quit_game
                if not direction:
                    return event
                if (Move.left != direction != Move.right):
                    if event.key in (K_LEFT, K_a):
                        return Move.left
                    if event.key in (K_RIGHT, K_d):
                        return Move.right
                if (Move.up != direction != Move.down):
                    if event.key in (K_UP, K_w):
                        return Move.up
                    if event.key in (K_DOWN, K_x):
                        return Move.down
                if event.key == K_EQUALS:
                    return Move.speed_up
                if event.key == K_MINUS:
                    return Move.speed_down
            if event.type == QUIT:
                return Move.quit_game
    return None


def is_snake_legal(snake):
    global _graphic_globals

    head = snake[0]
    return ((head[0] >= 0) and (head[0] < _graphic_globals.window_width) and
            (head[1] >= 0) and (head[1] < _graphic_globals.window_height) and
            head not in snake[1:])


def calc_new_head_coords(snake, direction):
    newx, newy = snake[0][0], snake[0][1]
    if direction == Move.up:
        newy -= _graphic_globals.cell_border_sz
    elif direction == Move.down:
        newy += _graphic_globals.cell_border_sz
    elif direction == Move.left:
        newx -= _graphic_globals.cell_border_sz
    elif direction == Move.right:
        newx += _graphic_globals.cell_border_sz

    return (newx, newy)


def redraw(snake, jedi, sith, score):
    global _graphic_globals

    _graphic_globals.game_surf.fill(Color.black.value)
    draw_grid()
    draw_edibles(jedi, sith)
    draw_snake(snake)
    draw_score(score)
    pygame.display.update()


def draw_score(score):
    global _graphic_globals

    font = pygame.font.Font('fonts/verdana.ttf', 24)
    score_surf = font.render('Score: %s' % (score), True, Color.blue.value)
    score_rect = score_surf.get_rect()
    _graphic_globals.game_surf.blit(score_surf, score_rect)


def draw_snake(snake):
    global _graphic_globals

    def draw_cell(i):
        draw_snake.cell_frame.topleft = snake[i]
        pygame.draw.rect(_graphic_globals.game_surf,
                         Color.blue.value,
                         draw_snake.cell_frame)

    draw_cell(0)
    for i in range(1, len(snake)):
        draw_cell(i)
        draw_snake.inner_cell.topleft = (snake[i][0] + 1, snake[i][1] + 1)
        pygame.draw.rect(_graphic_globals.game_surf,
                         Color.black.value,
                         draw_snake.inner_cell)
draw_snake.cell_frame = pygame.Rect(0,
                                    0,
                                    _graphic_globals.cell_border_sz,
                                    _graphic_globals.cell_border_sz)
draw_snake.inner_cell = pygame.Rect(0,
                                    0,
                                    _graphic_globals.cell_border_sz - 2,
                                    _graphic_globals.cell_border_sz - 2)


def draw_edibles(jedi, sith):
    global _graphic_globals

    draw_edibles.jedi_frame.topleft = jedi.coords
    pygame.draw.rect(_graphic_globals.game_surf,
                     Color.blue.value,
                     draw_edibles.jedi_frame)
    _graphic_globals.game_surf.blit(jedi.pic,
                                    (jedi.coords[0] + 1, jedi.coords[1] + 1))
    if sith:
        draw_edibles.sith_frame.topleft = sith.coords
        pygame.draw.rect(_graphic_globals.game_surf,
                         Color.red.value,
                         draw_edibles.sith_frame)
        _graphic_globals.game_surf.blit(sith.pic,
                                        (sith.coords[0] + 1,
                                         sith.coords[1] + 1))
draw_edibles.jedi_frame = pygame.Rect(0,
                                      0,
                                      _graphic_globals.cell_border_sz,
                                      _graphic_globals.cell_border_sz)
draw_edibles.sith_frame = pygame.Rect(0,
                                      0,
                                      _graphic_globals.cell_border_sz,
                                      _graphic_globals.cell_border_sz)


def draw_grid():
    global _graphic_globals

    for x in range(0,
                   _graphic_globals.window_width,
                   _graphic_globals.cell_border_sz):
        pygame.draw.line(_graphic_globals.game_surf,
                         Color.gray.value,
                         (x, 0),
                         (x, _graphic_globals.window_height))
    for y in range(0,
                   _graphic_globals.window_height,
                   _graphic_globals.cell_border_sz):
        pygame.draw.line(_graphic_globals.game_surf,
                         Color.gray.value,
                         (0, y),
                         (_graphic_globals.window_width, y))


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
