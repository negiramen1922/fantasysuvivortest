# -*- coding: utf-8 -*-
"""敵立ち絵の確認シート。 python3 tools/preview_enemy.py 出力.png id1 id2 ...
   背景はステージ③の地面タイル。下段に既存の敵を並べて比較する。"""
import sys
from PIL import Image, ImageDraw, ImageFont
F='/usr/share/fonts/opentype/ipafont-gothic/ipag.ttf'
NM={'lich':'リッチ','necro':'ネクロマンサー','dullahan':'デュラハン','boomer':'ブーマー',
    'gargoyle':'ガーゴイル','sarcher':'スケルトンアーチャー','fly':'フライ','gnat':'スウォームナット',
    'skeleton':'スケルトン(既存)','wraith':'レイス(既存)','ghoul':'グール(既存)','mummy':'ミイラ(既存)',
    'shieldman':'盾の戦士(既存)','shadow':'シャドウ(既存)','panther':'パンサー(既存)','spider':'スパイダー(既存)',
    'sahagin':'サハギン','crab':'カニ','jelly':'クラゲ','kelpie':'ケルピー','serpent':'ミズチ','siren':'セイレーン',
    'shark':'サメ','manta':'マンタ','hermit':'ヤドカリ','clam':'カイ','flyingfish':'トビウオ','umibozu':'海坊主',
    'icewolf':'氷狼','yeti':'雪男','icegolem':'アイスゴーレム','icicle':'氷柱','snowworm':'スノーワーム',
    'wisp':'フロストウィスプ','snowman':'雪だるま','snowmanS':'小雪だるま','icearcher':'氷の弓兵',
    'walrus':'セイウチ','flurry':'吹雪の精','wolf':'ウルフ(既存)','ogre':'オーガ(既存)'}
def sheet(out, ids, refs, tile='assets/bg_s3.png', title='敵の立ち絵'):
    Z=5; cell=64*Z+22
    cols=max(len(ids),len(refs)); W=cell*cols+24
    H=70+cell+40+(64*3+40+40 if refs else 0)
    bg=Image.open(tile).convert('RGBA')
    im=Image.new('RGBA',(W,H))
    for y in range(0,H,bg.height):
        for x in range(0,W,bg.width): im.paste(bg,(x,y))
    d=ImageDraw.Draw(im)
    d.rectangle((0,0,W,58),fill=(14,10,26,235))
    f=ImageFont.truetype(F,21); fs=ImageFont.truetype(F,16); fb=ImageFont.truetype(F,28)
    d.text((22,16),title,font=fb,fill=(255,255,255))
    y=70
    for i,k in enumerate(ids):
        s=Image.open('assets/%s.png'%k).convert('RGBA')
        x=22+i*cell
        im.alpha_composite(s.resize((64*Z,64*Z),Image.NEAREST),(x,y))
        im.alpha_composite(s.resize((56,56),Image.NEAREST),(x+64*Z-58,y+64*Z-58))
        d.rectangle((x-2,y+64*Z+2,x+64*Z,y+64*Z+26),fill=(14,10,26,220))
        d.text((x,y+64*Z+4),NM.get(k,k),font=f,fill=(255,255,255))
    if refs:
        y+=cell+22
        d.rectangle((0,y-6,W,y+64*3+34),fill=(14,10,26,215))
        d.text((22,y),'既存の敵（比較用）',font=f,fill=(170,170,200)); y+=28
        for i,k in enumerate(refs):
            s=Image.open('assets/%s.png'%k).convert('RGBA')
            x=22+i*(64*3+18)
            im.alpha_composite(s.resize((64*3,64*3),Image.NEAREST),(x,y))
            d.text((x,y+64*3+2),NM.get(k,k),font=fs,fill=(150,150,180))
    im.convert('RGB').save(out); print(out)
if __name__=='__main__':
    sheet(sys.argv[1], sys.argv[2:], ['skeleton','wraith','ghoul','mummy','shieldman','shadow'])
