from pico2d import *

import os

import pico2d
import sdl2

# sonic-sprite.png is 399x525 with no uniform grid, so frame rects were
# measured by scanning transparent gaps: (lefts, width, height, bottom)
# `bottom` is the offset from the BOTTOM edge of the sheet (pico2d coordinate).
ACTIONS = {
    'spin': ([0, 35, 69, 104, 138, 173], 35, 27, 292),
    'walk': ([0, 36, 74, 111, 148, 185], 37, 36, 251),
    'run': ([1, 35, 67, 98, 131, 162, 193, 230, 268], 31, 33, 325),
}

SEQUENCE = ['walk', 'run', 'spin']
CYCLES_PER_ACTION = 5
FPS = 12

WIDTH, HEIGHT = 800, 400

open_canvas(WIDTH, HEIGHT)

sheet = load_image('sonic-sprite.png')
font = load_font(os.path.join(os.path.dirname(pico2d.__file__), 'data', 'ConsolaMalgun.ttf'), 20)

frame_time = 1.0 / FPS
state = {'action': 0, 'frame': 0, 'cycles': 0, 'elapsed': 0.0}


def current():
    return SEQUENCE[state['action']]


def advance():
    state['action'] = (state['action'] + 1) % len(SEQUENCE)
    state['frame'] = 0
    state['cycles'] = 0


running = True

while running:
    for event in get_events():
        if event.type == sdl2.SDL_QUIT:
            running = False
        elif event.type == sdl2.SDL_KEYDOWN:
            if event.key == sdl2.SDLK_ESCAPE:
                running = False
            elif event.key == sdl2.SDLK_SPACE:
                advance()

    name = current()
    lefts, fw, fh, bottom = ACTIONS[name]

    state['elapsed'] += 1.0 / 60.0
    while state['elapsed'] >= frame_time:
        state['elapsed'] -= frame_time
        state['frame'] += 1
        if state['frame'] >= len(lefts):
            state['frame'] = 0
            state['cycles'] += 1
            if state['cycles'] >= CYCLES_PER_ACTION:
                advance()
                name = current()
                lefts, fw, fh, bottom = ACTIONS[name]

    clear_canvas()
    sheet.clip_draw(lefts[state['frame']], bottom, fw, fh,
                    (WIDTH - fw) // 2, (HEIGHT - fh) // 2)

    cycle = min(state['cycles'] + 1, CYCLES_PER_ACTION)
    font.draw(150, 370, '%s  frame %d/%d  cycle %d/%d'
              % (name, state['frame'] + 1, len(lefts), cycle, CYCLES_PER_ACTION), (0, 0, 0))
    font.draw(150, 350, 'SPACE: next action    ESC: quit', (0, 0, 0))
    update_canvas()
    delay(1.0 / 60.0)

close_canvas()
