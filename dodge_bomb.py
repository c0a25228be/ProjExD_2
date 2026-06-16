import math
import os
import pygame as pg
import random
import sys
import time


WIDTH, HEIGHT = 1100, 650
DELTA = {
    pg.K_UP:(0,-5),
    pg.K_DOWN:(0,+5),
    pg.K_LEFT:(-5,0),
    pg.K_RIGHT:(+5,0),
}

os.chdir(os.path.dirname(os.path.abspath(__file__)))


def check_bound(rct: pg.Rect) -> tuple[bool, bool]:
    """
    引数：こうかとんRectまたは爆弾Rect
    戻り値：タプル（横方向判定結果、縦方向判定結果）
    画面内ならTrue, 画面外ならFalse
    """
    yoko, tate = True, True
    if rct.left < 0 or WIDTH < rct.right:
        yoko = False
    if rct.top < 0 or HEIGHT < rct.bottom:
        tate = False
    return yoko, tate


def gameover(screen: pg.Surface) -> None:
    """
    ゲームオーバー画面を表示する関数
    引数: screen (描画対象のSurface)
    戻り値: None
    """
    black_out = pg.Surface((WIDTH, HEIGHT))
    black_out.fill((0, 0, 0))
    black_out.set_alpha(128)
    
    font = pg.font.Font(None, 80)
    txt = font.render("Game Over", True, (255, 255, 255))
    txt_rect = txt.get_rect(center=(WIDTH // 2, HEIGHT // 2))
    
    kk_cry_img = pg.image.load("fig/8.png")
    kk_cry_rect1 = kk_cry_img.get_rect(center=(WIDTH // 2 - 200, HEIGHT // 2))
    kk_cry_rect2 = kk_cry_img.get_rect(center=(WIDTH // 2 + 200, HEIGHT // 2))
    
    screen.blit(black_out, [0, 0])
    screen.blit(txt, txt_rect)
    screen.blit(kk_cry_img, kk_cry_rect1)
    screen.blit(kk_cry_img, kk_cry_rect2)
    
    pg.display.update()
    time.sleep(5)


def init_bb_imgs() -> tuple[list[pg.Surface], list[int]]:
    """
    10段階の大きさを変えた爆弾Surfaceのリストと加速度のリストを準備する関数
    引数: None
    戻り値: タプル（爆弾Surfaceのリスト、加速度のリスト）
    """
    bb_imgs = []
    for r in range(1, 11):
        bb_img = pg.Surface((20 * r, 20 * r))
        bb_img.set_colorkey((0, 0, 0))
        pg.draw.circle(bb_img, (255, 0, 0), (10 * r, 10 * r), 10 * r)
        bb_imgs.append(bb_img)
    bb_accs = [a for a in range(1, 11)]
    return bb_imgs, bb_accs


def get_kk_imgs() -> dict[tuple[int, int], pg.Surface]:
    """
    移動量タプルと対応する画像Surfaceの辞書を返す関数
    引数: None
    戻り値: 辞書（キー：移動量のタプル、値：rotozoomした画像Surface）
    """
    base_img = pg.image.load("fig/3.png")
    flip_img = pg.transform.flip(base_img, True, False)
    
    kk_dict = {
        (0, 0): pg.transform.rotozoom(base_img, 0, 0.9),
        (-5, 0): pg.transform.rotozoom(base_img, 0, 0.9),
        (-5, -5): pg.transform.rotozoom(base_img, -45, 0.9),
        (0, -5): pg.transform.rotozoom(flip_img, 90, 0.9),
        (+5, -5): pg.transform.rotozoom(flip_img, 45, 0.9),
        (+5, 0): pg.transform.rotozoom(flip_img, 0, 0.9),
        (+5, +5): pg.transform.rotozoom(flip_img, -45, 0.9),
        (0, +5): pg.transform.rotozoom(flip_img, -90, 0.9),
        (-5, +5): pg.transform.rotozoom(base_img, 45, 0.9),
    }
    return kk_dict


def calc_orientation(org: pg.Rect, dst: pg.Rect, current_xy: tuple[float, float])-> tuple[float, float]:
    """
    爆弾から見て、こうかとんRectがある方向、すなわち移動すべき方向ベクトルを返す関数
    引数: org (爆弾のRect), dst (こうかとんのRect), current_xy (計算前の方向ベクトル)
    戻り値: 正規化された方向ベクトル (vx, vy)
    """
    dx = dst.centerx - org.centerx
    dy = dst.centery - org.centery
    dist = math.hypot(dx, dy)

    if dist < 300:
        return current_xy
    
    if dist != 0:
        vx: float = dx / dist * math.sqrt(50)
        vy: float = dy / dist * math.sqrt(50)
    else:
        vx, vy = current_xy
        
    return vx, vy


def main():
    pg.display.set_caption("逃げろ！こうかとん")
    screen = pg.display.set_mode((WIDTH, HEIGHT))
    
    bg_img = pg.image.load("fig/pg_bg.jpg")    
    kk_img = pg.transform.rotozoom(pg.image.load("fig/3.png"), 0, 0.9)
    kk_imgs = get_kk_imgs()
    kk_img = kk_imgs[(0, 0)]
    kk_rct = kk_img.get_rect()
    kk_rct.center = 300, 200

    clock = pg.time.Clock()
    tmr = 0

    bb_img = pg.Surface((20, 20))
    pg.draw.circle(bb_img, (255, 0, 0), (10, 10), 10)
    bb_img.set_colorkey((0, 0, 0))
    bb_rct = bb_img.get_rect()
    bb_rct.centerx = random.randint(0,WIDTH)
    bb_rct.centery = random.randint(0,HEIGHT)
    vx, vy = +5, +5

    bb_imgs, bb_accs = init_bb_imgs()
    bb_rct = bb_imgs[0].get_rect()
    bb_rct.center = random.randint(0, WIDTH), random.randint(0, HEIGHT)

    clock = pg.time.Clock()
    tmr: int = 0

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:  #×ボタンを押したらゲーム終了
                return
            
        if kk_rct.colliderect(bb_rct):
            gameover(screen)
            print("ゲームオーバー")
            return
        
        screen.blit(bg_img, [0, 0]) 

        key_lst = pg.key.get_pressed()
        sum_mv = [0, 0]
        #if key_lst[pg.K_UP]:
        #    sum_mv[1] -= 5
        #if key_lst[pg.K_DOWN]:
        #    sum_mv[1] += 5
        #if key_lst[pg.K_LEFT]:
        #    sum_mv[0] -= 5
        #if key_lst[pg.K_RIGHT]:
        #    sum_mv[0] += 5
        for key, mv in DELTA.items():
            if key_lst[key]:
                sum_mv[0] += mv[0]  #横方向の移動
                sum_mv[1] += mv[1]  #縦方向の移動
        kk_rct.move_ip(sum_mv)
        if check_bound(kk_rct) != (True, True):
            kk_rct.move_ip(-sum_mv[0], -sum_mv[1])  #更新前のに位置に戻す
        screen.blit(kk_img, kk_rct)

        kk_img = kk_imgs[tuple(sum_mv)]

        vx, vy = calc_orientation(bb_rct, kk_rct, (vx, vy))

        idx = min(tmr // 500, 9)
        avx = vx * bb_accs[idx]
        avy = vy * bb_accs[idx]
        bb_img = bb_imgs[idx]
        
        bb_rct.width = bb_img.get_rect().width
        bb_rct.height = bb_img.get_rect().height

        bb_rct.move_ip(vx, vy)
        yoko, tate = check_bound(bb_rct)
        if not yoko:
            vx *= -1
        if not tate:
            vy *= -1
        screen.blit(bb_img, bb_rct)

        pg.display.update()
        tmr += 1
        clock.tick(50)

if __name__ == "__main__":
    pg.init()
    main()
    pg.quit()
    sys.exit()
