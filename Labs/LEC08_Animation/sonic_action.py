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
}

ACTION = 'walk'
FPS = 12

open_canvas(800, 400)

sheet = load_image('sonic-sprite.png')
font = load_font(os.path.join(os.path.dirname(pico2d.__file__), 'data', 'ConsolaMalgun.ttf'), 20)

lefts, fw, fh, bottom = ACTIONS[ACTION]
ground = 90

x = 80.0
vx = 4.0
frame = 0
elapsed = 0.0
frame_time = 1.0 / FPS
running = True

while running:
    for event in get_events():
        if event.type == sdl2.SDL_QUIT:
            running = False
        elif event.type == sdl2.SDL_KEYDOWN:
            if event.key == sdl2.SDLK_ESCAPE:
                running = False

    elapsed += 1.0 / 60.0
    while elapsed >= frame_time:
        elapsed -= frame_time
        frame = (frame + 1) % len(lefts)

    x += vx
    if x < 40:
        x = 40
        vx = abs(vx)
        frame = 0
    elif x > 760:
        x = 760
        vx = -abs(vx)
        frame = 0

    clear_canvas()
    draw_rectangle(0, 0, 799, ground - 4, 40, 120, 60, filled=True)

    sheet.clip_draw(lefts[frame], bottom, fw, fh, int(x), ground)

    font.draw(150, 370, '%s  frame %d/%d' % (ACTION, frame + 1, len(lefts)), (0, 0, 0))
    font.draw(150, 350, 'ESC: quit', (0, 0, 0))
    update_canvas()
    delay(1.0 / 60.0)

close_canvas()
