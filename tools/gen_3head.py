# -*- coding: utf-8 -*-
"""【試作】3頭身の立ち絵（64x64）。既存のチビ体型（頭≒体、1.5頭身）とは別方針。
   頭 y=3〜23（約20px）／胴 y=23〜41／脚 y=41〜61 の3分割を基本の骨格にする。
   使い方: python3 tools/gen_3head.py [id ...]
"""
import os, sys
from PIL import Image, ImageDraw

S = 64
OUT = (20, 18, 28, 255)
TR  = (0, 0, 0, 0)

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
def lighten(c, f=0.28): return mix(c, (255,255,255,255), f)
def darken(c, f=0.30):  return mix(c, (10,8,18,255), f)

def outline(im, col=OUT):
    p = im.load(); add = []
    for y in range(S):
        for x in range(S):
            if p[x, y][3]: continue
            for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
                nx, ny = x+dx, y+dy
                if 0 <= nx < S and 0 <= ny < S and p[nx, ny][3] and p[nx, ny] != col:
                    add.append((x, y)); break
    for x, y in add: p[x, y] = col

# ---- 3頭身の共通パーツ ------------------------------------------------------
# 頭 20px / 胴 18px / 脚 20px。肩幅は頭幅よりわずかに広い程度にして頭の大きさを活かす。

def legs(im, col, boot=None, y0=41, y1=60, w=6, gap=3):
    """左右の脚。boot を渡すと足先を別色にする。"""
    cx = S//2
    for s in (-1, 1):
        x = cx + s*gap - (w//2 if s < 0 else -0)
        x0 = cx + (s*gap) - w//2
        rect(im, (x0, y0, x0+w-1, y1-3), col)
        rect(im, (x0-1, y1-3, x0+w, y1), boot or darken(col, 0.30))

def torso(im, col, top=22, bot=43, w=18):
    cx = S//2
    poly(im, [(cx-w//2, top), (cx+w//2, top), (cx+w//2+1, bot), (cx-w//2-1, bot)], col)

def arm(im, col, side, pts, w=4):
    line(im, pts, col, w)

def head(im, col, cy=13, rw=9, rh=10):
    cx = S//2
    ell(im, (cx-rw, cy-rh, cx+rw, cy+rh), col)

def eyes(im, col=(24,20,32,255), y=14, dx=4, w=2, h=3, white=None):
    cx = S//2
    for s in (-1, 1):
        x = cx + s*dx - w//2
        if white: rect(im, (x-1, y-1, x+w, y+h), white)
        rect(im, (x, y, x+w-1, y+h-1), col)

# ---- キャラ ----------------------------------------------------------------

def c3_knight():
    """騎士（3頭身）：全身鎧＋大剣＋マント。"""
    im = new()
    ST = hexc('#b9c2d4'); ST_L = lighten(ST, 0.30); ST_D = darken(ST, 0.34)
    CAPE = hexc('#7a2f52'); DARK = (26, 26, 38, 255); GOLD = hexc('#e0b552')
    # マント
    poly(im, [(20, 24), (44, 24), (50, 52), (40, 48), (32, 54), (24, 48), (14, 52)], CAPE)
    poly(im, [(24, 26), (40, 26), (44, 46), (36, 44), (32, 48), (28, 44), (20, 46)], darken(CAPE, 0.26))
    # 脚
    legs(im, ST, boot=ST_D, y0=42, y1=60, w=7, gap=4)
    rect(im, (24, 46, 40, 49), ST_D)                     # 腰当て
    # 胴
    torso(im, ST, top=23, bot=45, w=19)
    poly(im, [(23, 24), (32, 24), (32, 42), (24, 42)], ST_L)
    rect(im, (23, 33, 41, 35), GOLD)
    # 肩当て
    ell(im, (14, 22, 26, 32), ST_L); ell(im, (38, 22, 50, 32), ST_L)
    ell(im, (16, 23, 25, 31), ST);   ell(im, (39, 23, 48, 31), ST)
    # 腕
    arm(im, ST, -1, [(20, 30), (16, 40)], 4)
    arm(im, ST,  1, [(44, 30), (48, 38)], 4)
    # 兜
    head(im, ST, cy=13, rw=9, rh=10)
    ell(im, (23, 4, 41, 18), ST_L)
    rect(im, (23, 12, 41, 22), ST)
    rect(im, (25, 12, 39, 16), DARK)                     # 覗き窓
    rect(im, (27, 13, 31, 15), (96, 176, 210, 255)); rect(im, (33, 13, 37, 15), (96, 176, 210, 255))
    for x in range(27, 39, 3): px(im, x, 19, DARK)       # 通気孔
    poly(im, [(28, 4), (32, -1), (36, 4)], GOLD)         # 頭頂の飾り
    rect(im, (23, 10, 41, 12), GOLD)
    # 大剣（右手に立てる）
    rect(im, (50, 14, 54, 44), (222, 228, 240, 255))
    rect(im, (50, 14, 51, 44), lighten((222,228,240,255), 0.4))
    poly(im, [(50, 14), (52, 8), (54, 14)], (240, 244, 250, 255))
    rect(im, (46, 44, 58, 47), GOLD)
    rect(im, (51, 47, 53, 54), hexc('#6a4a2e'))
    ell(im, (50, 53, 54, 57), GOLD)
    outline(im)
    return im

def c3_mage():
    """魔道士（3頭身）：とんがり帽＋ローブ＋杖。"""
    im = new()
    ROBE = hexc('#7a4ab0'); ROBE_L = lighten(ROBE, 0.26); ROBE_D = darken(ROBE, 0.34)
    HAT = hexc('#5e2f92'); SKIN = hexc('#f2cfae'); HAIR = hexc('#e8d27a')
    GOLD = hexc('#ffd85c'); ORB = hexc('#7ce8ff')
    # ローブの裾（脚は見せずに広がる）
    poly(im, [(24, 40), (40, 40), (48, 60), (16, 60)], ROBE)
    poly(im, [(27, 42), (37, 42), (42, 58), (22, 58)], ROBE_L)
    for x in (22, 27, 32, 37, 42): line(im, [(x, 48), (x-1, 60)], ROBE_D)
    # 胴
    torso(im, ROBE, top=23, bot=44, w=17)
    poly(im, [(24, 24), (32, 24), (32, 42), (25, 42)], ROBE_L)
    rect(im, (23, 34, 41, 37), GOLD)                     # 帯
    # 腕（袖）
    poly(im, [(22, 26), (16, 38), (22, 40), (26, 30)], ROBE)
    poly(im, [(42, 26), (48, 36), (43, 39), (38, 30)], ROBE_D)
    ell(im, (14, 36, 22, 43), SKIN)                      # 手
    # 髪と顔
    ell(im, (22, 6, 42, 24), HAIR)
    head(im, SKIN, cy=14, rw=8, rh=9)
    ell(im, (24, 6, 40, 16), HAIR)
    poly(im, [(22, 12), (24, 22), (27, 12)], HAIR)
    poly(im, [(42, 12), (40, 22), (37, 12)], HAIR)
    # とんがり帽（顔より先に描き、目はつばの下へ）
    poly(im, [(18, 8), (32, -4), (46, 8)], HAT)
    poly(im, [(22, 7), (32, -1), (34, 4)], lighten(HAT, 0.24))
    ell(im, (16, 6, 48, 14), HAT)
    ell(im, (19, 7, 45, 12), lighten(HAT, 0.18))
    rect(im, (18, 5, 46, 8), GOLD)
    # 顔（つばの下に出す）
    eyes(im, (52, 40, 70, 255), y=16, dx=4, w=3, h=4, white=(250, 250, 255, 255))
    px(im, 32, 21, (206, 140, 130, 255))
    line(im, [(30, 23), (34, 23)], (198, 128, 122, 255))
    # 杖
    rect(im, (49, 18, 52, 58), hexc('#7a5230'))
    rect(im, (49, 18, 50, 58), lighten(hexc('#7a5230'), 0.28))
    ell(im, (45, 8, 57, 20), ORB)
    ell(im, (48, 10, 53, 15), (240, 254, 255, 255))
    outline(im)
    return im

def c3_ninja():
    """忍者（3頭身）：覆面＋たなびく襟巻き＋手裏剣。"""
    im = new()
    NAVY = hexc('#3d4a72'); NAVY_L = lighten(NAVY, 0.26); NAVY_D = darken(NAVY, 0.36)
    MASK = hexc('#232a44'); RED = hexc('#c8434a'); SKIN = hexc('#f0cba8')
    STEEL = hexc('#c3ccdd')
    # 襟巻き（後方へ）
    poly(im, [(38, 24), (60, 16), (54, 24), (62, 30), (40, 30)], RED)
    poly(im, [(40, 24), (56, 18), (52, 24)], lighten(RED, 0.22))
    # 脚
    legs(im, NAVY, boot=MASK, y0=41, y1=60, w=6, gap=4)
    rect(im, (25, 44, 39, 47), MASK)
    # 胴
    torso(im, NAVY, top=23, bot=44, w=17)
    poly(im, [(24, 24), (32, 24), (32, 42), (25, 42)], NAVY_L)
    rect(im, (23, 35, 41, 38), MASK)                     # 帯
    poly(im, [(23, 24), (32, 30), (41, 24), (41, 27), (32, 33), (23, 27)], NAVY_D)  # 打ち合わせ
    # 腕（片方は手裏剣を構える）
    arm(im, NAVY, -1, [(22, 27), (16, 36)], 4)
    arm(im, NAVY,  1, [(42, 27), (50, 22)], 4)
    ell(im, (14, 34, 21, 41), SKIN)
    ell(im, (48, 18, 55, 25), SKIN)
    # 頭（覆面）
    head(im, MASK, cy=14, rw=8, rh=9)
    ell(im, (25, 6, 39, 16), lighten(MASK, 0.18))
    poly(im, [(24, 12), (40, 12), (39, 17), (25, 17)], SKIN)   # 目元だけ肌
    eyes(im, (30, 34, 52, 255), y=13, dx=4, w=3, h=3, white=(248, 250, 255, 255))
    rect(im, (23, 9, 41, 12), RED)                        # 鉢巻
    poly(im, [(41, 9), (52, 6), (48, 12), (41, 12)], RED)
    # 手裏剣
    poly(im, [(52, 14), (54, 19), (59, 21), (54, 23), (52, 28), (50, 23), (45, 21), (50, 19)], STEEL)
    px(im, 52, 21, MASK)
    outline(im)
    return im

# ---- モンスター --------------------------------------------------------------

def m3_goblin():
    """ゴブリン（3頭身）：前かがみ、大きな耳、こん棒。"""
    im = new()
    SKIN = hexc('#8fbd52'); SKIN_L = lighten(SKIN, 0.26); SKIN_D = darken(SKIN, 0.36)
    CLOTH = hexc('#7a5a38'); DARK = (28, 34, 16, 255); WOOD = hexc('#8a5a30')
    # 脚（がに股）
    for s in (-1, 1):
        poly(im, [(32+s*4, 42), (32+s*11, 44), (32+s*12, 56), (32+s*5, 55)], SKIN_D)
        poly(im, [(32+s*4, 54), (32+s*14, 54), (32+s*14, 59), (32+s*4, 59)], DARK)
    # 胴（腰布）
    torso(im, SKIN, top=24, bot=45, w=18)
    poly(im, [(24, 25), (32, 25), (32, 43), (25, 43)], SKIN_L)
    poly(im, [(23, 38), (41, 38), (43, 47), (21, 47)], CLOTH)
    ell(im, (26, 32, 38, 41), SKIN_D)                    # 腹
    # 腕
    arm(im, SKIN, -1, [(22, 28), (15, 40)], 5)
    arm(im, SKIN,  1, [(42, 28), (49, 36)], 5)
    ell(im, (12, 37, 20, 45), SKIN_L)
    # 頭（大きめ・尖った耳）
    head(im, SKIN, cy=15, rw=9, rh=9)
    ell(im, (24, 7, 39, 17), SKIN_L)
    poly(im, [(23, 12), (8, 4), (16, 18)], SKIN)         # 左耳
    poly(im, [(41, 12), (56, 4), (48, 18)], SKIN_D)      # 右耳
    # 顔
    ell(im, (25, 11, 31, 17), (250, 250, 240, 255)); ell(im, (33, 11, 39, 17), (250, 250, 240, 255))
    ell(im, (27, 13, 30, 16), DARK); ell(im, (35, 13, 38, 16), DARK)
    poly(im, [(28, 19), (36, 19), (35, 22), (29, 22)], DARK)
    px(im, 29, 19, (250, 250, 240, 255)); px(im, 34, 19, (250, 250, 240, 255))
    px(im, 32, 18, SKIN_D)
    # こん棒
    poly(im, [(47, 34), (57, 16), (62, 20), (52, 38)], WOOD)
    ell(im, (52, 12, 63, 23), WOOD)
    ell(im, (54, 14, 60, 20), lighten(WOOD, 0.26))
    for x, y in [(55, 17), (58, 20), (53, 20)]: px(im, x, y, darken(WOOD, 0.3))
    outline(im)
    return im

def m3_skeleton():
    """スケルトン（3頭身）：肋骨と骨盤、剣と丸盾。"""
    im = new()
    BONE = hexc('#e6dfc4'); BONE_L = lighten(BONE, 0.26); BONE_D = darken(BONE, 0.30)
    DARK = (26, 24, 20, 255); STEEL = hexc('#c0c8d8'); SHIELD = hexc('#8a6a3a')
    # 脚（骨）
    for s in (-1, 1):
        rect(im, (32+s*5-2, 42, 32+s*5+1, 52), BONE)
        rect(im, (32+s*6-3, 52, 32+s*6+2, 56), BONE_D)
        rect(im, (32+s*7-4, 56, 32+s*7+3, 59), BONE)
        px(im, 32+s*5, 47, BONE_D)
    # 骨盤
    poly(im, [(25, 38), (39, 38), (41, 44), (32, 42), (23, 44)], BONE)
    # 背骨と肋骨
    rect(im, (31, 24, 33, 40), BONE_D)
    for k, y in enumerate((26, 30, 34)):
        w = 9 - k
        line(im, [(32-w, y), (32+w, y)], BONE)
        line(im, [(32-w, y+1), (32+w, y+1)], BONE_D)
        px(im, 32-w, y+2, BONE); px(im, 32+w, y+2, BONE)
    # 肩と腕
    line(im, [(22, 25), (42, 25)], BONE, 3)
    line(im, [(21, 26), (16, 38)], BONE, 3)
    line(im, [(43, 26), (49, 34)], BONE, 3)
    # 頭蓋
    head(im, BONE, cy=14, rw=8, rh=9)
    ell(im, (25, 6, 39, 16), BONE_L)
    ell(im, (24, 11, 31, 18), DARK); ell(im, (33, 11, 40, 18), DARK)
    px(im, 27, 14, hexc('#ff5a4a')); px(im, 36, 14, hexc('#ff5a4a'))
    poly(im, [(31, 18), (33, 18), (32, 21)], DARK)
    poly(im, [(26, 21, ), (38, 21), (37, 24), (27, 24)], BONE)
    for x in range(27, 38, 3): line(im, [(x, 21), (x, 24)], BONE_D)
    # 剣（右手）
    poly(im, [(48, 32), (52, 10), (55, 10), (52, 34)], STEEL)
    rect(im, (46, 32, 56, 35), hexc('#8a6a3a'))
    rect(im, (50, 35, 53, 40), hexc('#6a4a2a'))
    # 丸盾（左手）
    ell(im, (8, 30, 24, 46), SHIELD)
    ell(im, (11, 33, 21, 43), lighten(SHIELD, 0.24))
    ell(im, (14, 36, 18, 40), STEEL)
    outline(im)
    return im

def m3_sahagin():
    """サハギン（3頭身）：背びれ・水かき・銛。"""
    im = new()
    BODY = hexc('#4f9a9a'); BODY_L = lighten(BODY, 0.26); BODY_D = darken(BODY, 0.36)
    BELLY = hexc('#cfe6d8'); FIN = hexc('#2f6f7f'); EYE = hexc('#ffe07a')
    DARK = (14, 30, 34, 255); WOOD = hexc('#7a5638'); STEEL = hexc('#c8ccd4')
    # 水かきの足
    for s in (-1, 1):
        poly(im, [(32+s*4, 42), (32+s*10, 44), (32+s*11, 55), (32+s*4, 54)], BODY_D)
        poly(im, [(32+s*3, 54), (32+s*15, 56), (32+s*14, 60), (32+s*3, 59)], FIN)
    # 尾びれ
    poly(im, [(38, 40), (52, 46), (44, 48)], FIN)
    # 胴
    torso(im, BODY, top=23, bot=45, w=18)
    poly(im, [(24, 24), (32, 24), (32, 43), (25, 43)], BODY_L)
    poly(im, [(27, 28), (37, 28), (38, 44), (26, 44)], BELLY)
    for y in (32, 36, 40): line(im, [(27, y), (37, y)], darken(BELLY, 0.16))
    # 背びれ
    poly(im, [(30, 22), (34, 8), (38, 18), (42, 12), (42, 26)], FIN)
    # 腕（水かき）
    arm(im, BODY, -1, [(22, 27), (15, 38)], 5)
    arm(im, BODY,  1, [(42, 27), (48, 34)], 5)
    poly(im, [(12, 36), (20, 34), (21, 43), (11, 43)], FIN)
    # 頭（魚顔）
    head(im, BODY, cy=14, rw=9, rh=9)
    ell(im, (24, 6, 39, 16), BODY_L)
    poly(im, [(23, 14), (12, 10), (16, 20)], FIN)        # 頬びれ
    poly(im, [(41, 14), (52, 10), (48, 20)], FIN)
    ell(im, (24, 10, 31, 17), (250, 250, 250, 255)); ell(im, (33, 10, 40, 17), (250, 250, 250, 255))
    ell(im, (26, 12, 30, 16), EYE); ell(im, (35, 12, 39, 16), EYE)
    px(im, 27, 13, (255, 255, 255, 255)); px(im, 36, 13, (255, 255, 255, 255))
    ell(im, (26, 12, 28, 15), DARK); ell(im, (36, 12, 38, 15), DARK)
    poly(im, [(27, 19), (37, 19), (36, 23), (28, 23)], DARK)
    for x in range(28, 37, 3): poly(im, [(x, 19), (x+2, 19), (x+1, 22)], (245, 250, 245, 255))
    for k in range(3): line(im, [(22+k*2, 20+k), (26+k*2, 20+k)], BODY_D)   # えら
    # 銛
    rect(im, (52, 18, 55, 60), WOOD)
    rect(im, (52, 18, 53, 60), lighten(WOOD, 0.26))
    poly(im, [(53, 18), (49, 10), (52, 12), (53, 4), (55, 12), (58, 10), (54, 18)], STEEL)
    outline(im)
    return im

CH3 = {'k3_knight': c3_knight, 'k3_mage': c3_mage, 'k3_ninja': c3_ninja,
       'm3_goblin': m3_goblin, 'm3_skeleton': m3_skeleton, 'm3_sahagin': m3_sahagin}

def main():
    ids = sys.argv[1:] or list(CH3.keys())
    os.makedirs('assets/3head', exist_ok=True)
    for i in ids:
        if i not in CH3: print('unknown:', i); continue
        im = CH3[i]()
        im.save('assets/3head/%s.png' % i)
        cols = len({im.getpixel((x, y)) for y in range(S) for x in range(S) if im.getpixel((x, y))[3]})
        print('assets/3head/%s.png' % i, im.size, '色数:', cols)

if __name__ == '__main__':
    main()
