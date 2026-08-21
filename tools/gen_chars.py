# -*- coding: utf-8 -*-
"""キャラ立ち絵（64x64 ドット絵）の生成スクリプト。
既存 assets/*.png（knight/hunter/bomber/mage/saint）の規格に合わせつつ、描き込みを増やした版：
  - 64x64 RGBA / アンチエイリアス無し / シルエット外周に 1px の黒縁(#131313)
  - まん丸のチビ体型：球体の胴＋下に小さな足2つ＋顔＋頭装備＋手持ち小物
  - 各素材は「明・基本・影」の3階調＋ハイライト点。目安12〜16色
使い方: python3 tools/gen_chars.py [キャラid ...]   （省略時は全部）
"""
import os, sys
from PIL import Image, ImageDraw

S = 64
OUT = (19, 19, 19, 255)
TR  = (0, 0, 0, 0)

def new(): return Image.new('RGBA', (S, S), TR)
def D(im): return ImageDraw.Draw(im)
def ell(im, b, c):  D(im).ellipse(b, fill=c)
def rect(im, b, c): D(im).rectangle(b, fill=c)
def poly(im, p, c): D(im).polygon(p, fill=c)
def line(im, p, c, w=1): D(im).line(p, fill=c, width=w)
def px(im, x, y, c): im.putpixel((x, y), c)

def mix(c, t, f):
    """c を t（色）方向へ f だけ寄せる。"""
    return tuple(int(c[i] + (t[i] - c[i]) * f) for i in range(3)) + (255,)

def lighten(c, f=0.35): return mix(c, (255, 255, 255, 255), f)
def darken(c, f=0.35):  return mix(c, (10, 8, 20, 255), f)

def sphere(im, box, base, lf=0.30, df=0.34):
    """球としての立体感を持つ楕円（影→基本→ハイライトの3階調）。"""
    x0, y0, x1, y1 = box
    w, h = x1-x0, y1-y0
    ell(im, box, darken(base, df))
    ell(im, (x0, y0, x1-max(1, w//12), y1-max(1, h//9)), base)
    ell(im, (x0+w//6, y0+h//8, x0+int(w*0.62), y0+int(h*0.52)), lighten(base, lf))
    ell(im, (x0+int(w*0.20), y0+int(h*0.16), x0+int(w*0.44), y0+int(h*0.36)), lighten(base, lf+0.28))

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

def edged(im, draw_fn, oc=OUT):
    """draw_fn(色) で描く図形に 1px の内縁を付ける（体に重なる小物用）。"""
    for dx in (-1, 0, 1):
        for dy in (-1, 0, 1):
            if dx or dy:
                tmp = new(); draw_fn(tmp, oc)
                px_ = tmp.load()
                for y in range(S):
                    for x in range(S):
                        if px_[x, y][3]:
                            nx, ny = x+dx, y+dy
                            if 0 <= nx < S and 0 <= ny < S: im.putpixel((nx, ny), oc)
    draw_fn(im, None)

def feet(im, base, y=51, dx=11, w=13, h=9):
    cx = S//2
    for s in (-1, 1):
        b = (cx+s*dx-w//2, y, cx+s*dx+w//2, y+h)
        ell(im, b, darken(base, 0.25)); ell(im, (b[0], b[1], b[2]-1, b[3]-2), base)

def eye(im, cx, cy, white=(246, 247, 253, 255), iris=(38, 42, 62, 255), w=5, h=7, slant=0):
    """既存立ち絵に合わせた角ばった目。slant=1 でつり目（外側が上がる）。"""
    x0, y0 = cx - w//2, cy - h//2
    rect(im, (x0, y0, x0+w-1, y0+h-1), white)
    rect(im, (x0+1, y0+h-4, x0+w-2, y0+h-2), iris)
    px(im, x0+1, y0+1, (255, 255, 255, 255))
    if slant:
        for i in range(w//2+1):
            rect(im, (x0+i*slant if slant>0 else x0, y0, x0+i*slant if slant>0 else x0, y0), TR)

# ---- キャラ ---------------------------------------------------------------

def c_ninja():
    """忍者：濃紺の装束＋覆面＋赤い鉢巻＋額当て。手裏剣。"""
    im = new()
    NAVY = (58, 68, 104, 255); MASK = (28, 33, 54, 255)
    RED  = (188, 56, 60, 255); STEEL= (176, 186, 206, 255)
    feet(im, darken(NAVY, 0.30))
    sphere(im, (11, 17, 53, 54), NAVY)
    # 装束の合わせ目
    line(im, [(30, 44), (26, 54)], darken(NAVY, 0.45))
    line(im, [(34, 44), (39, 53)], darken(NAVY, 0.45))
    # 覆面
    ell(im, (13, 20, 51, 50), MASK)
    ell(im, (15, 22, 49, 40), lighten(MASK, 0.16))
    ell(im, (16, 36, 48, 50), darken(MASK, 0.30))
    eye(im, 25, 34, w=6, h=7); eye(im, 39, 34, w=6, h=7)
    # つり目にする（内側上を削る）
    poly(im, [(22, 31), (28, 31), (28, 32), (22, 33)], MASK)
    poly(im, [(42, 31), (36, 31), (36, 32), (42, 33)], MASK)
    # 頭巾
    ell(im, (11, 12, 53, 34), NAVY)
    ell(im, (13, 13, 49, 27), lighten(NAVY, 0.22))
    rect(im, (11, 24, 53, 30), NAVY)
    # 鉢巻
    rect(im, (12, 24, 52, 30), RED)
    rect(im, (12, 24, 52, 25), lighten(RED, 0.30))
    rect(im, (12, 29, 52, 30), darken(RED, 0.30))
    # 額当て
    rect(im, (26, 23, 38, 31), darken(STEEL, 0.40))
    rect(im, (27, 24, 37, 30), STEEL)
    rect(im, (28, 25, 36, 26), lighten(STEEL, 0.40))
    rect(im, (31, 26, 33, 29), darken(STEEL, 0.22))
    # 鉢巻のたなびき
    poly(im, [(51, 26), (62, 21), (59, 28), (63, 33), (51, 31)], RED)
    poly(im, [(51, 26), (62, 21), (60, 25), (51, 28)], lighten(RED, 0.22))
    # 手裏剣
    poly(im, [(56, 37), (58, 44), (64, 46), (58, 48), (56, 55), (54, 48), (48, 46), (54, 44)], STEEL)
    poly(im, [(56, 37), (58, 44), (56, 46), (54, 44)], lighten(STEEL, 0.45))
    poly(im, [(56, 55), (58, 48), (56, 46), (54, 48)], darken(STEEL, 0.30))
    px(im, 56, 46, MASK)
    outline(im)
    return im

def c_samurai():
    """サムライ：漆黒の甲冑＋三日月の前立て＋朱の面頬。刀を担ぐ。"""
    im = new()
    LAQ  = (66, 48, 74, 255); CRIM = (172, 46, 54, 255)
    GOLD = (230, 188, 78, 255); SKIN = (238, 208, 178, 255)
    STEEL= (202, 210, 224, 255)
    feet(im, darken(LAQ, 0.30))
    sphere(im, (11, 16, 53, 55), LAQ)
    # 胴の緋縅（下側）＋威毛の縦線
    ell(im, (12, 43, 52, 56), CRIM)
    ell(im, (13, 44, 51, 52), lighten(CRIM, 0.22))
    for x in range(16, 50, 5):
        line(im, [(x, 45), (x, 55)], darken(CRIM, 0.35))
    rect(im, (13, 41, 51, 43), GOLD)
    rect(im, (13, 41, 51, 41), lighten(GOLD, 0.35))
    # 顔
    ell(im, (19, 24, 45, 45), SKIN)
    ell(im, (21, 25, 43, 36), lighten(SKIN, 0.22))
    # 喉輪（顎の下だけ朱）
    ell(im, (24, 41, 40, 47), CRIM)
    ell(im, (25, 42, 39, 45), lighten(CRIM, 0.22))
    ell(im, (19, 24, 45, 42), SKIN)
    ell(im, (21, 25, 43, 35), lighten(SKIN, 0.20))
    # 目
    eye(im, 26, 32, iris=(58, 40, 34, 255), w=6, h=8)
    eye(im, 38, 32, iris=(58, 40, 34, 255), w=6, h=8)
    # 眉（きつめ）
    poly(im, [(21, 27), (29, 28), (29, 30), (21, 29)], (48, 36, 40, 255))
    poly(im, [(43, 27), (35, 28), (35, 30), (43, 29)], (48, 36, 40, 255))
    # 口（への字）
    line(im, [(29, 39), (32, 38)], (120, 66, 62, 255)); line(im, [(32, 38), (35, 39)], (120, 66, 62, 255))
    # 兜の鉢
    ell(im, (10, 10, 54, 33), LAQ)
    ell(im, (13, 11, 47, 26), lighten(LAQ, 0.24))
    rect(im, (10, 21, 54, 28), LAQ)
    for x in (22, 32, 42):
        line(im, [(x, 12), (x, 26)], darken(LAQ, 0.30))
    # しころ
    poly(im, [(11, 25), (4, 41), (15, 37), (17, 27)], darken(LAQ, 0.28))
    poly(im, [(53, 25), (60, 41), (49, 37), (47, 27)], darken(LAQ, 0.28))
    poly(im, [(11, 25), (6, 34), (14, 32), (16, 27)], LAQ)
    poly(im, [(53, 25), (58, 34), (50, 32), (48, 27)], LAQ)
    # 眉庇の金帯
    rect(im, (12, 23, 52, 27), GOLD)
    rect(im, (12, 23, 52, 24), lighten(GOLD, 0.40))
    rect(im, (12, 26, 52, 27), darken(GOLD, 0.35))
    # 前立て（三日月）
    poly(im, [(21, 17), (32, 4), (43, 17), (39, 17), (32, 10), (25, 17)], GOLD)
    poly(im, [(24, 16), (32, 6), (36, 11), (32, 9), (26, 16)], lighten(GOLD, 0.40))
    rect(im, (29, 15, 35, 20), GOLD); rect(im, (30, 16, 31, 19), lighten(GOLD, 0.35))
    # 刀
    poly(im, [(47, 38), (62, 14), (64, 17), (50, 41)], STEEL)
    poly(im, [(48, 38), (62, 15), (63, 16), (49, 39)], lighten(STEEL, 0.45))
    poly(im, [(44, 43), (49, 35), (52, 37), (47, 46)], (52, 40, 36, 255))
    poly(im, [(45, 43), (49, 37), (50, 38), (46, 45)], (86, 66, 54, 255))
    rect(im, (46, 35, 53, 38), GOLD)
    outline(im)
    return im

def c_hknight():
    """重騎士：全身鎧。騎士より一回り大きい暗鋼＋金の縁取り。錨を担ぐ。"""
    im = new()
    STEEL = (124, 134, 158, 255); GOLD = (214, 172, 72, 255)
    DARK  = (28, 32, 46, 255);    GLOW = (120, 190, 230, 255)
    feet(im, darken(STEEL, 0.35), y=52, dx=12, w=14, h=9)
    sphere(im, (9, 15, 55, 56), STEEL, lf=0.26, df=0.36)
    # 胴のプレート分割
    line(im, [(14, 47), (50, 47)], darken(STEEL, 0.45))
    line(im, [(32, 47), (32, 56)], darken(STEEL, 0.45))
    rect(im, (13, 43, 51, 46), GOLD)
    rect(im, (13, 43, 51, 43), lighten(GOLD, 0.40))
    rect(im, (13, 46, 51, 46), darken(GOLD, 0.35))
    # 肩当て
    for s, x0 in ((-1, 3), (1, 42)):
        ell(im, (x0, 30, x0+19, 48), darken(STEEL, 0.20))
        ell(im, (x0+1, 31, x0+17, 45), STEEL)
        ell(im, (x0+3, 32, x0+12, 39), lighten(STEEL, 0.34))
        px(im, x0+9, 43, darken(STEEL, 0.5)); px(im, x0+5, 41, darken(STEEL, 0.5))
    # 兜
    ell(im, (12, 11, 52, 43), STEEL)
    ell(im, (14, 12, 46, 31), lighten(STEEL, 0.30))
    ell(im, (17, 15, 33, 25), lighten(STEEL, 0.52))
    rect(im, (12, 26, 52, 38), STEEL)
    ell(im, (14, 30, 50, 44), darken(STEEL, 0.18))
    # T字スリット
    rect(im, (19, 26, 45, 32), DARK)
    rect(im, (29, 26, 35, 42), DARK)
    rect(im, (22, 28, 27, 30), GLOW); rect(im, (37, 28, 42, 30), GLOW)
    rect(im, (19, 25, 45, 25), darken(STEEL, 0.5))
    # 面頬のリベット
    for x in (22, 26, 38, 42): px(im, x, 36, darken(STEEL, 0.5))
    # 兜の金帯と鶏冠
    rect(im, (13, 21, 51, 24), GOLD)
    rect(im, (13, 21, 51, 21), lighten(GOLD, 0.40))
    rect(im, (13, 24, 51, 24), darken(GOLD, 0.35))
    poly(im, [(27, 12), (32, 2), (37, 12)], GOLD)
    poly(im, [(30, 11), (32, 4), (33, 11)], lighten(GOLD, 0.45))
    # 錨
    A = (200, 208, 222, 255)
    rect(im, (54, 20, 58, 50), A); rect(im, (54, 20, 55, 50), lighten(A, 0.40)); rect(im, (57, 22, 58, 50), darken(A, 0.30))
    rect(im, (48, 27, 63, 31), A); rect(im, (48, 27, 63, 28), lighten(A, 0.40)); rect(im, (48, 30, 63, 31), darken(A, 0.30))
    poly(im, [(45, 41), (56, 55), (64, 42), (61, 41), (56, 49), (49, 40)], A)
    poly(im, [(45, 41), (52, 50), (54, 49), (49, 40)], lighten(A, 0.35))
    ell(im, (52, 14, 61, 23), A); ell(im, (54, 16, 59, 21), TR)
    outline(im)
    return im

def c_cryo():
    """氷術師：淡い氷青のローブ＋毛皮の縁＋雪の結晶の飾り。氷の槍を持つ。"""
    im = new()
    ROBE = (108, 158, 208, 255); FUR = (226, 238, 250, 255)
    ICE  = (150, 224, 246, 255); DEEP = (52, 84, 138, 255)
    SKIN = (238, 214, 196, 255)
    feet(im, darken(ROBE, 0.34))
    sphere(im, (11, 17, 53, 55), ROBE)
    # ローブの裾の襞
    for x in range(16, 50, 6):
        line(im, [(x, 46), (x-1, 55)], darken(ROBE, 0.35))
    # 毛皮の襟（控えめ）
    ell(im, (16, 40, 48, 48), FUR)
    ell(im, (18, 41, 46, 45), lighten(FUR, 0.30))
    for x in range(19, 46, 5):
        px(im, x, 44, darken(FUR, 0.18)); px(im, x+2, 46, darken(FUR, 0.14))
    # 顔
    ell(im, (20, 26, 44, 44), SKIN)
    ell(im, (22, 27, 42, 36), lighten(SKIN, 0.20))
    eye(im, 26, 33, iris=(46, 108, 158, 255), w=6, h=8)
    eye(im, 38, 33, iris=(46, 108, 158, 255), w=6, h=8)
    # フード
    ell(im, (9, 10, 55, 40), DEEP)
    ell(im, (12, 11, 48, 30), lighten(DEEP, 0.26))
    ell(im, (19, 24, 45, 42), TR)               # 顔の穴を抜く
    ell(im, (20, 26, 44, 44), SKIN)
    ell(im, (22, 27, 42, 36), lighten(SKIN, 0.20))
    eye(im, 26, 33, iris=(46, 108, 158, 255), w=6, h=8)
    eye(im, 38, 33, iris=(46, 108, 158, 255), w=6, h=8)
    # フードの縁だけ細い毛皮
    for x in range(18, 47, 4):
        ell(im, (x, 23, x+3, 26), FUR)
    ell(im, (15, 27, 19, 33), FUR); ell(im, (45, 27, 49, 33), FUR)
    # 雪の結晶（フードの前立て）
    cx, cy = 32, 16
    for dx, dy in ((0, 5), (4, 2), (4, -2)):
        line(im, [(cx-dx, cy-dy), (cx+dx, cy+dy)], ICE)
    px(im, cx, cy, (255, 255, 255, 255))
    # 氷の槍
    poly(im, [(56, 20), (60, 30), (58, 46), (54, 46), (52, 30)], ICE)
    poly(im, [(56, 20), (58, 30), (57, 44), (55, 44), (55, 30)], lighten(ICE, 0.45))
    poly(im, [(58, 30), (58, 46), (56, 46)], darken(ICE, 0.30))
    ell(im, (52, 44, 60, 52), lighten(ICE, 0.20))
    outline(im)
    return im

def c_thundr():
    """雷鳴使い：紫紺の外套＋金の雷紋＋角つきの兜巾。雷の球を連れる。"""
    im = new()
    ROBE = (98, 74, 158, 255); GOLD = (250, 224, 96, 255)
    DEEP = (58, 40, 100, 255); SKIN = (236, 206, 176, 255)
    SPARK= (168, 220, 255, 255)
    feet(im, darken(ROBE, 0.34))
    sphere(im, (11, 17, 53, 55), ROBE)
    # 外套の雷紋
    poly(im, [(20, 44), (27, 44), (23, 49), (29, 49), (19, 56), (22, 50), (17, 50)], GOLD)
    poly(im, [(40, 44), (47, 44), (43, 49), (49, 49), (39, 56), (42, 50), (37, 50)], darken(GOLD, 0.25))
    # 顔
    ell(im, (20, 26, 44, 45), SKIN)
    ell(im, (22, 27, 42, 37), lighten(SKIN, 0.20))
    eye(im, 26, 33, iris=(120, 84, 40, 255), w=6, h=8)
    eye(im, 38, 33, iris=(120, 84, 40, 255), w=6, h=8)
    # 兜巾（頭巾）
    ell(im, (10, 10, 54, 36), DEEP)
    ell(im, (13, 11, 47, 28), lighten(DEEP, 0.28))
    ell(im, (19, 24, 45, 42), TR)
    ell(im, (20, 26, 44, 45), SKIN)
    ell(im, (22, 27, 42, 37), lighten(SKIN, 0.20))
    eye(im, 26, 33, iris=(120, 84, 40, 255), w=6, h=8)
    eye(im, 38, 33, iris=(120, 84, 40, 255), w=6, h=8)
    # 角（左右）
    poly(im, [(12, 22), (4, 8), (18, 16)], DEEP)
    poly(im, [(52, 22), (60, 8), (46, 16)], DEEP)
    poly(im, [(12, 21), (7, 12), (15, 17)], lighten(DEEP, 0.30))
    poly(im, [(52, 21), (57, 12), (49, 17)], lighten(DEEP, 0.18))
    # 額の雷
    poly(im, [(30, 18), (36, 18), (32, 23), (37, 23), (28, 31), (31, 24), (27, 24)], GOLD)
    poly(im, [(31, 19), (34, 19), (31, 23)], lighten(GOLD, 0.40))
    # 雷球
    ell(im, (48, 34, 62, 48), (86, 62, 140, 255))
    ell(im, (50, 36, 60, 46), GOLD)
    ell(im, (52, 38, 57, 43), lighten(GOLD, 0.45))
    line(im, [(55, 30), (53, 35)], SPARK); line(im, [(63, 40), (58, 41)], SPARK)
    line(im, [(55, 52), (56, 47)], SPARK); line(im, [(46, 42), (50, 42)], SPARK)
    outline(im)
    return im

def c_gunner():
    """銃士：三角帽＋外套＋白い襟飾り。マスケット銃を担ぐ。"""
    im = new()
    COAT = (122, 52, 62, 255); HAT = (48, 42, 60, 255)
    GOLD = (226, 186, 84, 255); LACE = (244, 240, 232, 255)
    SKIN = (238, 208, 178, 255); WOOD = (118, 76, 44, 255)
    STEEL= (172, 182, 198, 255)
    feet(im, darken(COAT, 0.40))
    sphere(im, (11, 17, 53, 55), COAT)
    # 前合わせと金ボタン
    line(im, [(32, 40), (32, 56)], darken(COAT, 0.40))
    for y in (44, 49, 54):
        px(im, 29, y, GOLD); px(im, 35, y, GOLD)
    # 襟飾り（ジャボ）
    poly(im, [(26, 38), (38, 38), (36, 48), (32, 44), (28, 48)], LACE)
    poly(im, [(28, 39), (34, 39), (33, 44), (30, 42)], lighten(LACE, 0.20))
    # 顔
    ell(im, (20, 24, 44, 43), SKIN)
    ell(im, (22, 25, 42, 35), lighten(SKIN, 0.20))
    eye(im, 26, 31, iris=(62, 92, 60, 255), w=6, h=8)
    eye(im, 38, 31, iris=(62, 92, 60, 255), w=6, h=8)
    line(im, [(29, 37), (35, 37)], (168, 118, 96, 255))
    # 三角帽（山＋反り返ったつば。両端が跳ね上がる）
    ell(im, (14, 8, 50, 26), HAT)                       # 山
    ell(im, (17, 9, 43, 20), lighten(HAT, 0.26))
    poly(im, [(2, 24), (16, 14), (32, 11), (48, 14), (62, 24),
              (54, 26), (48, 19), (32, 16), (16, 19), (10, 26)], HAT)   # 反り返ったつば
    poly(im, [(4, 24), (16, 15), (26, 12), (24, 15), (14, 19), (9, 24)], lighten(HAT, 0.22))
    poly(im, [(2, 24), (10, 26), (18, 25), (10, 27)], darken(HAT, 0.30))
    poly(im, [(62, 24), (54, 26), (46, 25), (54, 27)], darken(HAT, 0.30))
    rect(im, (16, 20, 48, 22), GOLD)
    rect(im, (16, 20, 48, 20), lighten(GOLD, 0.40))
    # 帽章と羽根
    poly(im, [(28, 13), (32, 6), (36, 13), (32, 11)], GOLD)
    poly(im, [(44, 14), (62, 2), (57, 12), (63, 11), (46, 20)], (234, 236, 242, 255))
    poly(im, [(46, 15), (58, 5), (55, 11)], (192, 198, 212, 255))
    # マスケット銃（太め）
    poly(im, [(46, 52), (60, 22), (64, 24), (50, 54)], WOOD)
    poly(im, [(47, 52), (60, 24), (62, 25), (49, 53)], lighten(WOOD, 0.30))
    poly(im, [(55, 34), (63, 14), (67, 16), (59, 36)], STEEL)
    poly(im, [(56, 34), (63, 16), (64, 17), (57, 35)], lighten(STEEL, 0.40))
    rect(im, (52, 38, 58, 43), darken(STEEL, 0.15))
    rect(im, (53, 39, 57, 42), STEEL)
    px(im, 55, 40, GOLD)
    poly(im, [(45, 52), (52, 50), (50, 57), (44, 57)], darken(WOOD, 0.25))
    outline(im)
    return im
def c_farmer():
    """農夫：麦わら帽子＋前掛け。鎌を担ぎ、麦の穂を差している。"""
    im = new()
    TUNIC= (126, 148, 84, 255); STRAW = (226, 194, 108, 255)
    APRON= (196, 176, 140, 255); SKIN = (238, 204, 164, 255)
    WOOD = (128, 88, 50, 255);   STEEL= (196, 204, 218, 255)
    WHEAT= (232, 206, 118, 255)
    feet(im, (86, 66, 44, 255))
    sphere(im, (11, 17, 53, 55), TUNIC)
    # 前掛け
    poly(im, [(22, 38), (42, 38), (46, 52), (40, 56), (24, 56), (18, 52)], APRON)
    poly(im, [(24, 39), (40, 39), (42, 47), (22, 47)], lighten(APRON, 0.22))
    line(im, [(32, 40), (32, 55)], darken(APRON, 0.25))
    # 顔（帽子の下）
    ell(im, (20, 26, 44, 45), SKIN)
    ell(im, (22, 27, 42, 36), lighten(SKIN, 0.18))
    eye(im, 26, 33, iris=(96, 66, 40, 255), w=6, h=8)
    eye(im, 38, 33, iris=(96, 66, 40, 255), w=6, h=8)
    line(im, [(29, 40), (35, 40)], (172, 122, 90, 255))
    # 麦わら帽子（広いつば＋山）
    ell(im, (4, 20, 60, 34), STRAW)
    ell(im, (7, 21, 45, 29), lighten(STRAW, 0.30))
    ell(im, (14, 10, 50, 28), STRAW)
    ell(im, (17, 11, 42, 22), lighten(STRAW, 0.34))
    for x in range(8, 58, 5):
        px(im, x, 30, darken(STRAW, 0.28))
    rect(im, (16, 22, 48, 25), (150, 106, 62, 255))          # 帽子のリボン
    rect(im, (16, 22, 48, 22), lighten((150, 106, 62, 255), 0.30))
    # 麦の穂（帽子に差す）
    line(im, [(48, 20), (56, 6)], (176, 148, 70, 255))
    for i in range(5):
        y = 8 + i*2; x = 55 - i
        px(im, x, y, WHEAT); px(im, x+2, y, WHEAT); px(im, x-2, y+1, WHEAT)
    # 鎌（体・帽子に重なるので内縁を付ける）
    def _scythe(t, oc):
        line(t, [(49, 56), (60, 22)], oc or WOOD, 3)
        if not oc: line(t, [(50, 55), (59, 25)], lighten(WOOD, 0.30))
        poly(t, [(60, 22), (46, 13), (33, 17), (45, 18), (58, 27)], oc or STEEL)
        if not oc:
            poly(t, [(58, 22), (47, 15), (39, 17), (48, 19)], lighten(STEEL, 0.40))
            poly(t, [(60, 24), (52, 20), (58, 27)], darken(STEEL, 0.28))
    edged(im, _scythe)
    outline(im)
    return im

def c_apoth():
    """調剤師：ゴーグルを額に上げた薬師。深緑の前掛けと薬瓶。"""
    im = new()
    COAT = (58, 92, 84, 255);  APRON = (196, 190, 172, 255)
    BRASS= (214, 168, 84, 255); GLASS = (146, 214, 108, 255)
    SKIN = (238, 210, 180, 255); HAIR = (86, 66, 52, 255)
    feet(im, darken(COAT, 0.35))
    sphere(im, (11, 17, 53, 55), COAT)
    # 前掛け＋ベルト
    poly(im, [(21, 40), (43, 40), (45, 54), (19, 54)], APRON)
    poly(im, [(23, 41), (41, 41), (42, 47), (22, 47)], lighten(APRON, 0.20))
    rect(im, (18, 47, 46, 50), (92, 64, 44, 255))
    rect(im, (30, 46, 35, 51), BRASS)
    # 小瓶を差したベルト
    for x in (21, 40):
        rect(im, (x, 43, x+3, 48), GLASS); px(im, x+1, 43, BRASS)
    # 顔
    ell(im, (20, 24, 44, 44), SKIN)
    ell(im, (22, 25, 42, 35), lighten(SKIN, 0.18))
    eye(im, 26, 32, iris=(72, 108, 76, 255), w=6, h=8)
    eye(im, 38, 32, iris=(72, 108, 76, 255), w=6, h=8)
    # 髪
    ell(im, (16, 12, 48, 32), HAIR)
    ell(im, (19, 13, 43, 24), lighten(HAIR, 0.24))
    ell(im, (20, 24, 44, 40), TR)
    ell(im, (20, 24, 44, 44), SKIN)
    ell(im, (22, 25, 42, 35), lighten(SKIN, 0.18))
    eye(im, 26, 32, iris=(72, 108, 76, 255), w=6, h=8)
    eye(im, 38, 32, iris=(72, 108, 76, 255), w=6, h=8)
    poly(im, [(17, 24), (22, 14), (30, 12), (24, 20), (20, 26)], HAIR)
    poly(im, [(47, 24), (42, 14), (34, 12), (40, 20), (44, 26)], HAIR)
    # ゴーグル（額に上げている）
    rect(im, (15, 18, 49, 23), (72, 54, 44, 255))
    ell(im, (18, 15, 29, 25), BRASS); ell(im, (20, 17, 27, 23), (108, 176, 200, 255))
    ell(im, (35, 15, 46, 25), BRASS); ell(im, (37, 17, 44, 23), (108, 176, 200, 255))
    px(im, 22, 19, (240, 250, 255, 255)); px(im, 39, 19, (240, 250, 255, 255))
    # 薬瓶（泡立つ緑）
    rect(im, (54, 30, 58, 36), (208, 214, 220, 255))
    poly(im, [(50, 36), (62, 36), (60, 50), (52, 50)], (208, 214, 220, 255))
    poly(im, [(52, 40), (60, 40), (59, 49), (53, 49)], GLASS)
    poly(im, [(53, 41), (56, 41), (55, 48), (54, 48)], lighten(GLASS, 0.40))
    px(im, 55, 38, GLASS); px(im, 58, 36, lighten(GLASS, 0.4)); px(im, 53, 34, GLASS)
    rect(im, (53, 28, 59, 30), BRASS)
    outline(im)
    return im

def c_shepd():
    """羊飼い：羊毛のフード＋杖と鈴。"""
    im = new()
    WOOL = (236, 228, 208, 255); TUNIC = (150, 118, 82, 255)
    GOLD = (228, 186, 76, 255);  SKIN = (240, 212, 182, 255)
    WOOD = (122, 86, 52, 255)
    feet(im, darken(TUNIC, 0.35))
    sphere(im, (11, 17, 53, 55), TUNIC)
    # 羊毛のケープ（もこもこ）
    for i, (x, y) in enumerate([(12, 34), (19, 31), (27, 30), (35, 30), (43, 31), (49, 34),
                                (14, 40), (22, 38), (30, 37), (38, 37), (46, 39)]):
        ell(im, (x, y, x+11, y+11), WOOL)
    for x, y in [(20, 33), (30, 32), (40, 33)]:
        ell(im, (x, y, x+7, y+6), lighten(WOOL, 0.35))
    # 顔
    ell(im, (21, 25, 43, 43), SKIN)
    ell(im, (23, 26, 41, 34), lighten(SKIN, 0.18))
    eye(im, 27, 32, iris=(104, 78, 50, 255), w=6, h=8)
    eye(im, 38, 32, iris=(104, 78, 50, 255), w=6, h=8)
    line(im, [(30, 38), (35, 38)], (180, 132, 104, 255))
    # 羊毛のフード
    for x, y in [(13, 14), (21, 10), (30, 8), (39, 10), (47, 14), (11, 22), (49, 22)]:
        ell(im, (x, y, x+13, y+13), WOOL)
    ell(im, (21, 24, 43, 40), TR)
    ell(im, (21, 25, 43, 43), SKIN)
    ell(im, (23, 26, 41, 34), lighten(SKIN, 0.18))
    eye(im, 27, 32, iris=(104, 78, 50, 255), w=6, h=8)
    eye(im, 38, 32, iris=(104, 78, 50, 255), w=6, h=8)
    line(im, [(30, 38), (35, 38)], (180, 132, 104, 255))
    for x, y in [(18, 13), (28, 10), (38, 12)]:
        ell(im, (x, y, x+8, y+7), lighten(WOOL, 0.35))
    # 羊の耳
    ell(im, (8, 26, 16, 32), WOOL); ell(im, (48, 26, 56, 32), WOOL)
    # 杖（右端に寄せる。体に重なるので内縁付き）
    def _crook(t, oc):
        line(t, [(57, 56), (57, 20)], oc or WOOD, 3)
        if not oc: line(t, [(56, 55), (56, 22)], lighten(WOOD, 0.30))
        poly(t, [(58, 20), (58, 12), (50, 10), (46, 16), (49, 18), (52, 14), (55, 15), (55, 20)], oc or WOOD)
        if not oc: poly(t, [(57, 19), (57, 13), (51, 12), (49, 15), (51, 16), (53, 13), (56, 14)], lighten(WOOD, 0.26))
    edged(im, _crook)
    # 鈴（杖から下げる）
    def _bell(t, oc):
        poly(t, [(45, 40), (53, 40), (55, 48), (43, 48)], oc or GOLD)
        if not oc:
            poly(t, [(46, 41), (50, 41), (51, 46), (45, 46)], lighten(GOLD, 0.40))
            poly(t, [(53, 42), (55, 48), (51, 48)], darken(GOLD, 0.28))
        rect(t, (43, 48, 55, 49), oc or darken(GOLD, 0.30))
        rect(t, (47, 50, 51, 52), oc or darken(GOLD, 0.45))
    edged(im, _bell)
    outline(im)
    return im

def c_necro():
    """死霊術師：漆黒のフード＋髑髏の面。紫に光る眼と骨の杖。"""
    im = new()
    ROBE = (48, 38, 66, 255);  DEEP = (30, 24, 46, 255)
    BONE = (226, 220, 204, 255); GLOW = (186, 110, 250, 255)
    feet(im, darken(ROBE, 0.40))
    sphere(im, (11, 17, 53, 55), ROBE)
    # 裾のぼろ
    for x in range(14, 50, 6):
        poly(im, [(x, 48), (x+3, 56), (x+6, 48)], DEEP)
    # 髑髏の面
    ell(im, (19, 25, 45, 46), BONE)
    ell(im, (21, 26, 43, 36), lighten(BONE, 0.25))
    ell(im, (23, 41, 41, 47), BONE)
    for x in range(25, 40, 3):
        line(im, [(x, 42), (x, 47)], darken(BONE, 0.35))
    line(im, [(23, 43), (41, 43)], darken(BONE, 0.35))
    # 眼窩（紫の光）
    ell(im, (23, 30, 30, 38), (26, 20, 34, 255))
    ell(im, (34, 30, 41, 38), (26, 20, 34, 255))
    ell(im, (24, 32, 28, 36), GLOW); ell(im, (35, 32, 39, 36), GLOW)
    px(im, 25, 33, (250, 230, 255, 255)); px(im, 36, 33, (250, 230, 255, 255))
    poly(im, [(31, 37), (33, 37), (32, 40)], (26, 20, 34, 255))     # 鼻孔
    # フード
    ell(im, (8, 9, 56, 40), DEEP)
    ell(im, (12, 10, 46, 27), lighten(DEEP, 0.22))
    ell(im, (18, 23, 46, 44), TR)
    ell(im, (19, 25, 45, 46), BONE)
    ell(im, (21, 26, 43, 36), lighten(BONE, 0.25))
    ell(im, (23, 41, 41, 47), BONE)
    for x in range(25, 40, 3):
        line(im, [(x, 42), (x, 47)], darken(BONE, 0.35))
    ell(im, (23, 30, 30, 38), (26, 20, 34, 255))
    ell(im, (34, 30, 41, 38), (26, 20, 34, 255))
    ell(im, (24, 32, 28, 36), GLOW); ell(im, (35, 32, 39, 36), GLOW)
    px(im, 25, 33, (250, 230, 255, 255)); px(im, 36, 33, (250, 230, 255, 255))
    poly(im, [(31, 37), (33, 37), (32, 40)], (26, 20, 34, 255))
    # フードの尖り
    poly(im, [(26, 12), (32, 2), (38, 12)], DEEP)
    poly(im, [(30, 11), (32, 4), (33, 11)], lighten(DEEP, 0.30))
    # 骨の杖＋浮かぶ闇の手
    line(im, [(56, 54), (56, 24)], BONE, 3)
    line(im, [(55, 54), (55, 26)], lighten(BONE, 0.30))
    ell(im, (51, 16, 61, 26), BONE)
    ell(im, (53, 18, 56, 21), (40, 30, 56, 255)); ell(im, (57, 18, 60, 21), (40, 30, 56, 255))
    ell(im, (52, 12, 60, 18), GLOW)
    outline(im)
    return im

def c_android():
    """ヴァルカン：灼熱ビームの自律機。金属の体＋橙に光るバイザー。"""
    im = new()
    HULL = (140, 150, 168, 255); DARKM = (54, 60, 76, 255)
    HOT  = (255, 138, 48, 255);  CORE = (255, 226, 140, 255)
    RED  = (188, 62, 48, 255)
    feet(im, darken(HULL, 0.42), y=52, dx=11, w=13, h=9)
    sphere(im, (11, 16, 53, 55), HULL)
    # 装甲の分割線とリベット
    line(im, [(13, 44), (51, 44)], darken(HULL, 0.45))
    line(im, [(32, 44), (32, 56)], darken(HULL, 0.45))
    for x in (18, 46): px(im, x, 47, darken(HULL, 0.5))
    # 胸の炉心
    ell(im, (26, 45, 38, 55), DARKM)
    ell(im, (28, 47, 36, 53), HOT)
    ell(im, (30, 48, 34, 51), CORE)
    # 頭部（バイザー）
    ell(im, (12, 12, 52, 42), DARKM)
    ell(im, (14, 13, 46, 30), lighten(DARKM, 0.30))
    rect(im, (14, 26, 50, 36), DARKM)
    poly(im, [(16, 27), (48, 27), (46, 35), (18, 35)], (18, 20, 30, 255))
    rect(im, (19, 29, 45, 33), HOT)
    rect(im, (19, 29, 45, 30), CORE)
    rect(im, (21, 30, 26, 32), (255, 255, 240, 255))
    # 天板の金属とアンテナ
    ell(im, (14, 10, 50, 26), HULL)
    ell(im, (17, 11, 43, 21), lighten(HULL, 0.34))
    rect(im, (30, 2, 34, 12), HULL); rect(im, (30, 2, 31, 12), lighten(HULL, 0.40))
    ell(im, (28, 0, 36, 7), RED); ell(im, (30, 2, 33, 5), (255, 190, 170, 255))
    # 側面の排熱口
    for y in (24, 28, 32):
        rect(im, (8, y, 12, y+2), DARKM); rect(im, (52, y, 56, y+2), DARKM)
    # 砲身（インフェルノ）
    rect(im, (50, 36, 62, 44), HULL)
    rect(im, (50, 36, 62, 38), lighten(HULL, 0.36))
    rect(im, (50, 42, 62, 44), darken(HULL, 0.32))
    rect(im, (60, 34, 64, 46), DARKM)
    ell(im, (61, 36, 66, 44), HOT); ell(im, (62, 38, 65, 42), CORE)
    outline(im)
    return im
CHARS = {'ninja': c_ninja, 'samurai': c_samurai, 'hknight': c_hknight,
         'cryo': c_cryo, 'thundr': c_thundr, 'gunner': c_gunner,
         'farmer': c_farmer, 'apoth': c_apoth, 'shepd': c_shepd,
         'necro': c_necro, 'android': c_android}

def main():
    ids = sys.argv[1:] or list(CHARS.keys())
    os.makedirs('assets', exist_ok=True)
    for i in ids:
        if i not in CHARS: print('unknown:', i); continue
        im = CHARS[i]()
        im.save('assets/%s.png' % i)
        cols = len({im.getpixel((x, y)) for y in range(S) for x in range(S) if im.getpixel((x, y))[3]})
        print('assets/%s.png' % i, im.size, '色数:', cols)

if __name__ == '__main__':
    main()
