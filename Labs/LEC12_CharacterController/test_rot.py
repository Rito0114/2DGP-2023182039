from pico2d import *
open_canvas()
img = load_image('animation_sheet.png')
clear_canvas()
img.clip_composite_draw(0, 0, 100, 100, 3.14159 / 2, '', 400, 70, 100, 100)
update_canvas()
delay(3)
close_canvas()
