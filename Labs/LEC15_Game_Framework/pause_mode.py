import game_framework
import play_mode
from pico2d import *

image = None

def init():
    global image

    image = load_image('pause.png')

def finish():
    global image
    del image

def pause():
    pass

def resume():
    pass

def handle_events():
    events = get_events()
    for event in events:
        if event.type == SDL_QUIT:
            game_framework.quit()
            return
        elif event.type == SDL_KEYDOWN and event.key == SDLK_p:
            game_framework.pop_mode()
            return

def update():
    pass

def render():
    clear_canvas()
    play_mode.render_scene()
    image.draw(400, 300)
    update_canvas()
