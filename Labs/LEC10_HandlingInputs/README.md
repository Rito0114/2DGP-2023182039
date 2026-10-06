# LEC10_HandlingInputs - 방향키로 소년 움직이기

`run_animation.png` 스프라이트 시트를 이용해 방향키로 소년을 위/아래/왼쪽/오른쪽으로 움직이는 프로그램입니다.

## 실행

프로젝트 폴더(`Labs/LEC10_HandlingInputs/`)에서:

```bash
python move_boy_with_arrow_keys.py
```

## 조작법

| 키 | 동작 |
| --- | --- |
| ↑ / ↓ / ← / → | 위 / 아래 / 왼쪽 / 오른쪽 이동 (WASD 도 가능) |
| ESC | 종료 |

## 동작 설명

- 달리는 동안 스프라이트 시트의 프레임(가로 8칸 × 세로 1줄, 한 프레임 100×100)을 순서대로 재생합니다.
- 멈추면 멈춤 프레임으로 돌아오고, 왼쪽으로 이동할 때는 그림을 좌우 반전해서 그립니다.
- 화면 밖으로 나가지 않도록 경계 안으로 제한하며, 화면 상단에 현재 좌표와 바라보는 방향을 표시합니다.

## 설정

`move_boy_with_arrow_keys.py` 맨 위의 설정값(속도 `SPEED`, 애니메이션 속도 `ANIM_FPS`, 프레임 구성 `SPRITE_COLS`/`SPRITE_ROWS`/`FRAME_W`/`FRAME_H`, 크기 배율 `SCALE` 등)을 바꿔서 응용할 수 있습니다.