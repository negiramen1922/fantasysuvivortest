#!/usr/bin/env python3
# 引き継ぎ資料 §4-2 の検証を1コマンドにまとめたもの。
# 使い方: python3 docs/check.py
import re, subprocess, sys, tempfile, os
src = 'index.html'
s = open(src, encoding='utf-8').read()
m = re.search(r'<script>(.*?)</script>', s, re.S)
if not m:
    print('NG: <script> が見つからない'); sys.exit(1)
js = m.group(1)
tmp = os.path.join(tempfile.gettempdir(), 'bsv_check.js')
open(tmp, 'w', encoding='utf-8').write(js)

# 1) 構文チェック (node --check)
r = subprocess.run(['node', '--check', tmp], capture_output=True, text=True)
if r.returncode != 0:
    print('NG: 構文エラー\n' + r.stderr); sys.exit(1)
print('OK: 構文チェック通過')

# 2) 未定義・重複の検出
defined = set(re.findall(r'\bfunction (\w+)\(', js))
called = set(re.findall(r'(?<![\w.\'"])([a-zA-Z_]\w*)\s*\(', js))
skip = {'if','for','while','switch','catch','function','return','typeof','JSON','Math',
 'Object','Array','String','Number','parseInt','parseFloat','setTimeout','clearTimeout','setInterval','clearInterval',
 'addEventListener','requestAnimationFrame','console','var','new','onHit','cv','ctx',
 'document','window','localStorage','performance','isNaN','Boolean','in'}
undef = sorted(c for c in called if c not in defined and c not in skip and c[0].islower())
dup = [f for f in defined if len(re.findall(r'^function '+f+r'\(', js, re.M)) > 1]
print('未定義:', undef or 'なし')
print('重複:', dup or 'なし')
if dup:
    print('NG: 重複定義あり（後勝ちで上書きされる事故の元）'); sys.exit(1)
print('検証完了')
