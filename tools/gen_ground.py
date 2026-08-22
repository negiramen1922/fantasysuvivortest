# -*- coding: utf-8 -*-
"""ステージ地面のタイル（64x64・シームレス）と散らし物シート（128x32＝32px×4種）を作る。
   python3 tools/gen_ground.py [s1 s2 s3 s4 s5]
方針：
  - 弾やエフェクトの視認性を落とさないよう、地面は暗く低コントラストに保つ（明度差は±10%程度）
  - タイルは上下左右がつながるよう、各図形を 9 方向にずらして描いてから中央を切り出す
  - 散らし物は 32x32 の4種。ゲーム側が座標ハッシュで種類と位置を決めて置く
"""
import os, sys, random
from PIL import Image, ImageDraw

T = 128         # タイル1辺（64だと繰り返しが格子状に見えたので128に）
P = 32          # 散らし物1つ
OUT = (19, 19, 19, 255)

def mix(c, t, f):
    return tuple(int(c[i] + (t[i]-c[i])*f) for i in range(3)) + (255,)
def lighten(c, f): return mix(c, (255,255,255,255), f)
def darken(c, f):  return mix(c, (0,0,0,255), f)

def wrap(im, fn):
    """fn(draw, ox, oy) を 9 方向に描いてタイルの継ぎ目を無くす。"""
    big = Image.new('RGBA', (T*3, T*3), (0,0,0,0))
    d = ImageDraw.Draw(big)
    for oy in (0, T, T*2):
        for ox in (0, T, T*2):
            fn(d, ox, oy)
    im.alpha_composite(big.crop((T, T, T*2, T*2)))

# ---------- 地面タイル ----------

def tile_s1(seed=1):
    """草原：夜の草地。短い草の筋と小さな花。"""
    rnd = random.Random(seed)
    base = (26, 20, 52, 255)
    im = Image.new('RGBA', (T, T), base)
    d = ImageDraw.Draw(im)
    for i in range(560):                                   # ざらつき
        x, y = rnd.randrange(T), rnd.randrange(T)
        d.point((x, y), lighten(base, rnd.choice([0.05, 0.08, 0.12])))
    blades = [(rnd.randrange(T), rnd.randrange(T), rnd.choice([-1,1]), rnd.randint(2,4)) for _ in range(52)]
    def f(d2, ox, oy):
        for x, y, s, h in blades:
            g = (34, 46, 46, 255)
            d2.line([(ox+x, oy+y), (ox+x+s, oy+y-h)], fill=g)
            d2.point((ox+x+s, oy+y-h), lighten(g, 0.18))
    wrap(im, f)
    fl = [(rnd.randrange(T), rnd.randrange(T)) for _ in range(12)]
    def f2(d2, ox, oy):
        for x, y in fl:
            d2.point((ox+x, oy+y), (110, 96, 160, 255))
    wrap(im, f2)
    return im

def tile_s2(seed=2):
    """森：下草と落ち葉、根。"""
    rnd = random.Random(seed)
    base = (18, 36, 24, 255)
    im = Image.new('RGBA', (T, T), base)
    d = ImageDraw.Draw(im)
    for i in range(640):
        x, y = rnd.randrange(T), rnd.randrange(T)
        d.point((x, y), rnd.choice([lighten(base, 0.07), darken(base, 0.15), lighten(base, 0.12)]))
    leaves = [(rnd.randrange(T), rnd.randrange(T), rnd.randrange(2, 4)) for _ in range(36)]
    roots  = [(rnd.randrange(T), rnd.randrange(T), rnd.randrange(8, 14), rnd.choice([-1, 1])) for _ in range(16)]
    def f(d2, ox, oy):
        for x, y, w in leaves:
            c = rnd.choice([(32, 50, 30, 255), (38, 48, 28, 255), (26, 44, 32, 255)])
            d2.ellipse((ox+x, oy+y, ox+x+w, oy+y+w-1), fill=c)
        for x, y, L, s in roots:
            d2.line([(ox+x, oy+y), (ox+x+L, oy+y+s*3)], fill=(30, 40, 26, 255), width=2)
            d2.line([(ox+x, oy+y-1), (ox+x+L, oy+y+s*3-1)], fill=(38, 48, 30, 255))
    wrap(im, f)
    return im

def tile_s3(seed=3):
    """古代の王墓：石畳。目地と欠け。"""
    rnd = random.Random(seed)
    base = (40, 34, 24, 255)
    im = Image.new('RGBA', (T, T), base)
    d = ImageDraw.Draw(im)
    # 32px の石畳を目地でくぎる（互い違い）
    for gy in range(0, T, 32):
        for gx in range(0, T, 32):
            off = 16 if (gy // 32) % 2 else 0
            x0 = (gx + off) % T
            c = lighten(base, rnd.choice([0.02, 0.045, 0.07]))
            d.rectangle((x0+1, gy+1, x0+30, gy+30), fill=c)
            if x0 + 30 >= T:                                    # 右端は左へ回り込む
                d.rectangle((x0-T+1, gy+1, x0-T+30, gy+30), fill=c)
            d.line([(x0+1, gy+1), (x0+29, gy+1)], fill=lighten(c, 0.07))
            d.line([(x0+1, gy+29), (x0+29, gy+29)], fill=darken(c, 0.16))
    for i in range(480):
        x, y = rnd.randrange(T), rnd.randrange(T)
        d.point((x, y), rnd.choice([lighten(base, 0.12), darken(base, 0.20)]))
    cr = [(rnd.randrange(T), rnd.randrange(T), rnd.randrange(4, 9), rnd.choice([-1, 1])) for _ in range(16)]
    def f(d2, ox, oy):
        for x, y, L, s in cr:
            d2.line([(ox+x, oy+y), (ox+x+L, oy+y+s*2)], fill=darken(base, 0.35))
    wrap(im, f)
    return im

def tile_s4(seed=4):
    """大海原：波紋とうねり。"""
    rnd = random.Random(seed)
    base = (14, 30, 46, 255)
    im = Image.new('RGBA', (T, T), base)
    d = ImageDraw.Draw(im)
    for i in range(880):                                        # 深さのゆらぎ
        x, y = rnd.randrange(T), rnd.randrange(T)
        d.point((x, y), rnd.choice([lighten(base, 0.05), darken(base, 0.10), lighten(base, 0.09)]))
    waves = [(rnd.randrange(T), rnd.randrange(T), rnd.randrange(9, 18)) for _ in range(22)]
    def f(d2, ox, oy):
        for x, y, w in waves:
            d2.arc((ox+x, oy+y, ox+x+w, oy+y+max(5, w//2)), 195, 345, fill=lighten(base, 0.11))
            d2.arc((ox+x+3, oy+y+4, ox+x+w-3, oy+y+max(5, w//2)+3), 200, 340, fill=lighten(base, 0.06))
    wrap(im, f)
    for i in range(90):                                         # 泡のきらめき
        x, y = rnd.randrange(T), rnd.randrange(T)
        d.point((x, y), lighten(base, 0.24))
    return im

def tile_s5(seed=5):
    """凍てつく氷河：踏み固められた雪と、うっすら透ける氷の割れ目。
       氷結床（青白い板）を上に重ねるので、地面側は青みを抑えて暗くしておく。"""
    rnd = random.Random(seed)
    base = (32, 38, 54, 255)
    im = Image.new('RGBA', (T, T), base)
    d = ImageDraw.Draw(im)
    for i in range(900):                                        # 雪面のざらつき
        x, y = rnd.randrange(T), rnd.randrange(T)
        d.point((x, y), rnd.choice([lighten(base, 0.06), lighten(base, 0.10), darken(base, 0.12)]))
    # 吹きだまりの筋（風向きに沿った横長のうねり）
    drifts = [(rnd.randrange(T), rnd.randrange(T), rnd.randrange(14, 26)) for _ in range(20)]
    def f(d2, ox, oy):
        for x, y, w in drifts:
            d2.arc((ox+x, oy+y, ox+x+w, oy+y+6), 190, 350, fill=lighten(base, 0.13))
            d2.arc((ox+x+2, oy+y+2, ox+x+w-2, oy+y+7), 195, 345, fill=darken(base, 0.10))
    wrap(im, f)
    # 氷の割れ目（折れ線）
    cracks = []
    for _ in range(10):
        x, y = rnd.randrange(T), rnd.randrange(T)
        seg = [(x, y)]
        for k in range(3):
            x += rnd.randint(-9, 9); y += rnd.randint(-9, 9)
            seg.append((x, y))
        cracks.append(seg)
    def f2(d2, ox, oy):
        for seg in cracks:
            d2.line([(ox+a, oy+b) for a, b in seg], fill=lighten(base, 0.16))
    wrap(im, f2)
    for i in range(120):                                        # 雪のきらめき
        x, y = rnd.randrange(T), rnd.randrange(T)
        d.point((x, y), lighten(base, 0.30))
    return im

# ---------- 散らし物 ----------

def props_s1():
    """草原：岩・草の束・小花・切り株。"""
    sh = Image.new('RGBA', (P*4, P), (0,0,0,0)); d = ImageDraw.Draw(sh)
    # 岩
    d.polygon([(8,24),(11,14),(18,11),(24,17),(23,24)], fill=(64,60,86,255))
    d.polygon([(11,15),(17,12),(21,16),(14,18)], fill=(88,84,116,255))
    # 草の束
    for i, (x, h, s) in enumerate([(38,10,-1),(42,13,0),(46,11,1),(34,8,-1),(50,8,1)]):
        d.line([(x,26),(x+s*2,26-h)], fill=(48,78,52,255), width=2)
        d.point((x+s*2,26-h), (72,106,68,255))
    # 小花
    d.line([(76,26),(76,18)], fill=(52,80,56,255))
    d.ellipse((73,13,79,19), fill=(150,132,196,255)); d.point((76,16),(230,220,255,255))
    d.line([(84,26),(84,20)], fill=(52,80,56,255)); d.ellipse((82,17,86,21), fill=(120,104,168,255))
    # 切り株
    d.rectangle((105,17,120,26), fill=(58,44,32,255))
    d.ellipse((104,13,121,20), fill=(86,64,44,255))
    d.ellipse((108,15,117,19), fill=(112,86,58,255))
    d.ellipse((111,16,114,18), fill=(74,56,38,255))
    return sh

def props_s2():
    """森：きのこ・シダ・倒木・苔石。"""
    sh = Image.new('RGBA', (P*4, P), (0,0,0,0)); d = ImageDraw.Draw(sh)
    d.rectangle((14,18,17,26), fill=(198,190,164,255))
    d.ellipse((7,10,24,20), fill=(140,52,52,255)); d.ellipse((10,12,17,16), fill=(184,80,72,255))
    for p in [(11,14),(19,15),(15,11)]: d.point(p, (232,220,200,255))
    for i, (x, s) in enumerate([(46,-1),(46,1)]):
        d.line([(46,27),(46,12)], fill=(44,74,42,255), width=2)
        for k in range(5):
            y = 14 + k*3
            d.line([(46,y),(46+s*(7-k),y-2)], fill=(58,96,54,255))
    d.rectangle((70,18,92,25), fill=(62,48,32,255))
    d.rectangle((70,18,92,19), fill=(84,66,44,255))
    d.ellipse((88,17,95,26), fill=(96,76,50,255)); d.ellipse((90,19,93,24), fill=(64,50,34,255))
    for x in range(72, 90, 5): d.ellipse((x,16,x+4,19), fill=(58,92,54,255))
    d.ellipse((104,14,124,27), fill=(58,58,70,255))
    d.ellipse((107,16,118,22), fill=(78,80,94,255))
    for x, y in [(106,15),(114,14),(120,18),(110,13)]: d.ellipse((x,y,x+5,y+3), fill=(52,88,52,255))
    return sh

def props_s3():
    """王墓：骨・壺・墓石・砂だまり。"""
    sh = Image.new('RGBA', (P*4, P), (0,0,0,0)); d = ImageDraw.Draw(sh)
    d.line([(9,22),(23,17)], fill=(206,198,176,255), width=3)
    for p in [(8,20),(8,24),(23,15),(23,19)]: d.ellipse((p[0]-2,p[1]-2,p[0]+2,p[1]+2), fill=(224,216,196,255))
    d.line([(11,25),(21,22)], fill=(180,172,152,255), width=2)
    d.polygon([(40,26),(38,16),(42,12),(50,12),(54,16),(52,26)], fill=(96,68,44,255))
    d.polygon([(41,16),(44,13),(48,13),(43,20)], fill=(126,92,58,255))
    d.rectangle((38,10,54,13), fill=(74,52,34,255))
    d.rectangle((44,18,50,22), fill=(150,120,70,255))
    d.polygon([(70,27),(70,12),(74,8),(84,8),(88,12),(88,27)], fill=(72,70,78,255))
    d.polygon([(72,13),(75,10),(82,10),(78,16)], fill=(96,94,104,255))
    d.rectangle((75,15,83,17), fill=(52,50,58,255)); d.rectangle((78,15,80,22), fill=(52,50,58,255))
    d.ellipse((100,18,126,27), fill=(72,62,42,255))
    d.ellipse((104,19,120,24), fill=(96,84,56,255))
    for x in range(103, 124, 4): d.point((x, 21), (120,106,70,255))
    return sh

def props_s4():
    """海：珊瑚・貝殻・海藻・泡。"""
    sh = Image.new('RGBA', (P*4, P), (0,0,0,0)); d = ImageDraw.Draw(sh)
    d.line([(16,27),(16,16)], fill=(150,70,86,255), width=3)
    d.line([(16,20),(9,12)], fill=(150,70,86,255), width=2)
    d.line([(16,18),(23,11)], fill=(150,70,86,255), width=2)
    for p in [(9,11),(23,10),(16,14)]: d.ellipse((p[0]-2,p[1]-2,p[0]+2,p[1]+2), fill=(190,96,110,255))
    d.polygon([(48,26),(38,20),(40,13),(48,10),(56,13),(58,20)], fill=(196,182,196,255))
    for i, x in enumerate([42,46,50,54]):
        d.line([(48,25),(x,12)], fill=(150,138,158,255))
    d.ellipse((44,22,52,27), fill=(214,204,214,255))
    for x, s in [(74,-1),(80,1),(86,-1)]:
        for k in range(6):
            y = 27 - k*3
            d.line([(x+s*(k%2)*2, y), (x+s*((k+1)%2)*2, y-3)], fill=(48,110,88,255), width=2)
    for cx, cy, r in [(106,20,4),(116,14,3),(112,24,2),(120,22,3)]:
        d.ellipse((cx-r,cy-r,cx+r,cy+r), outline=(120,190,210,255))
        d.point((cx-r//2, cy-r//2), (200,240,250,255))
    return sh

def props_s5():
    """氷河：氷柱の束・凍った枯木・雪だまり・凍った岩。"""
    sh = Image.new('RGBA', (P*4, P), (0,0,0,0)); d = ImageDraw.Draw(sh)
    # 氷柱の束（地面から生えた氷）
    for x, h, w in [(12, 16, 3), (17, 22, 4), (23, 13, 3)]:
        d.polygon([(x-w, 27), (x+w, 27), (x, 27-h)], fill=(120, 168, 200, 255))
        d.polygon([(x-1, 26), (x+w-1, 26), (x, 29-h)], fill=(168, 210, 232, 255))
        d.point((x, 29-h), (226, 244, 252, 255))
    d.ellipse((6, 25, 28, 29), fill=(150, 178, 200, 255))
    # 凍った枯木
    d.line([(46, 28), (46, 12)], fill=(58, 54, 62, 255), width=3)
    for x2, y2 in [(38, 14), (54, 12), (40, 20), (53, 19)]:
        d.line([(46, y2 + 4), (x2, y2)], fill=(58, 54, 62, 255), width=2)
        d.point((x2, y2), (150, 186, 208, 255))
    for p in [(46, 13), (43, 16), (49, 15)]:
        d.point(p, (192, 220, 236, 255))
    d.ellipse((38, 26, 54, 30), fill=(150, 178, 200, 255))
    # 雪だまり
    d.polygon([(68, 28), (72, 20), (80, 16), (89, 20), (92, 28)], fill=(158, 182, 204, 255))
    d.polygon([(73, 24), (80, 19), (86, 23), (80, 26)], fill=(198, 216, 232, 255))
    for p in [(76, 22), (84, 24), (80, 21)]:
        d.point(p, (232, 244, 252, 255))
    # 凍った岩（岩の上に雪が乗っている）
    d.polygon([(104, 27), (106, 17), (114, 13), (122, 18), (124, 27)], fill=(60, 62, 80, 255))
    d.polygon([(107, 17), (114, 14), (120, 18), (112, 20)], fill=(84, 88, 108, 255))
    d.polygon([(106, 16), (114, 12), (121, 17), (114, 17)], fill=(190, 210, 228, 255))
    d.point((114, 14), (232, 244, 252, 255))
    return sh

TILES = {'s1': tile_s1, 's2': tile_s2, 's3': tile_s3, 's4': tile_s4, 's5': tile_s5}
PROPS = {'s1': props_s1, 's2': props_s2, 's3': props_s3, 's4': props_s4, 's5': props_s5}

def main():
    ks = sys.argv[1:] or list(TILES.keys())
    os.makedirs('assets', exist_ok=True)
    for k in ks:
        TILES[k]().save('assets/bg_%s.png' % k)
        PROPS[k]().save('assets/prop_%s.png' % k)
        print('assets/bg_%s.png / assets/prop_%s.png' % (k, k))

if __name__ == '__main__':
    main()
