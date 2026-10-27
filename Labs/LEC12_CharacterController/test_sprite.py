from pico2d import *
open_canvas()
img = load_image('animation_sheet.png')
clear_canvas()
img.clip_draw(0, 100, 100, 100, 400, 90)
update_canvas()
delay(3)
close_canvas()
