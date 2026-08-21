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

def e_skeledragon():
    """スケルトンドラゴン（ステージ③ラストボス）：骨の竜。横向きで「竜」と分かる構図。
    長い頭骨＋開いた顎、首の椎骨、肋骨の胴、背後に広げた骨の翼、伸びる尾。眼窩は紫の炎。"""
    im = new()
    BONE  = hexc('#e2dbc0'); BONE_L = lighten(BONE, 0.26); BONE_D = darken(BONE, 0.24)
    BONE_S = darken(BONE, 0.46)
    DARK  = (22, 18, 30, 255); FIRE = hexc('#b06aff'); FIRE_L = hexc('#e8caff')

    # ── 翼（体の後ろ＝右上に大きく広げる。指の骨と骨膜）
    root = (38, 34)
    tips = [(63, 2), (63, 16), (58, 28), (50, 36)]
    MEM = (58, 52, 62, 255)                                           # 骨膜（暗くして骨と分ける）
    for i in range(len(tips)-1):
        a, b = tips[i], tips[i+1]
        mid = ((a[0]+b[0])//2 - 3, (a[1]+b[1])//2 + 2)                # 後縁をえぐって膜らしく
        poly(im, [root, a, mid, b], MEM)
    for t in tips:                                                    # 指の骨
        line(im, [root, t], BONE_D, 2)
        line(im, [(root[0], root[1]-1), (t[0], t[1]-1)], BONE_L)
        for f in (0.4, 0.72):                                         # 指の関節
            px(im, int(root[0]+(t[0]-root[0])*f), int(root[1]+(t[1]-root[1])*f), BONE_L)
        px(im, t[0]-1, t[1]+1, BONE_L); px(im, t[0]-2, t[1]+2, BONE_D)
    ell(im, (root[0]-4, root[1]-4, root[0]+4, root[1]+4), BONE)       # 肩の関節
    px(im, root[0]-1, root[1]-2, BONE_L)

    # ── 尾（右下へ細くなる椎骨）
    for k in range(8):
        x = 44 + k*2 + (k*k)//6; y = 50 + (k*k)//7
        r = max(1, 4 - k//2)
        ell(im, (x-r, y-r, x+r, y+r), BONE if k % 2 == 0 else BONE_D)
    poly(im, [(60, 57), (63, 60), (58, 61)], BONE_L)

    # ── 肋骨の胴
    ell(im, (24, 34, 48, 56), BONE_D)
    ell(im, (26, 35, 46, 53), BONE)
    for k, y in enumerate((38, 42, 46, 50)):
        w = 10 - k
        line(im, [(36 - w, y), (36 + w, y)], BONE_S)
        line(im, [(36 - w, y-1), (36 + w, y-1)], BONE_L)
    line(im, [(36, 35), (36, 54)], BONE_S)

    # ── 後ろ脚（爪）
    for bx in (28, 40):
        poly(im, [(bx, 48), (bx+9, 50), (bx+8, 60), (bx-1, 58)], BONE)
        poly(im, [(bx+1, 50), (bx+7, 51), (bx+6, 57), (bx, 56)], BONE_D)
        for c in range(3):
            px(im, bx + c*3, 61, BONE_L); px(im, bx + c*3, 62, BONE_L)

    # ── 首（椎骨を頭へつなぐ）
    neck = [(30, 34), (26, 30), (23, 26), (21, 22)]
    for i, (x, y) in enumerate(neck):
        r = 4 - i//2
        ell(im, (x-r, y-r, x+r, y+r), BONE if i % 2 == 0 else BONE_D)
        px(im, x, y-r, BONE_L)

    # ── 頭骨（左を向く。長い鼻面＋開いた顎）
    poly(im, [(16, 14), (28, 16), (30, 26), (22, 30), (12, 28), (8, 22)], BONE)   # 頭蓋
    poly(im, [(17, 15), (26, 17), (27, 22), (14, 22)], BONE_L)
    poly(im, [(12, 22), (2, 26), (1, 30), (14, 30)], BONE)                        # 鼻面
    poly(im, [(12, 23), (4, 26), (4, 27), (13, 26)], BONE_L)
    px(im, 5, 27, DARK); px(im, 7, 26, DARK)                                      # 鼻孔
    poly(im, [(14, 31), (3, 33), (6, 37), (18, 35)], BONE_D)                      # 下顎（開いている）
    for x in range(4, 16, 3):                                                     # 牙（上下）
        poly(im, [(x, 29), (x+2, 29), (x+1, 34)], BONE_L)
        px(im, x+1, 33, BONE_D)
    for x in range(5, 16, 3):
        poly(im, [(x, 35), (x+2, 35), (x+1, 31)], BONE_L)
    # 眼窩＋紫の炎
    poly(im, [(15, 19), (23, 20), (22, 26), (14, 25)], DARK)
    ell(im, (16, 21, 21, 25), FIRE)
    px(im, 18, 22, FIRE_L)
    for x, y in [(16, 17), (19, 15), (22, 17)]:
        px(im, x, y, FIRE); px(im, x, y-1, FIRE_L)
    # 角（後方＝右上へ反る2本）
    poly(im, [(24, 16), (40, 6), (42, 10), (28, 20)], BONE_L)
    poly(im, [(23, 20), (38, 16), (38, 20), (26, 24)], BONE_D)
    px(im, 40, 7, BONE_L); px(im, 39, 17, BONE_L)
    return im

def e_sahagin():
    """サハギン：銛を持つ半魚人の戦士。背びれと大きな目、鱗の腹。"""
    im = new()
    BODY = hexc('#5aa0a0'); BODY_L = lighten(BODY, 0.26); BODY_D = darken(BODY, 0.32)
    BELLY = hexc('#cfe6d8'); EYE = hexc('#ffe07a'); DARK = (18, 34, 38, 255)
    SPEAR = hexc('#c8ccd4'); WOOD = hexc('#7a5a38')
    # 水かきの足
    for s2 in (-1, 1):
        poly(im, [(32 + s2*6, 50), (32 + s2*20, 56), (32 + s2*18, 60), (32 + s2*4, 58)], BODY_D)
    # 背びれ
    poly(im, [(30, 14), (34, 4), (38, 10), (42, 2), (44, 18)], BODY_D)
    # 体
    ell(im, (12, 14, 50, 56), BODY)
    ell(im, (16, 16, 38, 32), BODY_L)
    ell(im, (22, 34, 42, 54), BELLY)
    for y in (38, 43, 48):                      # 腹の鱗
        line(im, [(24, y), (40, y)], darken(BELLY, 0.16))
    # えら
    for k in range(3):
        line(im, [(14 + k*2, 30 + k*3), (20 + k*2, 30 + k*3)], BODY_D)
    # 目
    ell(im, (17, 20, 28, 31), (250, 250, 250, 255)); ell(im, (34, 20, 45, 31), (250, 250, 250, 255))
    ell(im, (20, 23, 25, 28), EYE); ell(im, (37, 23, 42, 28), EYE)
    px(im, 21, 24, (255, 255, 255, 255)); px(im, 38, 24, (255, 255, 255, 255))
    ell(im, (21, 24, 24, 27), DARK); ell(im, (38, 24, 41, 27), DARK)
    # 口と牙
    poly(im, [(24, 33), (40, 33), (37, 39), (27, 39)], DARK)
    for x in (26, 30, 34, 37): poly(im, [(x, 33), (x+2, 33), (x+1, 37)], (240, 244, 240, 255))
    # 銛
    line(im, [(52, 60), (52, 16)], WOOD, 3)
    line(im, [(51, 58), (51, 18)], lighten(WOOD, 0.28))
    poly(im, [(52, 16), (48, 10), (50, 4), (52, 10), (54, 4), (56, 10), (52, 16)], SPEAR)
    px(im, 50, 6, lighten(SPEAR, 0.4)); px(im, 54, 6, lighten(SPEAR, 0.4))
    return im

def e_crab():
    """カニ：巨大なハサミを盾のように構える。ハサミを割らないと本体に届かない。"""
    im = new()
    SH = hexc('#e07a4a'); SH_L = lighten(SH, 0.28); SH_D = darken(SH, 0.34)
    DARK = (40, 18, 12, 255); EYE = (250, 250, 250, 255)
    # 脚
    for s2 in (-1, 1):
        for k, y in enumerate((40, 46, 52)):
            poly(im, [(32 + s2*12, y), (32 + s2*24, y + 2 + k), (32 + s2*23, y + 6 + k), (32 + s2*11, y + 4)], SH_D)
    # 甲羅
    ell(im, (14, 20, 50, 50), SH)
    ell(im, (18, 22, 40, 34), SH_L)
    ell(im, (18, 38, 46, 49), SH_D)
    for x in (24, 32, 40): px(im, x, 30, SH_D)
    # 目（柄の先）
    for s2 in (-1, 1):
        x = 32 + s2*8
        line(im, [(x, 22), (x + s2*2, 12)], SH_D, 2)
        ell(im, (x + s2*2 - 4, 8, x + s2*2 + 4, 16), EYE)
        ell(im, (x + s2*2 - 2, 10, x + s2*2 + 2, 14), DARK)
    # 口
    poly(im, [(27, 40), (37, 40), (35, 44), (29, 44)], DARK)
    # 大きなハサミ（前に構える＝盾。上下に割れた鋏として描く）
    for s2 in (-1, 1):
        bx = 32 + s2*21
        # 付け根の腕
        poly(im, [(32 + s2*12, 34), (bx, 30), (bx, 44), (32 + s2*12, 44)], SH_D)
        # 下の鋏
        poly(im, [(bx - s2*4, 36), (bx + s2*13, 38), (bx + s2*15, 46), (bx - s2*3, 48)], SH)
        poly(im, [(bx - s2*2, 39), (bx + s2*10, 41), (bx + s2*11, 45), (bx - s2*1, 46)], SH_L)
        # 上の鋏（開いている）
        poly(im, [(bx - s2*4, 34), (bx + s2*14, 24), (bx + s2*17, 30), (bx - s2*2, 38)], SH)
        poly(im, [(bx - s2*2, 34), (bx + s2*11, 27), (bx + s2*12, 30), (bx - s2*1, 36)], SH_L)
        # 鋏の先の暗い縁と関節
        line(im, [(bx + s2*13, 38), (bx + s2*15, 46)], SH_D)
        line(im, [(bx + s2*14, 24), (bx + s2*17, 30)], SH_D)
        px(im, bx - s2*3, 37, DARK)
    return im

def e_jelly():
    """クラゲ：漂う傘と長い触手。触れると毒。"""
    im = new()
    BELL = hexc('#c0a0e0'); BELL_L = lighten(BELL, 0.34); BELL_D = darken(BELL, 0.28)
    POIS = hexc('#a8f0a0'); DARK = (44, 26, 68, 255)
    # 触手
    for k, x in enumerate((18, 25, 32, 39, 46)):
        w = 3 if k % 2 == 0 else 2
        pts = [(x, 36), (x + (2 if k % 2 else -2), 44), (x + (-2 if k % 2 else 2), 52), (x + (1 if k % 2 else -1), 60)]
        for i in range(len(pts)-1):
            line(im, [pts[i], pts[i+1]], BELL if i % 2 == 0 else BELL_D, w)
        px(im, pts[-1][0], 61, POIS)
    # 口腕（内側の短い房）
    for x in (27, 32, 37):
        line(im, [(x, 34), (x, 44)], BELL_L, 2)
    # 傘
    ell(im, (10, 10, 54, 42), BELL)
    ell(im, (14, 12, 42, 28), BELL_L)
    poly(im, [(10, 30), (54, 30), (50, 40), (44, 34), (38, 40), (32, 34), (26, 40), (20, 34), (14, 40)], BELL)
    ell(im, (24, 18, 40, 30), lighten(BELL, 0.5))          # 内側の透け
    # 毒の斑点
    for cx, cy in [(20, 20), (44, 22), (32, 14), (26, 27), (40, 30)]:
        ell(im, (cx-3, cy-2, cx+3, cy+2), POIS)
    # 目
    ell(im, (24, 22, 29, 28), DARK); ell(im, (35, 22, 40, 28), DARK)
    px(im, 25, 23, (255, 255, 255, 255)); px(im, 36, 23, (255, 255, 255, 255))
    return im

def e_kelpie():
    """ケルピー：水面を駆ける魔馬。たてがみと尾が水流。左向き。"""
    im = new()
    BODY = hexc('#7ab0d8'); BODY_L = lighten(BODY, 0.30); BODY_D = darken(BODY, 0.34)
    FOAM = hexc('#e4f4ff'); EYE = hexc('#8ef0ff'); DARK = (14, 32, 48, 255)
    # 尾（水流。後方へ長く）
    poly(im, [(46, 30), (63, 18), (60, 30), (64, 36), (52, 42), (46, 38)], BODY_D)
    poly(im, [(48, 30), (60, 22), (57, 30), (52, 36)], FOAM)
    # 胴（横に長い馬体）
    ell(im, (18, 30, 52, 50), BODY)
    ell(im, (22, 31, 44, 41), BODY_L)
    ell(im, (24, 42, 46, 50), BODY_D)
    # 脚（細く4本。前脚は駆けるように前へ）
    for bx, fw in ((21, 1), (28, 0), (39, 0), (45, 1)):
        poly(im, [(bx, 44), (bx+5, 44), (bx+4 - fw*2, 58), (bx - fw*2, 58)], BODY_D if fw else BODY)
        rect(im, (bx - fw*2, 57, bx+5 - fw*2, 60), FOAM)
    # 首（胴から左上へ）
    poly(im, [(18, 34), (14, 20), (26, 18), (28, 34)], BODY)
    poly(im, [(19, 32), (17, 22), (23, 21), (24, 32)], BODY_L)
    # 頭（左向き。長い鼻面）
    poly(im, [(2, 20), (16, 14), (22, 20), (18, 28), (6, 28)], BODY)
    poly(im, [(2, 21), (14, 16), (17, 21), (5, 25)], BODY_L)
    poly(im, [(1, 24), (8, 22), (9, 28), (2, 28)], BODY_D)      # 鼻先
    px(im, 3, 25, DARK); px(im, 4, 26, DARK)
    poly(im, [(9, 29), (18, 27), (17, 31), (10, 32)], BODY_D)   # 顎
    # 耳
    poly(im, [(15, 14), (16, 7), (20, 15)], BODY_D)
    poly(im, [(19, 14), (22, 8), (24, 16)], BODY_D)
    # たてがみ（泡立つ水の流れ）
    for k, (x, y, r) in enumerate([(22, 12, 6), (28, 16, 6), (34, 21, 6), (40, 26, 5), (45, 30, 4)]):
        ell(im, (x-r, y-r, x+r, y+r), FOAM if k % 2 == 0 else BODY_L)
        px(im, x, y-r+1, (255, 255, 255, 255))
    # 目
    ell(im, (9, 18, 15, 24), (250, 252, 255, 255))
    ell(im, (10, 19, 14, 23), EYE); px(im, 12, 20, DARK)
    return im

def e_serpent():
    """ミズチ：水を這う蛇竜。大きな頭と、重なりながらうねる胴。左向き。"""
    im = new()
    BODY = hexc('#4a9a7a'); BODY_L = lighten(BODY, 0.30); BODY_D = darken(BODY, 0.36)
    BELLY = hexc('#dceabc'); EYE = hexc('#ffd24a'); DARK = (12, 36, 30, 255)
    RED = hexc('#e05a5a')
    # 胴（後方が太く、前方へ細くなる重なった輪）
    seg = [(60, 22, 7), (54, 30, 7), (47, 37, 7), (39, 42, 6), (31, 45, 6), (24, 44, 5)]
    for i, (x, y, r) in enumerate(seg):
        ell(im, (x-r, y-r, x+r, y+r), BODY_D)
        ell(im, (x-r+1, y-r+1, x+r-1, y+r-1), BODY if i % 2 == 0 else BODY_L)
        ell(im, (x-r+2, y+1, x+r-3, y+r-1), BELLY)              # 腹
    poly(im, [(60, 14), (64, 10), (63, 24), (58, 26)], BODY_D)  # 尾びれ
    # 背びれ
    for x, y in [(56, 24), (49, 31), (42, 36), (35, 40)]:
        poly(im, [(x-4, y), (x, y-8), (x+4, y)], BODY_D)
        poly(im, [(x-2, y), (x, y-5), (x+2, y)], BODY_L)
    # 頭（大きく・左向き）
    poly(im, [(4, 28), (22, 22), (30, 32), (22, 44), (8, 42)], BODY)
    poly(im, [(6, 29), (20, 24), (25, 31), (10, 36)], BODY_L)
    poly(im, [(1, 32), (10, 28), (12, 38), (2, 40)], BODY)      # 鼻面
    px(im, 3, 33, DARK); px(im, 4, 34, DARK)
    poly(im, [(3, 40), (20, 41), (18, 46), (5, 45)], BELLY)     # 顎
    for x in range(6, 18, 3): poly(im, [(x, 40), (x+2, 40), (x+1, 44)], (250, 252, 240, 255))
    # 角
    poly(im, [(18, 24), (30, 12), (33, 17), (23, 28)], BODY_D)
    poly(im, [(13, 25), (21, 13), (25, 16), (18, 27)], BODY_D)
    # ひげ
    line(im, [(4, 42), (0, 52)], RED); line(im, [(8, 44), (4, 54)], RED)
    # 目
    ell(im, (10, 29, 18, 36), (252, 252, 240, 255))
    ell(im, (12, 30, 16, 35), EYE); px(im, 14, 32, DARK)
    return im

def e_shark():
    """サメ：突進してくる灰色のサメ。左向き。"""
    im = new()
    BODY = hexc('#9aa8b8'); BODY_L = lighten(BODY, 0.26); BODY_D = darken(BODY, 0.34)
    BELLY = hexc('#e8eef4'); DARK = (20, 26, 36, 255); GUM = hexc('#d47a86')
    # 尾びれ
    poly(im, [(48, 30), (62, 16), (58, 32), (63, 44), (48, 40)], BODY_D)
    poly(im, [(50, 30), (59, 20), (57, 31), (52, 36)], BODY)
    # 胴（左が頭）
    poly(im, [(4, 32), (16, 22), (34, 20), (50, 28), (52, 36), (34, 46), (16, 46), (4, 38)], BODY)
    poly(im, [(8, 28), (22, 24), (38, 24), (48, 30), (34, 34), (16, 34)], BODY_L)
    poly(im, [(6, 38), (20, 42), (38, 42), (50, 36), (34, 46), (16, 46)], BELLY)
    # 背びれ
    poly(im, [(24, 21), (32, 6), (38, 22)], BODY_D)
    poly(im, [(27, 20), (32, 10), (34, 20)], BODY)
    # 胸びれ
    poly(im, [(18, 40), (10, 54), (26, 46)], BODY_D)
    poly(im, [(34, 40), (30, 52), (44, 44)], BODY_D)
    # えら
    for k in range(3):
        line(im, [(18 + k*3, 30), (18 + k*3, 38)], BODY_D)
    # 口と牙
    poly(im, [(3, 36), (20, 38), (18, 44), (4, 41)], GUM)
    for x in range(5, 18, 3):
        poly(im, [(x, 37), (x+2, 37), (x+1, 41)], (250, 252, 250, 255))
        poly(im, [(x+1, 43), (x+3, 43), (x+2, 39)], (250, 252, 250, 255))
    # 目
    ell(im, (10, 28, 16, 34), (250, 250, 250, 255))
    ell(im, (11, 29, 15, 33), DARK); px(im, 12, 30, (255, 255, 255, 255))
    return im

def e_manta():
    """マンタ：真上から見た大きなエイ。ゆったり飛ぶように泳ぐ。"""
    im = new()
    BODY = hexc('#5a6a8a'); BODY_L = lighten(BODY, 0.26); BODY_D = darken(BODY, 0.34)
    BELLY = hexc('#c8d4e4'); DARK = (14, 18, 28, 255)
    # 尾
    poly(im, [(30, 44), (34, 44), (33, 62), (31, 62)], BODY_D)
    # 翼（ひし形）
    poly(im, [(32, 12), (62, 34), (46, 44), (32, 48), (18, 44), (2, 34)], BODY)
    poly(im, [(32, 16), (54, 33), (42, 39), (32, 41), (22, 39), (10, 33)], BODY_L)
    # 翼の先の陰
    poly(im, [(2, 34), (16, 30), (18, 44)], BODY_D)
    poly(im, [(62, 34), (48, 30), (46, 44)], BODY_D)
    # 頭のひれ（頭鰭）
    poly(im, [(24, 14), (20, 4), (27, 12)], BODY_D)
    poly(im, [(40, 14), (44, 4), (37, 12)], BODY_D)
    # 白い斑点
    for cx, cy in [(20, 26), (44, 26), (32, 22), (14, 33), (50, 33)]:
        ell(im, (cx-3, cy-2, cx+3, cy+2), BELLY)
    # 目
    ell(im, (24, 18, 29, 23), (250, 250, 250, 255)); ell(im, (35, 18, 40, 23), (250, 250, 250, 255))
    ell(im, (25, 19, 28, 22), DARK); ell(im, (36, 19, 39, 22), DARK)
    return im

def e_hermit():
    """ヤドカリ：渦巻の宿を背負い、ハサミを構える。素早い。"""
    im = new()
    SHELL = hexc('#d0a060'); SHELL_L = lighten(SHELL, 0.28); SHELL_D = darken(SHELL, 0.36)
    BODY = hexc('#e0705a'); BODY_D = darken(BODY, 0.30); DARK = (36, 20, 12, 255)
    # 脚
    for s2 in (-1, 1):
        for k, y in enumerate((46, 52)):
            poly(im, [(32 + s2*8, y), (32 + s2*18, y+3), (32 + s2*17, y+7), (32 + s2*7, y+4)], BODY_D)
    # 宿（渦巻の貝）
    ell(im, (18, 8, 58, 48), SHELL)
    ell(im, (22, 10, 50, 34), SHELL_L)
    # 渦
    for k, r in enumerate((16, 11, 6, 3)):
        cx, cy = 40 - k, 28 - k
        D(im).arc((cx-r, cy-r, cx+r, cy+r), 20 + k*40, 320 + k*40, fill=SHELL_D if k % 2 == 0 else SHELL)
    for x, y in [(24, 40), (34, 44), (46, 42), (52, 32)]:
        px(im, x, y, SHELL_D)
    # 体（貝から出た前半身）
    ell(im, (8, 28, 30, 48), BODY)
    ell(im, (11, 30, 24, 39), lighten(BODY, 0.24))
    # 目（柄）
    for s2 in (-1, 1):
        x = 18 + s2*5
        line(im, [(x, 30), (x + s2*2, 20)], BODY_D, 2)
        ell(im, (x + s2*2 - 3, 16, x + s2*2 + 3, 22), (250, 250, 250, 255))
        ell(im, (x + s2*2 - 1, 18, x + s2*2 + 1, 20), DARK)
    # ハサミ（前に構える）
    for by, sz in ((34, 8), (42, 6)):
        ell(im, (2, by, 2 + sz + 6, by + sz), BODY)
        poly(im, [(2, by), (2 - 2, by - 4), (8, by + 2)], BODY_D)
        line(im, [(3, by + sz//2), (2 + sz + 4, by + sz//2)], DARK)
    return im

def e_clam():
    """カイ：砂に潜む二枚貝。開いた殻の奥に真珠。"""
    im = new()
    SH = hexc('#c09ac0'); SH_L = lighten(SH, 0.30); SH_D = darken(SH, 0.34)
    FLESH = hexc('#e88aa0'); PEARL = (250, 250, 240, 255); DARK = (40, 22, 44, 255)
    SAND = hexc('#c8b088')
    # 砂
    ell(im, (6, 48, 58, 60), SAND)
    ell(im, (12, 50, 52, 56), lighten(SAND, 0.22))
    # 下の殻
    poly(im, [(8, 34), (32, 30), (56, 34), (52, 52), (12, 52)], SH)
    for k in range(6):                                   # 放射状の筋
        line(im, [(32, 32), (10 + k*9, 52)], SH_D)
    poly(im, [(12, 46), (52, 46), (50, 52), (14, 52)], SH_L)
    # 中身と真珠
    ell(im, (18, 30, 46, 44), FLESH)
    ell(im, (22, 32, 42, 40), lighten(FLESH, 0.26))
    ell(im, (27, 31, 37, 41), PEARL)
    ell(im, (29, 33, 33, 37), (255, 255, 255, 255))
    # 上の殻（扇形に開く）
    D(im).pieslice((6, 6, 58, 50), 180, 360, fill=SH)
    D(im).pieslice((10, 10, 54, 46), 180, 360, fill=SH_L)
    for k in range(7):
        line(im, [(32, 30), (8 + k*8, 12 if 1 < k < 5 else 18)], SH_D)
    D(im).arc((6, 6, 58, 50), 180, 360, fill=SH_D)
    rect(im, (8, 28, 56, 31), SH)
    rect(im, (8, 30, 56, 31), SH_D)
    # 目
    ell(im, (24, 34, 29, 39), (250, 250, 250, 255)); ell(im, (35, 34, 40, 39), (250, 250, 250, 255))
    ell(im, (25, 35, 28, 38), DARK); ell(im, (36, 35, 39, 38), DARK)
    return im

def e_siren():
    """セイレーン：歌で光線を放つ海妖。長い髪と魚の尾。"""
    im = new()
    SKIN = hexc('#f0c0b0'); SKIN_L = lighten(SKIN, 0.22)
    HAIR = hexc('#7ad0c8'); HAIR_L = lighten(HAIR, 0.26); HAIR_D = darken(HAIR, 0.32)
    TAIL = hexc('#e0a0b0'); TAIL_L = lighten(TAIL, 0.28); TAIL_D = darken(TAIL, 0.32)
    DARK = (52, 26, 40, 255); GLOW = hexc('#fff0a0')
    # 尾（下半身）
    poly(im, [(22, 38), (42, 38), (44, 50), (36, 56), (28, 56), (20, 50)], TAIL)
    for y in (42, 47, 52):
        line(im, [(23, y), (41, y)], TAIL_D)
    poly(im, [(28, 54), (16, 62), (32, 58), (48, 62), (36, 54)], TAIL_L)   # 尾びれ
    # 髪（後ろ）
    ell(im, (10, 8, 54, 46), HAIR)
    poly(im, [(10, 30), (6, 50), (16, 44), (18, 30)], HAIR_D)
    poly(im, [(54, 30), (58, 50), (48, 44), (46, 30)], HAIR_D)
    # 顔と上半身
    ell(im, (22, 28, 42, 42), SKIN)                                        # 胴
    ell(im, (21, 12, 43, 34), SKIN)                                        # 顔
    ell(im, (24, 14, 40, 24), SKIN_L)
    # 前髪
    poly(im, [(20, 22), (22, 10), (32, 6), (44, 10), (44, 22), (40, 14), (32, 12), (24, 15)], HAIR)
    poly(im, [(23, 18), (26, 10), (33, 8), (28, 14)], HAIR_L)
    # 目と歌う口
    ell(im, (25, 21, 30, 27), (250, 250, 250, 255)); ell(im, (34, 21, 39, 27), (250, 250, 250, 255))
    ell(im, (26, 22, 29, 26), DARK); ell(im, (35, 22, 38, 26), DARK)
    ell(im, (29, 30, 35, 35), DARK); ell(im, (30, 31, 34, 34), hexc('#8a3a50'))
    px(im, 32, 32, GLOW)
    for r in (7, 11):                                  # 口から右へ広がる歌の輪（顔にかからないように）
        D(im).arc((36-r, 33-r, 36+r, 33+r), 300, 60, fill=GLOW)
    # 歌（音符）
    for cx, cy in [(50, 16), (56, 24)]:
        ell(im, (cx-3, cy-2, cx+1, cy+2), GLOW)
        line(im, [(cx+1, cy), (cx+1, cy-6)], GLOW)
    return im

def e_flyingfish():
    """トビウオ：まっすぐ突っ切る小魚。大きな胸びれ。"""
    im = new()
    BODY = hexc('#8fd4ff'); BODY_L = lighten(BODY, 0.30); BODY_D = darken(BODY, 0.34)
    BELLY = (240, 250, 255, 255); DARK = (18, 40, 60, 255)
    # 胸びれ（大きな翼）
    poly(im, [(28, 28), (52, 8), (48, 26), (30, 34)], BODY_D)
    poly(im, [(28, 34), (50, 52), (46, 38), (30, 32)], BODY_D)
    poly(im, [(30, 28), (46, 14), (44, 25)], BODY_L)
    # 胴（左向き）
    poly(im, [(6, 30), (18, 22), (36, 24), (48, 32), (36, 40), (18, 42)], BODY)
    poly(im, [(10, 28), (22, 25), (38, 28), (44, 32), (26, 33)], BODY_L)
    poly(im, [(10, 36), (26, 38), (40, 36), (34, 40), (18, 41)], BELLY)
    # 尾びれ
    poly(im, [(46, 32), (60, 22), (56, 32), (60, 44)], BODY)
    poly(im, [(48, 32), (57, 26), (55, 32)], BODY_L)
    # 目
    ell(im, (10, 28, 16, 34), (250, 252, 255, 255))
    ell(im, (11, 29, 15, 33), DARK); px(im, 12, 30, (255, 255, 255, 255))
    return im

def e_whale():
    """ホエール（ステージ④ボス1）：跳ねる巨鯨。潮吹き。左向き。"""
    im = new()
    BODY = hexc('#3a5a8a'); BODY_L = lighten(BODY, 0.26); BODY_D = darken(BODY, 0.36)
    BELLY = hexc('#cfe0f0'); DARK = (10, 18, 32, 255); FOAM = (232, 246, 255, 255)
    # 潮吹き
    for k, (x, y, r) in enumerate([(30, 8, 5), (26, 3, 4), (35, 3, 4), (30, 0, 3)]):
        ell(im, (x-r, y-r, x+r, y+r), FOAM if k % 2 == 0 else lighten(BODY, 0.55))
    # 尾びれ
    poly(im, [(48, 34), (63, 22), (58, 36), (63, 50), (48, 42)], BODY_D)
    poly(im, [(50, 34), (60, 26), (57, 36), (52, 40)], BODY)
    # 胴（左が頭）
    poly(im, [(2, 34), (10, 22), (28, 18), (44, 24), (52, 36), (44, 48), (24, 52), (8, 46)], BODY)
    poly(im, [(8, 28), (24, 22), (40, 26), (48, 34), (30, 34), (14, 34)], BODY_L)
    poly(im, [(6, 42), (22, 48), (40, 46), (50, 38), (34, 52), (16, 50)], BELLY)
    for x in range(8, 34, 4):                              # 腹の畝
        line(im, [(x, 42), (x+2, 50)], darken(BELLY, 0.16))
    # 胸びれ
    poly(im, [(20, 46), (14, 58), (32, 50)], BODY_D)
    # 口
    poly(im, [(2, 38), (22, 42), (20, 46), (3, 43)], DARK)
    # 目
    ell(im, (10, 30, 17, 37), (250, 250, 250, 255))
    ell(im, (11, 31, 15, 35), DARK); px(im, 12, 32, (255, 255, 255, 255))
    # 噴気孔
    ell(im, (27, 17, 33, 21), DARK)
    return im

def e_kraken():
    """クラーケン（ステージ④ボス2）：深海の大烏賊。太い触手と墨。"""
    im = new()
    BODY = hexc('#6a3a7a'); BODY_L = lighten(BODY, 0.26); BODY_D = darken(BODY, 0.38)
    SUCK = hexc('#e0a8c0'); EYE = hexc('#ffe07a'); DARK = (16, 6, 24, 255)
    # 触手（下に広がる8本）
    for k, (x0, bend) in enumerate([(6, 1), (14, -1), (22, 1), (30, -1), (38, 1), (46, -1), (54, 1), (58, -1)]):
        x, y = x0, 40
        for i in range(4):
            r = 5 - i
            ell(im, (x-r, y-r, x+r, y+r), BODY if (k + i) % 2 == 0 else BODY_D)
            x += bend * (2 + i); y += 5
        px(im, x, y-4, SUCK)
    # 外套（頭）
    poly(im, [(32, 2), (52, 22), (48, 42), (16, 42), (12, 22)], BODY)
    poly(im, [(32, 6), (46, 22), (42, 34), (22, 34), (18, 22)], BODY_L)
    # ひれ
    poly(im, [(12, 20), (2, 12), (8, 28)], BODY_D)
    poly(im, [(52, 20), (62, 12), (56, 28)], BODY_D)
    # 目
    ell(im, (16, 26, 28, 38), (250, 250, 250, 255)); ell(im, (36, 26, 48, 38), (250, 250, 250, 255))
    ell(im, (19, 29, 25, 35), EYE); ell(im, (39, 29, 45, 35), EYE)
    rect(im, (21, 29, 23, 35), DARK); rect(im, (41, 29, 43, 35), DARK)
    px(im, 20, 30, (255, 255, 255, 255)); px(im, 40, 30, (255, 255, 255, 255))
    # 吸盤
    for x, y in [(10, 44), (20, 48), (30, 50), (40, 48), (50, 44)]:
        px(im, x, y, SUCK)
    return im

def e_tornadoshark():
    """トルネードシャーク（ステージ④ボス3）：竜巻を纏う鮫。"""
    im = new()
    BODY = hexc('#8aa0b8'); BODY_L = lighten(BODY, 0.28); BODY_D = darken(BODY, 0.36)
    BELLY = (236, 244, 250, 255); WIND = hexc('#bfe4f5'); DARK = (18, 26, 38, 255)
    GUM = hexc('#d47a86')
    # 竜巻（下半分の渦）
    for k, (w, y) in enumerate([(30, 34), (26, 40), (21, 46), (16, 52), (11, 58)]):
        D(im).ellipse((32-w, y-4, 32+w, y+4), fill=WIND if k % 2 == 0 else lighten(WIND, 0.35))
        D(im).arc((32-w, y-5, 32+w, y+5), 200, 340, fill=(255, 255, 255, 255))
    # 鮫の体（竜巻から上半身を出す。左向き）
    poly(im, [(4, 22), (16, 12), (36, 12), (52, 20), (50, 32), (30, 38), (12, 36)], BODY)
    poly(im, [(10, 18), (24, 14), (40, 16), (48, 22), (30, 26), (14, 26)], BODY_L)
    poly(im, [(8, 30), (26, 34), (44, 30), (30, 38), (14, 36)], BELLY)
    # 背びれ・尾
    poly(im, [(26, 12), (34, 0), (40, 13)], BODY_D)
    poly(im, [(50, 20), (63, 10), (58, 22), (62, 32), (50, 30)], BODY_D)
    # えら
    for k in range(3): line(im, [(18 + k*3, 20), (18 + k*3, 28)], BODY_D)
    # 口と牙
    poly(im, [(3, 26), (20, 28), (18, 34), (4, 31)], GUM)
    for x in range(5, 18, 3):
        poly(im, [(x, 27), (x+2, 27), (x+1, 31)], (250, 252, 250, 255))
        poly(im, [(x+1, 33), (x+3, 33), (x+2, 29)], (250, 252, 250, 255))
    # 目
    ell(im, (10, 18, 16, 24), (250, 250, 250, 255))
    ell(im, (11, 19, 15, 23), DARK); px(im, 12, 20, (255, 255, 255, 255))
    return im

def e_leviathan():
    """リヴァイアサン（ステージ④ラストボス）：海の主たる古の大蛇。
    連続した胴のうねり＋大きな頭と角、光る眼。左向き。"""
    im = new()
    BODY = hexc('#2a4a6a'); BODY_L = lighten(BODY, 0.24); BODY_D = darken(BODY, 0.42)
    FIN  = hexc('#3f7a9c'); BELLY = hexc('#a8c8dc'); EYE = hexc('#ffd24a')
    DARK = (6, 14, 24, 255); TEETH = (245, 250, 250, 255)
    # ── 胴：中心線に沿って円を重ねて「1本の蛇」にする（色は一定・境目を作らない）
    spine = [(62, 6), (58, 12), (53, 18), (48, 24), (43, 29), (38, 34),
             (33, 38), (28, 42), (23, 45)]
    for i, (x, y) in enumerate(spine):
        r = 5 + i                                  # 頭側ほど太い
        ell(im, (x-r-1, y-r-1, x+r+1, y+r+1), BODY_D)     # 縁
        ell(im, (x-r, y-r, x+r, y+r), BODY)
    for i, (x, y) in enumerate(spine):             # 背側のハイライトと腹
        r = 5 + i
        ell(im, (x-r+2, y-r+1, x+r-3, y-1), BODY_L)
        ell(im, (x-r+3, y+1, x+r-3, y+r-1), BELLY)
    # 背びれ（小さめ・胴の色でまとめる）
    for i in (1, 3, 5, 7):
        x, y = spine[i]; r = 5 + i
        poly(im, [(x-4, y-r+1), (x, y-r-5), (x+4, y-r+1)], FIN)
    poly(im, [(62, 2), (63, 14), (58, 8)], FIN)    # 尾の先
    # 胸びれ
    poly(im, [(26, 48), (14, 58), (30, 52)], FIN)
    # ── 頭（左向き・大きい）
    poly(im, [(3, 30), (20, 24), (30, 33), (26, 49), (10, 51)], BODY)
    poly(im, [(5, 31), (19, 26), (26, 33), (11, 40)], BODY_L)
    poly(im, [(0, 36), (11, 32), (13, 43), (1, 45)], BODY)          # 鼻面
    px(im, 2, 37, DARK); px(im, 4, 36, DARK)
    poly(im, [(1, 45), (22, 46), (20, 53), (3, 51)], BODY_D)        # 下顎
    poly(im, [(3, 46), (20, 47), (19, 51), (4, 50)], TEETH)
    for x in range(4, 20, 3):
        poly(im, [(x, 42), (x+2, 42), (x+1, 46)], TEETH)
    # 角（2対・後方へ反る）
    poly(im, [(19, 26), (33, 11), (36, 16), (24, 30)], FIN)
    poly(im, [(13, 27), (23, 11), (27, 14), (18, 30)], FIN)
    px(im, 33, 12, lighten(FIN, 0.45)); px(im, 24, 12, lighten(FIN, 0.45))
    # 眼（光る）
    ell(im, (8, 31, 18, 40), (250, 250, 240, 255))
    ell(im, (10, 32, 16, 39), EYE)
    rect(im, (12, 33, 14, 39), DARK)
    px(im, 11, 34, (255, 255, 255, 255))
    return im

def e_umibozu():
    """海坊主：夜の海の巨大な影。白い眼と裂けた口だけが見える。"""
    im = new()
    BODY = (18, 18, 30, 255); BODY_L = (34, 34, 54, 255); EDGE = (58, 56, 88, 255)
    WHITE = (238, 242, 250, 255); DARK = (4, 4, 10, 255)
    # 影の本体（下がにじむ）
    ell(im, (6, 6, 58, 54), BODY)
    poly(im, [(8, 40), (56, 40), (58, 58), (48, 52), (38, 60), (28, 52), (18, 60), (8, 52)], BODY)
    ell(im, (12, 10, 44, 32), BODY_L)
    # 輪郭のにじみ
    for x, y in [(10, 14), (52, 16), (8, 30), (56, 34), (16, 50), (46, 50)]:
        ell(im, (x-3, y-3, x+3, y+3), EDGE)
    # 眼
    ell(im, (16, 22, 28, 34), WHITE); ell(im, (36, 22, 48, 34), WHITE)
    ell(im, (20, 26, 25, 31), DARK); ell(im, (40, 26, 45, 31), DARK)
    px(im, 21, 27, WHITE); px(im, 41, 27, WHITE)
    # 裂けた口
    poly(im, [(20, 40), (44, 40), (38, 48), (26, 48)], DARK)
    for x in range(22, 42, 4):
        poly(im, [(x, 40), (x+2, 40), (x+1, 44)], WHITE)
    return im

def e_fly():
    """フライ：死肉に群がるハエ。まっすぐ突っ切る小型のスウォーム。"""
    im = new()
    BODY = hexc('#7a8a4a'); BODY_L = lighten(BODY, 0.30); BODY_D = darken(BODY, 0.36)
    EYE = hexc('#d04a3a'); WING = (198, 226, 236, 190); DARK = (18, 22, 12, 255)
    # 羽
    poly(im, [(30, 24), (56, 8), (58, 22), (34, 32)], WING)
    poly(im, [(30, 30), (56, 40), (52, 50), (32, 36)], WING)
    line(im, [(32, 25), (54, 12)], (240, 250, 255, 220))
    # 腹（縞）
    ell(im, (18, 22, 46, 44), BODY)
    for y in (28, 33, 38):
        line(im, [(22, y), (44, y)], BODY_D)
    ell(im, (21, 24, 36, 32), BODY_L)
    # 頭と複眼
    ell(im, (6, 20, 26, 40), BODY_D)
    ell(im, (7, 21, 18, 32), EYE); ell(im, (16, 24, 25, 36), darken(EYE, 0.22))
    px(im, 10, 24, (255, 220, 210, 255))
    # 脚
    for k, y in enumerate((40, 44)):
        line(im, [(20 + k*6, y), (14 + k*6, y + 10)], DARK)
        line(im, [(30 + k*6, y), (36 + k*6, y + 10)], DARK)
    return im

def e_gnat():
    """スウォームナット：羽虫の群れの1匹。細身で羽が大きい。"""
    im = new()
    BODY = hexc('#8a7a52'); BODY_L = lighten(BODY, 0.30); BODY_D = darken(BODY, 0.34)
    WING = (222, 226, 210, 170); DARK = (24, 20, 12, 255)
    poly(im, [(28, 26), (54, 12), (56, 24), (32, 32)], WING)
    poly(im, [(28, 30), (54, 44), (50, 52), (30, 36)], WING)
    # 細長い腹
    poly(im, [(16, 26), (44, 28), (48, 34), (16, 38)], BODY)
    poly(im, [(18, 28), (40, 30), (42, 32), (18, 33)], BODY_L)
    for x in (28, 34, 40): line(im, [(x, 29), (x, 37)], BODY_D)
    # 頭
    ell(im, (6, 24, 20, 38), BODY_D)
    ell(im, (8, 26, 14, 32), DARK)
    px(im, 9, 27, (240, 236, 220, 255))
    # 脚
    for k in range(3):
        line(im, [(20 + k*7, 36), (14 + k*7, 48)], DARK)
    return im

def e_archer():
    """ゴブリンアーチャー：弓を構えるゴブリン。既存ゴブリンと同系の緑。"""
    im = new()
    SKIN = hexc('#a8cc60'); SKIN_L = lighten(SKIN, 0.26); SKIN_D = darken(SKIN, 0.34)
    CLOTH = hexc('#6a5a38'); WOOD = hexc('#8a5a30'); DARK = (28, 34, 14, 255)
    feet(im, CLOTH, y=50, dx=9, w=12, h=9)
    # 体
    ell(im, (12, 16, 48, 52), SKIN)
    ell(im, (16, 18, 36, 32), SKIN_L)
    ell(im, (18, 38, 42, 50), SKIN_D)
    # 耳
    poly(im, [(12, 26), (0, 18), (10, 34)], SKIN)
    poly(im, [(48, 26), (60, 18), (50, 34)], SKIN_D)
    # 頭巾
    poly(im, [(12, 22), (18, 10), (32, 6), (46, 12), (48, 22), (40, 16), (30, 14), (18, 18)], CLOTH)
    poly(im, [(18, 18), (24, 10), (32, 8), (26, 15)], lighten(CLOTH, 0.24))
    # 目と口
    ell(im, (18, 26, 27, 34), (250, 250, 240, 255)); ell(im, (33, 26, 42, 34), (250, 250, 240, 255))
    ell(im, (21, 28, 25, 32), DARK); ell(im, (36, 28, 40, 32), DARK)
    px(im, 22, 29, (255, 255, 255, 255)); px(im, 37, 29, (255, 255, 255, 255))
    poly(im, [(25, 38), (37, 38), (35, 43), (27, 43)], DARK)
    for x in (27, 31, 34): poly(im, [(x, 38), (x+2, 38), (x+1, 41)], (250, 250, 240, 255))
    # 弓（右）
    for t in range(0, 34):
        y = 14 + t
        dx = int(8 - (t - 17) * (t - 17) * 0.028)
        px(im, 52 + dx, y, WOOD); px(im, 53 + dx, y, lighten(WOOD, 0.26))
    line(im, [(54, 14), (54, 47)], (236, 230, 210, 255))
    # 矢（顔にかからないよう下げる）
    line(im, [(46, 34), (62, 34)], (200, 194, 174, 255))
    poly(im, [(62, 32), (64, 34), (62, 36)], (214, 214, 220, 255))
    return im

def e_sharkmissile():
    """サメミサイル：リヴァイアサンが放つ金属のサメ型ミサイル。
    進行方向へ回転させて描かれるので、右(+x)を向いた絵にする。"""
    im = new()
    HULL = hexc('#9ab0c8'); HULL_L = lighten(HULL, 0.30); HULL_D = darken(HULL, 0.36)
    FIRE = hexc('#ff9a3a'); CORE = hexc('#ffe0a0'); DARK = (18, 26, 38, 255)
    RED = hexc('#c8443a')
    # 噴射炎（後方＝左）
    poly(im, [(6, 32), (0, 26), (2, 32), (0, 38)], FIRE)
    poly(im, [(10, 32), (4, 28), (6, 32), (4, 36)], CORE)
    # 胴（右が頭）
    poly(im, [(8, 26), (40, 22), (56, 32), (40, 42), (8, 38)], HULL)
    poly(im, [(12, 26), (38, 24), (50, 30), (30, 32), (14, 30)], HULL_L)
    poly(im, [(12, 36), (34, 38), (48, 34), (30, 34), (14, 34)], HULL_D)
    # 背びれと尾びれ
    poly(im, [(24, 22), (30, 10), (36, 23)], HULL_D)
    poly(im, [(10, 26), (2, 18), (8, 30)], HULL_D)
    poly(im, [(22, 40), (18, 52), (32, 42)], HULL_D)
    # 継ぎ目のリベット
    for x in (20, 28, 36): px(im, x, 32, DARK)
    line(im, [(16, 27), (16, 37)], HULL_D)
    # 顎（口の赤）
    poly(im, [(44, 30), (56, 32), (44, 36)], RED)
    for x in (46, 49, 52): poly(im, [(x, 30), (x+2, 31), (x, 33)], (240, 246, 250, 255))
    # 目（センサー）
    ell(im, (40, 26, 46, 32), (250, 250, 250, 255))
    ell(im, (41, 27, 45, 31), RED); px(im, 42, 28, (255, 230, 220, 255))
    return im

ENEMIES = {'lich': e_lich, 'necro': e_necro, 'dullahan': e_dullahan,
           'boomer': e_boomer, 'gargoyle': e_gargoyle, 'sarcher': e_sarcher,
           'skeledragon': e_skeledragon,
           'sahagin': e_sahagin, 'crab': e_crab, 'jelly': e_jelly,
           'kelpie': e_kelpie, 'serpent': e_serpent,
           'shark': e_shark, 'manta': e_manta, 'hermit': e_hermit,
           'clam': e_clam, 'siren': e_siren, 'flyingfish': e_flyingfish,
           'whale': e_whale, 'kraken': e_kraken, 'tornadoshark': e_tornadoshark,
           'leviathan': e_leviathan, 'umibozu': e_umibozu,
           'fly': e_fly, 'gnat': e_gnat, 'archer': e_archer, 'sharkmissile': e_sharkmissile}

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
