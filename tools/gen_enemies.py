# -*- coding: utf-8 -*-
"""敵の立ち絵（64x64 ドット絵）の生成スクリプト。
既存の敵スプライト（skeleton/wraith/ghoul/mummy/panther など）に合わせた規格：
  - 64x64 RGBA / アンチエイリアス無し / フラット塗り＋1〜2階調の陰影 / 5〜10色程度
  - 黒縁は付けない（形のコントラストで見せる。ゲーム側が drawEnemyOutlines で輪郭を重ねる）
  - まん丸の体＋小さな足。ETYPE の col / dark を基調にする
使い方: python3 tools/gen_enemies.py [敵id ...]   （省略時は全部）
"""
import os, sys
from PIL import Image, ImageDraw

S = 64
TR = (0, 0, 0, 0)

def new(): return Image.new('RGBA', (S, S), TR)
def D(im): return ImageDraw.Draw(im)
def ell(im, b, c):  D(im).ellipse(b, fill=c)
def rect(im, b, c): D(im).rectangle(b, fill=c)
def poly(im, p, c): D(im).polygon(p, fill=c)
def line(im, p, c, w=1): D(im).line(p, fill=c, width=w)
def px(im, x, y, c):
    if 0 <= x < S and 0 <= y < S: im.putpixel((x, y), c)

def hexc(h, a=255):
    h = h.lstrip('#'); return (int(h[0:2],16), int(h[2:4],16), int(h[4:6],16), a)
def mix(c, t, f): return tuple(int(c[i]+(t[i]-c[i])*f) for i in range(3))+(255,)
def lighten(c, f=0.3): return mix(c, (255,255,255,255), f)
def darken(c, f=0.3):  return mix(c, (8,6,16,255), f)

def feet(im, c, y=52, dx=10, w=12, h=8):
    for s in (-1, 1):
        ell(im, (S//2+s*dx-w//2, y, S//2+s*dx+w//2, y+h), c)

def hood(im, col, top=10, bot=48, left=10, right=54):
    """フードを被った上半身（頭巾のシルエット）。"""
    ell(im, (left, top, right, bot), col)
    poly(im, [(left+4, top+14), ((left+right)//2, top-6), (right-4, top+14)], col)

def glow_eyes(im, col, cx=32, cy=34, dx=6, w=4, h=5):
    for s in (-1, 1):
        x = cx + s*dx
        ell(im, (x-w//2, cy-h//2, x+w//2, cy+h//2), col)
        px(im, x, cy-1, lighten(col, 0.55))

# ---- 敵 --------------------------------------------------------------------

def e_lich():
    """リッチ：紫のローブに浮かぶ髑髏。金の冠と杖。周囲を強化する術者。"""
    im = new()
    ROBE = hexc('#6a4a92'); ROBE_L = lighten(ROBE, 0.22); ROBE_D = darken(ROBE, 0.30)
    BONE = hexc('#e6dfc8'); GLOW = hexc('#b9f2ff'); GOLD = hexc('#e8c04a')
    # 裾（浮いているので足は無く、ぼろぼろに広がる）
    poly(im, [(14, 40), (50, 40), (54, 58), (46, 52), (40, 60), (32, 52), (24, 60), (18, 52), (10, 58)], ROBE)
    poly(im, [(18, 42), (46, 42), (48, 52), (40, 48), (32, 54), (24, 48), (16, 52)], ROBE_D)
    # 肩・胴
    ell(im, (12, 30, 52, 50), ROBE)
    ell(im, (16, 31, 42, 42), ROBE_L)
    # フード
    ell(im, (13, 12, 51, 42), ROBE)
    poly(im, [(16, 24), (32, 4), (48, 24)], ROBE)
    ell(im, (16, 14, 40, 30), ROBE_L)
    # 髑髏
    ell(im, (20, 22, 44, 44), BONE)
    ell(im, (23, 40, 41, 48), BONE)
    for x in range(25, 40, 3): line(im, [(x, 42), (x, 47)], darken(BONE, 0.42))
    line(im, [(23, 42), (41, 42)], darken(BONE, 0.42))
    ell(im, (23, 28, 30, 36), (26, 18, 34, 255))
    ell(im, (34, 28, 41, 36), (26, 18, 34, 255))
    glow_eyes(im, GLOW, cy=32, dx=6, w=5, h=5)
    poly(im, [(31, 36), (33, 36), (32, 39)], (26, 18, 34, 255))
    # 冠
    poly(im, [(19, 20), (19, 12), (24, 17), (28, 9), (32, 17), (36, 9), (40, 17), (45, 12), (45, 20)], GOLD)
    rect(im, (19, 19, 45, 22), darken(GOLD, 0.25))
    px(im, 28, 13, lighten(GOLD, 0.5)); px(im, 36, 13, lighten(GOLD, 0.5))
    # 杖
    line(im, [(56, 58), (56, 22)], hexc('#c9c2a8'), 3)
    line(im, [(55, 56), (55, 24)], lighten(hexc('#c9c2a8'), 0.30))
    ell(im, (51, 12, 61, 22), GLOW)
    ell(im, (53, 14, 59, 20), lighten(GLOW, 0.5))
    return im

def e_necro():
    """ネクロマンサー：闇のフードの術者。骸骨を呼ぶ。顔は影＋緑の眼。"""
    im = new()
    ROBE = hexc('#5a3f80'); ROBE_L = lighten(ROBE, 0.20); ROBE_D = darken(ROBE, 0.34)
    SHADOW = (22, 14, 32, 255); GLOW = hexc('#8ef07a'); BONE = hexc('#ddd6bc')
    feet(im, ROBE_D, y=52, dx=9, w=11, h=8)
    ell(im, (12, 28, 52, 56), ROBE)
    poly(im, [(14, 44), (50, 44), (52, 58), (12, 58)], ROBE)
    for x in (20, 28, 36, 44): line(im, [(x, 46), (x-1, 58)], ROBE_D)
    hood(im, ROBE, top=10, bot=44, left=11, right=53)
    ell(im, (15, 12, 41, 30), ROBE_L)
    # 顔の影
    ell(im, (20, 24, 44, 44), SHADOW)
    glow_eyes(im, GLOW, cy=33, dx=6, w=5, h=6)
    # 掲げた骸骨
    ell(im, (48, 30, 62, 44), BONE)
    ell(im, (50, 41, 60, 47), BONE)
    ell(im, (51, 33, 55, 38), SHADOW); ell(im, (56, 33, 60, 38), SHADOW)
    for x in range(51, 60, 3): line(im, [(x, 42), (x, 46)], darken(BONE, 0.40))
    # 骨の手
    poly(im, [(44, 40), (50, 38), (50, 44), (44, 46)], BONE)
    return im

def e_dullahan():
    """デュラハン：首無しの騎士。切断面が赤く光り、自分の兜を脇に抱える。"""
    im = new()
    ARM = hexc('#5d6f80'); ARM_L = lighten(ARM, 0.28); ARM_D = darken(ARM, 0.36)
    CAPE = hexc('#7a2030'); CAPE_D = darken(CAPE, 0.30); RED = hexc('#ff4a42')
    DARK = (16, 20, 28, 255); GOLD = hexc('#c8a038')
    # マント（背後に広がる）
    poly(im, [(12, 22), (52, 22), (60, 54), (48, 50), (40, 58), (32, 50), (24, 58), (16, 50), (4, 54)], CAPE)
    poly(im, [(16, 26), (48, 26), (54, 48), (44, 46), (36, 52), (28, 46), (20, 48), (10, 48)], CAPE_D)
    feet(im, ARM_D, y=52, dx=10, w=12, h=8)
    # 胴（角ばった鎧）
    poly(im, [(18, 16), (46, 16), (52, 30), (50, 52), (14, 52), (12, 30)], ARM)
    poly(im, [(21, 18), (38, 18), (40, 30), (18, 30)], ARM_L)
    rect(im, (14, 34, 50, 37), ARM_D)
    rect(im, (14, 43, 50, 46), ARM_D)
    poly(im, [(30, 30), (34, 30), (35, 52), (29, 52)], ARM_L)      # 胸の合わせ
    # 肩当て（角のある台形。丸くしない＝耳に見えないように）
    poly(im, [(4, 26), (18, 18), (22, 28), (16, 38), (4, 36)], ARM_L)
    poly(im, [(60, 26), (46, 18), (42, 28), (48, 38), (60, 36)], ARM_L)
    poly(im, [(7, 28), (17, 22), (19, 28), (14, 34), (7, 33)], ARM)
    poly(im, [(57, 28), (47, 22), (45, 28), (50, 34), (57, 33)], ARM)
    # 首の切断面（赤く光る）
    poly(im, [(24, 10), (40, 10), (42, 18), (22, 18)], DARK)
    poly(im, [(26, 11), (38, 11), (39, 16), (25, 16)], RED)
    ell(im, (28, 11, 36, 15), lighten(RED, 0.45))
    for x, y in [(24, 6), (32, 3), (40, 6), (28, 8), (36, 8)]:
        px(im, x, y, RED); px(im, x, y-1, lighten(RED, 0.35))
    # 抱えた兜（右脇。腕で支える）
    poly(im, [(44, 40), (58, 38), (62, 48), (58, 56), (46, 56), (42, 48)], ARM_L)
    poly(im, [(46, 41), (56, 40), (58, 46), (46, 46)], ARM)
    rect(im, (45, 46, 60, 50), DARK)
    rect(im, (47, 47, 51, 49), RED); rect(im, (54, 47, 58, 49), RED)
    poly(im, [(49, 38), (52, 31), (55, 38)], GOLD)
    poly(im, [(38, 44), (46, 42), (46, 50), (38, 50)], ARM)        # 抱える腕
    return im

def e_boomer():
    """ブーマー：膨れた腐乱死体。緑に光る裂け目。倒すと毒の沼を撒く。"""
    im = new()
    BODY = hexc('#8a9a5a'); BODY_L = lighten(BODY, 0.24); BODY_D = darken(BODY, 0.32)
    GAS = hexc('#c8f06a'); DARK = (28, 34, 18, 255); PUS = hexc('#6a8030')
    feet(im, BODY_D, y=52, dx=11, w=13, h=8)
    # 膨れた胴
    ell(im, (8, 14, 56, 56), BODY)
    ell(im, (13, 16, 41, 34), BODY_L)
    ell(im, (14, 40, 50, 55), BODY_D)
    # 裂け目（緑に光る）
    for pts in ([(18, 30), (24, 34), (20, 40), (26, 44)],
                [(44, 26), (39, 32), (45, 36), (40, 42)],
                [(30, 46), (34, 50), (30, 54)]):
        line(im, pts, GAS, 2)
        line(im, [(pts[0][0], pts[0][1]-1), (pts[1][0], pts[1][1]-1)], lighten(GAS, 0.4))
    # 顔
    ell(im, (20, 22, 29, 32), DARK); ell(im, (35, 22, 44, 32), DARK)
    ell(im, (22, 24, 27, 29), GAS); ell(im, (37, 24, 42, 29), GAS)
    px(im, 23, 25, (255, 255, 255, 255)); px(im, 38, 25, (255, 255, 255, 255))
    poly(im, [(26, 36), (38, 36), (36, 42), (28, 42)], DARK)
    for x in (28, 31, 34): line(im, [(x, 36), (x, 41)], PUS)
    # 漏れ出すガス
    for cx, cy, r in [(12, 12, 4), (52, 14, 3), (56, 30, 3), (8, 34, 3)]:
        ell(im, (cx-r, cy-r, cx+r, cy+r), (GAS[0], GAS[1], GAS[2], 150))
    return im

def e_gargoyle():
    """ガーゴイル：石像の魔物。大きな翼と後ろへ反った角、琥珀の眼。硬い。"""
    im = new()
    ST = hexc('#8a90a0'); ST_L = lighten(ST, 0.26); ST_D = darken(ST, 0.36)
    WING = darken(ST, 0.22); WING_D = darken(ST, 0.44)
    EYE = hexc('#ffb44a'); DARK = (24, 26, 38, 255)
    # 翼（体の後ろから左右に広く。指の膜3枚）
    for s2 in (-1, 1):
        base = 32 + s2*10
        tipx = 32 + s2*32
        poly(im, [(base, 20), (tipx, 8), (tipx, 20), (base + s2*4, 30)], WING)
        poly(im, [(base, 24), (tipx, 20), (tipx - s2*2, 32), (base + s2*4, 34)], WING)
        poly(im, [(base, 28), (tipx - s2*4, 32), (tipx - s2*8, 42), (base + s2*3, 38)], WING_D)
        line(im, [(base, 22), (tipx, 12)], ST_L)
        line(im, [(base, 25), (tipx - s2*1, 24)], ST_L)
        line(im, [(base, 28), (tipx - s2*5, 34)], ST_D)
    feet(im, ST_D, y=52, dx=10, w=13, h=8)
    # 胴（うずくまった石像）
    ell(im, (15, 22, 49, 54), ST)
    ell(im, (19, 24, 39, 38), ST_L)
    ell(im, (20, 42, 44, 53), ST_D)
    # 前で組んだ腕
    poly(im, [(18, 42), (30, 40), (32, 46), (18, 48)], ST_L)
    poly(im, [(46, 42), (34, 40), (32, 46), (46, 48)], ST)
    # 角（後ろへ反る）
    poly(im, [(18, 24), (8, 12), (13, 11), (23, 20)], ST_L)
    poly(im, [(46, 24), (56, 12), (51, 11), (41, 20)], ST_L)
    # 耳
    poly(im, [(20, 22), (16, 16), (24, 19)], ST_D)
    poly(im, [(44, 22), (48, 16), (40, 19)], ST_D)
    # 顔
    ell(im, (20, 26, 29, 35), DARK); ell(im, (35, 26, 44, 35), DARK)
    ell(im, (22, 28, 27, 33), EYE); ell(im, (37, 28, 42, 33), EYE)
    px(im, 23, 29, (255, 246, 220, 255)); px(im, 38, 29, (255, 246, 220, 255))
    poly(im, [(25, 37), (39, 37), (36, 43), (28, 43)], DARK)
    for x in (27, 31, 35): poly(im, [(x, 37), (x+2, 37), (x+1, 41)], (232, 228, 216, 255))
    # 石のひび
    line(im, [(23, 45), (27, 50)], ST_D); line(im, [(42, 30), (45, 36)], ST_D)
    line(im, [(33, 22), (36, 26)], ST_D)
    return im

def e_sarcher():
    """スケルトンアーチャー：既存スケルトンと同系の髑髏＋弓。"""
    im = new()
    BONE = hexc('#ded6b8'); BONE_D = darken(BONE, 0.32); CLOTH = hexc('#4a4030')
    DARK = (34, 30, 22, 255); WOOD = hexc('#8a5a30')
    feet(im, (46, 40, 34, 255), y=50, dx=9, w=12, h=8)
    # 頭蓋（大きめ）＋あご
    ell(im, (14, 12, 50, 46), BONE)
    ell(im, (18, 14, 40, 30), lighten(BONE, 0.22))
    ell(im, (20, 40, 44, 50), BONE)
    for x in range(23, 42, 3): line(im, [(x, 43), (x, 49)], BONE_D)
    line(im, [(20, 43), (44, 43)], BONE_D)
    # 眼窩
    ell(im, (19, 22, 29, 34), DARK); ell(im, (35, 22, 45, 34), DARK)
    px(im, 23, 27, hexc('#ff6a4a')); px(im, 24, 27, hexc('#ff6a4a'))
    px(im, 39, 27, hexc('#ff6a4a')); px(im, 40, 27, hexc('#ff6a4a'))
    poly(im, [(30, 34), (34, 34), (32, 39)], DARK)
    # 頭巾（射手のフード）
    poly(im, [(12, 26), (16, 12), (32, 6), (48, 12), (52, 26), (44, 20), (32, 16), (20, 20)], CLOTH)
    poly(im, [(16, 22), (22, 12), (32, 9), (26, 16), (20, 22)], lighten(CLOTH, 0.22))
    # 弓（体の右側）
    for t in range(0, 33):
        y = 16 + t
        dx = int(10 - (t - 16) * (t - 16) * 0.035)
        px(im, 46 + dx, y, WOOD); px(im, 47 + dx, y, lighten(WOOD, 0.25))
    line(im, [(48, 16), (48, 48)], (232, 226, 206, 255))
    # 矢
    line(im, [(40, 32), (58, 32)], (196, 190, 170, 255))
    poly(im, [(58, 30), (63, 32), (58, 34)], (210, 210, 216, 255))
    return im

ENEMIES = {'lich': e_lich, 'necro': e_necro, 'dullahan': e_dullahan,
           'boomer': e_boomer, 'gargoyle': e_gargoyle, 'sarcher': e_sarcher}

def main():
    ids = sys.argv[1:] or list(ENEMIES.keys())
    os.makedirs('assets', exist_ok=True)
    for i in ids:
        if i not in ENEMIES: print('unknown:', i); continue
        im = ENEMIES[i]()
        im.save('assets/%s.png' % i)
        cols = len({im.getpixel((x, y)) for y in range(S) for x in range(S) if im.getpixel((x, y))[3]})
        print('assets/%s.png' % i, im.size, '色数:', cols)

if __name__ == '__main__':
    main()
