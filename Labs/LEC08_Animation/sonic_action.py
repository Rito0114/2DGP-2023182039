from pico2d import *

import os

import pico2d
import sdl2

# sonic-sprite.png is 399x525 with no uniform grid, so frame rects were
# measured by scanning transparent gaps. Each frame is (left, bottom, w, h).
# `bottom` is the offset from the BOTTOM edge of the sheet (pico2d coordinate).
WALK = [
    (0, 251, 37, 36),
    (36, 251, 37, 36),
    (74, 251, 37, 36),
    (111, 251, 37, 36),
    (148, 251, 37, 36),
    (185, 251, 37, 36),
]

RUN = [
    (1, 325, 31, 33),
    (35, 325, 31, 33),
    (67, 325, 31, 33),
    (98, 325, 31, 33),
    (131, 325, 31, 33),
    (162, 325, 31, 33),
    (193, 325, 31, 33),
    (230, 325, 31, 33),
    (268, 325, 31, 33),
]

SPIN = [
    (0, 292, 35, 27),
    (35, 292, 35, 27),
    (69, 292, 35, 27),
    (104, 292, 35, 27),
    (138, 292, 35, 27),
    (173, 292, 35, 27),
]

# kick: the leg swings from a low diagonal out to fully horizontal, so the
# shoe (red pixels) grows into a wide bar across frames 3-4.
KICK = [
    (1, 361, 35, 43),
    (39, 361, 35, 43),
    (89, 361, 35, 43),
    (130, 361, 35, 43),
    (181, 361, 35, 43),
    (228, 361, 35, 43),
]

# turn: widths differ per frame (27..33) and frame 0 sits only 3px from frame
# 1, so a uniform width would clip into the neighbour - keep each frame's own
# tight crop. Every frame is centred by its own width, so nothing jitters.
TURN = [
    (1, 108, 27, 40),
    (31, 108, 31, 40),
    (64, 108, 31, 40),
    (99, 108, 33, 40),
    (136, 108, 32, 40),
    (176, 108, 33, 40),
    (217, 108, 33, 40),
    (254, 108, 33, 40),
]

ACTIONS = {
    'walk': WALK,
    'run': RUN,
    'spin': SPIN,
    'kick': KICK,
    'turn': TURN,
    'dash': SPIN,
}

SEQUENCE = ['walk', 'dash', 'kick', 'turn']
CYCLES_PER_ACTION = 5
FPS = 12
SCALE = 6

WIDTH, HEIGHT = 800, 400

# sonic_background.png is 800x400, exactly the canvas size and aspect ratio, so
# at BG_MODE='cover' the scale factor is 1.0 and it draws 1:1 with no crop and
# no resampling blur. The mode still applies in case a different image is loaded:
# 'fit' scales down until the whole image fits inside the canvas, 'cover' scales
# up until it fills the canvas and crops the overflow evenly.
BG_MODE = 'cover'

open_canvas(WIDTH, HEIGHT)

sheet = load_image('sonic-sprite.png')
bg = load_image('sonic_background.png')
font = load_font(os.path.join(os.path.dirname(pico2d.__file__), 'data', 'ConsolaMalgun.ttf'), 20)

BG_SCALE = max(WIDTH / bg.w, HEIGHT / bg.h) if BG_MODE == 'cover' \
    else min(WIDTH / bg.w, HEIGHT / bg.h)
BG_W, BG_H = bg.w * BG_SCALE, bg.h * BG_SCALE

frame_time = 1.0 / FPS
# Pause between actions: once an action finishes its cycles, its last frame is
# held on screen for HOLD_SECONDS before moving on. This is separate from the
# frame timer, so the hold does not eat into the next action's cycle count.
HOLD_SECONDS = 1.0

state = {'action': 0, 'frame': 0, 'cycles': 0, 'elapsed': 0.0, 'hold': 0.0}


def current():
    return SEQUENCE[state['action']]


def advance():
    state['action'] = (state['action'] + 1) % len(SEQUENCE)
    state['frame'] = 0
    state['cycles'] = 0
    state['hold'] = 0.0


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
    frames = ACTIONS[name]

    if state['hold'] > 0.0:
        state['hold'] -= 1.0 / 60.0
        if state['hold'] <= 0.0:
            state['hold'] = 0.0
            advance()
            name = current()
            frames = ACTIONS[name]
    else:
        state['elapsed'] += 1.0 / 60.0
        while state['elapsed'] >= frame_time:
            state['elapsed'] -= frame_time
            state['frame'] += 1
            if state['frame'] >= len(frames):
                state['frame'] = 0
                state['cycles'] += 1
                if state['cycles'] >= CYCLES_PER_ACTION:
                    # Freeze on the last frame for HOLD_SECONDS.
                    state['frame'] = len(frames) - 1
                    state['hold'] = HOLD_SECONDS
                    break

    left, bottom, fw, fh = frames[state['frame']]

    # clip_draw's x, y are the CENTRE of the dest rect (pico2d.py:361), and the
    # w, h args set the dest size, so SCALE just multiplies those. The source
    # rect stays in sheet pixels, so no re-encoded texture is needed. pico2d
    # never calls SDL_SetTextureScaleMode, so SDL2's default nearest-neighbour
    # applies and the 2x stays crisp instead of blurring.
    dw, dh = fw * SCALE, fh * SCALE

    # True centre on both axes: left = cx-dw/2, right = cx+dw/2, and the same
    # for top/bottom, so the sprite is centred regardless of fw/fh.
    cx = WIDTH // 2
    cy = HEIGHT // 2

    clear_canvas()
    # draw() takes the centre too (pico2d.py:340-345), so the background goes
    # through the same centre-based path as the sprite.
    bg.draw(WIDTH // 2, HEIGHT // 2, BG_W, BG_H)
    sheet.clip_draw(left, bottom, fw, fh, cx, cy, dw, dh)

    cycle = min(state['cycles'] + 1, CYCLES_PER_ACTION)
    if state['hold'] > 0.0:
        status = '%s  hold %.1fs' % (name, state['hold'])
    else:
        status = '%s  frame %d/%d  cycle %d/%d' % (
            name, state['frame'] + 1, len(frames), cycle, CYCLES_PER_ACTION)
    font.draw(150, 370, status, (0, 0, 0))
    font.draw(150, 350, 'SPACE: next action    ESC: quit', (0, 0, 0))
    update_canvas()
    delay(1.0 / 60.0)

close_canvas()
