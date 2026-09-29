from pico2d import *

import os

import pico2d
import sdl2

# sonic-sprite.png is 399x525 with no uniform grid, so frame rects were
# measured by scanning transparent gaps: (lefts, width, height, bottom)
# `bottom` is the offset from the BOTTOM edge of the sheet (pico2d coordinate).
ACTIONS = {
    'spin': ([0, 35, 69, 104, 138, 173], 35, 27, 292, 5.0),
    'walk': ([0, 36, 74, 111, 148, 185], 37, 36, 251, 4.0),
    'run': ([1, 35, 67, 98, 131, 162, 193, 230, 268], 31, 33, 325, 8.0),
}

SEQUENCE = ['walk', 'run', 'spin']
FRAMES_PER_ACTION = 12
FPS = 12

open_canvas(800, 400)

sheet = load_image('sonic-sprite.png')
font = load_font(os.path.join(os.path.dirname(pico2d.__file__), 'data', 'ConsolaMalgun.ttf'), 20)

ground = 90
frame_time = 1.0 / FPS

state = {'action': 0, 'frame': 0, 'held': 0, 'x': 80.0, 'dir': 1, 'elapsed': 0.0}


def current():
    return SEQUENCE[state['action']]


def advance():
    state['action'] = (state['action'] + 1) % len(SEQUENCE)
    state['frame'] = 0
    state['held'] = 0


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
    lefts, fw, fh, bottom, speed = ACTIONS[name]

    state['elapsed'] += 1.0 / 60.0
    while state['elapsed'] >= frame_time:
        state['elapsed'] -= frame_time
        state['frame'] = (state['frame'] + 1) % len(lefts)
        state['held'] += 1
        if state['held'] >= FRAMES_PER_ACTION:
            advance()
            name = current()
            lefts, fw, fh, bottom, speed = ACTIONS[name]

    state['x'] += speed * state['dir']
    if state['x'] < 40:
        state['x'] = 40
        state['dir'] = 1
        state['frame'] = 0
    elif state['x'] > 720:
        state['x'] = 720
        state['dir'] = -1
        state['frame'] = 0

    clear_canvas()
    draw_rectangle(0, 0, 799, ground - 4, 40, 120, 60, filled=True)

    sheet.clip_draw(lefts[state['frame']], bottom, fw, fh, int(state['x']), ground)

    font.draw(150, 370, '%s  frame %d/%d' % (name, state['frame'] + 1, len(lefts)), (0, 0, 0))
    font.draw(150, 350, 'SPACE: next action    ESC: quit', (0, 0, 0))
    update_canvas()
    delay(1.0 / 60.0)

close_canvas()
