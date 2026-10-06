"""
방향키로 소년을 움직이는 프로그램 (pico2d) - LEC10_HandlingInputs 과제

조작법
    방향키(또는 WASD) : 상 / 하 / 좌 / 우 이동
    ESC                : 종료

실행법
    python move_boy_with_arrow_keys.py

사용 이미지 (같은 폴더에 있음)
    TUK_GROUND.png    : 배경 (1280x1024, 캔버스 크기와 동일)
    run_animation.png : 달리기 스프라이트 시트 (가로 8칸 x 세로 1줄, 한 프레임 100x100)
"""
import math
import os

import pico2d


# ==========================================================
#  설정값 - 여기만 고치면 됩니다
# ==========================================================
SPRITE_FILE = 'run_animation.png'   # 스프라이트 시트 파일 이름
GROUND_FILE = 'TUK_GROUND.png'      # 배경 이미지 (1280x1024, 없으면 바닥 선으로 대체)
CANVAS_W, CANVAS_H = 1280, 1024    # 화면(캔버스) 크기 - TUK_GROUND.png 크기에 맞춤

SPRITE_COLS = 8                    # 시트에서 가로(왼쪽 -> 오른쪽) 프레임 개수
SPRITE_ROWS = 1                    # 시트에서 세로(위 -> 아래) 프레임 개수
FRAME_W = 100                      # 한 프레임 가로 크기 (0 이면 이미지 폭 / SPRITE_COLS 로 자동 계산)
FRAME_H = 100                      # 한 프레임 세로 크기 (0 이면 이미지 높이 / SPRITE_ROWS 로 자동 계산)

SPEED = 260.0                      # 이동 속도 (픽셀 / 초)
ANIM_FPS = 12.0                    # 달리기 애니메이션 재생 속도 (프레임 / 초)
IDLE_FRAME = 0                     # 멈춰 있을 때 보여줄 프레임 번호
SCALE = 1.0                        # 화면에 그릴 크기 배율 (1.0 = 원본 크기)
MARGIN = 0                         # 화면 가장자리에 남길 여백 (픽셀)

FLOOR_Y = 40                       # 배경 이미지가 없을 때 쓰는 바닥 선 높이
HUD_COLOR = (255, 255, 255)        # 안내 문구 색상


# 방향키 + WASD 를 같이 받습니다
KEY_LEFT = (pico2d.SDLK_LEFT, pico2d.SDLK_a)
KEY_RIGHT = (pico2d.SDLK_RIGHT, pico2d.SDLK_d)
KEY_UP = (pico2d.SDLK_UP, pico2d.SDLK_w)
KEY_DOWN = (pico2d.SDLK_DOWN, pico2d.SDLK_s)


def get_sprite_path():
    """스프라이트 시트의 경로 (프로그램과 같은 폴더)"""
    return os.path.join(os.path.dirname(os.path.abspath(__file__)), SPRITE_FILE)


def png_size(path):
    """PNG 파일의 (너비, 높이) 를 파일 헤더만 읽어서 알아냅니다. (별도 라이브러리 필요 없음)"""
    with open(path, 'rb') as f:
        header = f.read(24)
    if header[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('PNG 파일이 아닙니다: ' + path)
    width = int.from_bytes(header[16:20], 'big')
    height = int.from_bytes(header[20:24], 'big')
    return width, height


def load_hud_font():
    """
    안내 문구를 그릴 폰트. pico2d에 딸려 온 폰트가 없으면 시스템 한글 폰트를 시도합니다.
    모두 실패하면 None (문구 없이 동작)
    """
    pico2d_dir = os.path.dirname(os.path.abspath(pico2d.__file__))
    candidates = [
        os.path.join(pico2d_dir, 'ConsolaMalgun.ttf'),   # pico2d 번들 폰트
        os.path.join(pico2d_dir, 'data', 'ConsolaMalgun.TTF'),  # 구버전 번들 경로
        r'C:\Windows\Fonts\malgun.ttf',                  # 맑은 고딕
        r'C:\Windows\Fonts\malgunbd.ttf',                # 맑은 고딕 Bold
        r'C:\Windows\Fonts\gulim.ttc',                   # 굴림
        r'C:\Windows\Fonts\arial.ttf',                   # 영문 전용 폰트
    ]
    for path in candidates:
        if not os.path.exists(path):
            continue
        try:
            return pico2d.load_font(path, 20)
        except Exception:
            continue
    return None


class Boy:
    """스프라이트 시트에서 한 프레임씩 잘라 그리는 소년 캐릭터"""

    def __init__(self, image, frame_w, frame_h, cols, rows, x, y, scale=SCALE):
        self.image = image          # 스프라이트 시트 전체 이미지
        self.frame_w = frame_w      # 한 프레임 크기
        self.frame_h = frame_h
        self.cols = cols            # 시트 가로 프레임 개수
        self.rows = rows            # 시트 세로 프레임 개수
        self.frame_count = cols * rows

        self.x = x                  # 화면에서의 중심 좌표
        self.y = y
        self.scale = scale
        self.draw_w = frame_w * scale   # 화면에 그릴 실제 크기
        self.draw_h = frame_h * scale

        self.facing_right = True    # 왼쪽으로 갈 때 그림을 좌우 반전해서 그립니다
        self.frame = IDLE_FRAME     # 지금 보여줄 프레임 번호
        self.frame_time = 0.0       # 다음 프레임까지 남은 시간(초)

    def update(self, dx, dy, dt):
        """
        (dx, dy) 방향으로 dt 초 동안 이동합니다.
        dx, dy 는 -1 / 0 / 1 이고, 둘 다 0 이면 멈춰 있는 상태입니다.
        """
        if dx or dy:
            # 대각선으로 움직여도 속도가 같도록 방향 벡터를 정규화합니다
            length = math.hypot(dx, dy)
            self.x += dx / length * SPEED * dt
            self.y += dy / length * SPEED * dt

            if dx < 0:
                self.facing_right = False
            elif dx > 0:
                self.facing_right = True

            # 달리는 애니메이션: ANIM_FPS 만큼의 시간이 지나면 다음 프레임
            self.frame_time += dt
            while self.frame_time >= 1.0 / ANIM_FPS:
                self.frame_time -= 1.0 / ANIM_FPS
                self.frame = (self.frame + 1) % self.frame_count
        else:
            self.frame = IDLE_FRAME
            self.frame_time = 0.0

        # 화면 밖으로 나가지 않도록 위 / 아래 / 좌 / 우 경계 안으로 제한
        half_w = self.draw_w / 2
        half_h = self.draw_h / 2
        self.x = pico2d.clamp(half_w - MARGIN, self.x, CANVAS_W - half_w + MARGIN)
        self.y = pico2d.clamp(half_h - MARGIN, self.y, CANVAS_H - half_h + MARGIN)

    def draw(self):
        """현재 프레임만 잘라서 (self.x, self.y) 를 중심으로 그립니다"""
        col = self.frame % self.cols
        row = self.frame // self.cols

        left = col * self.frame_w
        # pico2d 좌표는 원점이 왼쪽 아래이므로, 잘라낼 영역의 아래쪽 거리로 넘깁니다
        bottom = (self.rows - 1 - row) * self.frame_h
        flip = '' if self.facing_right else 'h'   # 'h' = 좌우 반전

        self.image.clip_composite_draw(left, bottom, self.frame_w, self.frame_h,
                                       0, flip, self.x, self.y,
                                       self.draw_w, self.draw_h)


def draw_scene(boy, font, ground):
    """배경 -> 소년 -> 안내 문구 순서로 그립니다 (pico2d 는 나중에 그린 것이 위에 놓임)"""
    if ground is not None:
        # 배경은 캔버스 중앙에 그리면 크기(1280x1024)와 캔버스(1280x1024)가 같아 1:1 로 채워집니다
        ground.draw(CANVAS_W / 2, CANVAS_H / 2, CANVAS_W, CANVAS_H)
    else:
        pico2d.draw_line(0, FLOOR_Y, CANVAS_W, FLOOR_Y, 130, 130, 140)
    pico2d.draw_rectangle(1, 1, CANVAS_W - 2, CANVAS_H - 2, 150, 150, 160, filled=False)

    boy.draw()

    if font is not None:
        # 배경 위에서 문구가 잘 보이도록 상단에 어두운 띠를 깔고 흰 글씨를 씁니다
        pico2d.draw_rectangle(0, CANVAS_H - 72, CANVAS_W, CANVAS_H,
                              30, 30, 40, 255, filled=True)
        font.draw(12, CANVAS_H - 25, '방향키로 이동   |   ESC 종료', HUD_COLOR)
        facing = '오른쪽' if boy.facing_right else '왼쪽'
        font.draw(12, CANVAS_H - 49,
                  'x=%.0f  y=%.0f  바라보는 방향: %s' % (boy.x, boy.y, facing),
                  HUD_COLOR)


def run_game(boy, font, ground, max_frames=None):
    """
    게임 루프. max_frames 를 주면 그 만큼만 돌고 끝납니다(자동 테스트용).
    """
    running = True
    last_time = pico2d.get_time()
    pressed = set()
    frames = 0

    while running:
        now = pico2d.get_time()
        dt = min(now - last_time, 0.1)   # 창이 멈췄다가 복귀해도 순간이동하지 않게 제한
        last_time = now

        # ---- 입력 처리 ----
        for event in pico2d.get_events():
            if event.type == pico2d.SDL_QUIT:
                running = False
            elif event.type == pico2d.SDL_KEYDOWN:
                if event.key == pico2d.SDLK_ESCAPE:
                    running = False
                else:
                    pressed.add(event.key)
            elif event.type == pico2d.SDL_KEYUP:
                pressed.discard(event.key)

        def is_down(keys):
            return any(key in pressed for key in keys)

        dx = int(is_down(KEY_RIGHT)) - int(is_down(KEY_LEFT))
        dy = int(is_down(KEY_UP)) - int(is_down(KEY_DOWN))

        # ---- 갱신 / 그리기 ----
        boy.update(dx, dy, dt)
        pico2d.clear_canvas()
        draw_scene(boy, font, ground)
        pico2d.update_canvas()

        frames += 1
        if max_frames is not None and frames >= max_frames:
            return


def main():
    sprite_path = get_sprite_path()
    if not os.path.exists(sprite_path):
        print('[error] cannot find %s' % SPRITE_FILE)
        print('        put run_animation.png in the same folder as this file')
        return

    # 스프라이트 시트 크기를 알아내서 한 프레임 크기를 계산합니다
    sheet_w, sheet_h = png_size(sprite_path)
    frame_w = FRAME_W if FRAME_W > 0 else sheet_w // SPRITE_COLS
    frame_h = FRAME_H if FRAME_H > 0 else sheet_h // SPRITE_ROWS

    print('[info] sprite sheet: %s %dx%d' % (SPRITE_FILE, sheet_w, sheet_h))
    print('[info] frames: %dx%d, frame size: %dx%d' % (SPRITE_COLS, SPRITE_ROWS,
                                                       frame_w, frame_h))
    # 프레임 크기를 자동으로 계산한 경우에만 크기 불일치를 경고합니다
    if (FRAME_W == 0 or FRAME_H == 0) and \
            (frame_w * SPRITE_COLS != sheet_w or frame_h * SPRITE_ROWS != sheet_h):
        print('[warn] sheet size does not match SPRITE_COLS x SPRITE_ROWS. '
              'Adjust the values at the top of this file.')
    print('[info] canvas: %dx%d, background: %s' % (CANVAS_W, CANVAS_H, GROUND_FILE))
    print('[info] arrow keys: move / ESC: quit')

    pico2d.open_canvas(CANVAS_W, CANVAS_H, sync=True)
    pico2d.hide_lattice()
    try:
        font = load_hud_font()
        ground = None
        ground_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), GROUND_FILE)
        if os.path.exists(ground_path):
            ground = pico2d.load_image(ground_path)

        boy = Boy(pico2d.load_image(sprite_path), frame_w, frame_h,
                  SPRITE_COLS, SPRITE_ROWS,
                  CANVAS_W / 2, FLOOR_Y + frame_h * SCALE / 2, SCALE)
        run_game(boy, font, ground)
    finally:
        pico2d.close_canvas()


if __name__ == '__main__':
    main()