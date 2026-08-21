# -*- coding: utf-8 -*-
"""立ち絵の確認用シートを作る。 python3 tools/preview.py 出力先.png id1 id2 ..."""
import sys
from PIL import Image, ImageDraw, ImageFont

FONT = '/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
BG = (21, 15, 44, 255)     # ステージ1の地面色
NAMES = {'knight':'騎士(既存)','hunter':'狩人(既存)','bomber':'爆弾魔(既存)','mage':'魔道士(既存)','saint':'聖女(既存)',
         'ninja':'忍者','samurai':'サムライ','hknight':'重騎士','cryo':'氷術師','thundr':'雷鳴使い','gunner':'銃士',
         'farmer':'農夫','necro':'死霊術師','apoth':'調剤師','shepd':'羊飼い','android':'ヴァルカン'}

def sheet(out, ids, refs, title):
    Z = 5
    cell = 64*Z + 24
    cols = max(len(ids), len(refs))
    W = cell*cols + 24
    H = 64 + cell + 46 + (cell + 46 if refs else 0) + 40
    im = Image.new('RGBA', (W, H), BG)
    d = ImageDraw.Draw(im)
    f  = ImageFont.truetype(FONT, 22)
    fs = ImageFont.truetype(FONT, 18)
    fb = ImageFont.truetype(FONT, 28)
    d.text((24, 20), title, font=fb, fill=(255, 255, 255, 255))
    y = 70
    d.text((24, y), '新規（%d体）— 5倍表示 / 実寸' % len(ids), font=f, fill=(180, 220, 255, 255))
    y += 34
    for i, k in enumerate(ids):
        s = Image.open('assets/%s.png' % k).convert('RGBA')
        x = 24 + i*cell
        im.alpha_composite(s.resize((64*Z, 64*Z), Image.NEAREST), (x, y))
        im.alpha_composite(s.resize((48, 48), Image.NEAREST), (x + 64*Z - 52, y + 64*Z - 52))
        d.text((x, y + 64*Z + 6), NAMES.get(k, k), font=f, fill=(255, 255, 255, 255))
    y += cell + 30
    if refs:
        d.text((24, y), '既存の立ち絵（比較用）', font=f, fill=(160, 160, 200, 255))
        y += 34
        Z2 = 3
        for i, k in enumerate(refs):
            s = Image.open('assets/%s.png' % k).convert('RGBA')
            x = 24 + i*(64*Z2 + 24)
            im.alpha_composite(s.resize((64*Z2, 64*Z2), Image.NEAREST), (x, y))
            d.text((x, y + 64*Z2 + 6), NAMES.get(k, k), font=fs, fill=(150, 150, 180, 255))
    im.convert('RGB').save(out)
    print(out)

if __name__ == '__main__':
    out = sys.argv[1]; ids = sys.argv[2:]
    sheet(out, ids, ['knight','hunter','bomber','mage','saint'], 'キャラ立ち絵 スタイルテスト')
