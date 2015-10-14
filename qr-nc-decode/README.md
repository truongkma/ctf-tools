strong-qr-decoder
=================

強力なQRコードデコーダ

特徴
====

- 誤り訂正に失敗しても無理やりデータ部分を読み出します
- 形式情報をの読み出しに失敗しても、エラー訂正レベルやマスクパターンを自分で設定できます
- `--verbose`オプションを使うとわりと詳細な出力が得られます

ヘルプ
======

```
% ./sqrt.py --help
usage: sqrd.py [-h] [-e ERROR_CORRECTION] [-m MASK] [-n] [-v] [FILE]

sqrd - Strong QR Decoder

positional arguments:
  FILE                  入力ファイル(デフォルトは標準入力)

optional arguments:
  -h, --help            show this help message and exit
  -e ERROR_CORRECTION, --error-correction ERROR_CORRECTION
                        エラー訂正レベル(1:L 0:M 3:Q 2:H)
  -m MASK, --mask MASK  マスクパターン(0〜7)
  -n, --no-correction   データブロックの誤り訂正をしない
  -v, --verbose         詳細な情報を表示
```

使い方
======

QRコードをテキストデータで流し込みます。

- `'X', 'x', 'O', 'o', '#', '1'`は暗モジュールとして扱われます。
- `'_', '-', ' ', '0'`は明モジュールとして扱われます。
- `'?'`は明暗が不明であるモジュールとして扱われます(マスク解除後に明モジュール扱いになります)

例
==

以下のデータを`qr.txt`として保存します。
```
XXXXXXX_X_XX_X____XXXXXXX
X_____X_XXX_XXX_X_X_____X
X_XXX_X_XX______X_X_XXX_X
X_XXX_X____X_X__X_X_XXX_X
X_XXX_X__X_XXXXX__X_XXX_X
X_____X_X__X_X_X__X_____X
XXXXXXX_X_X_X_X_X_XXXXXXX
________X__X_XX_X________
__XXX_X_X__XXX___XXX__XXX
XX_XX__X__X__X_XXX_X__X__
X___X_X_X_XX__X__XXX___XX
XX_X_X__X_XXX_____X____XX
_X_X__XXX__X_X_X_XX_X_X_X
X_X_______XXXX_XX__X_X___
X_XX__X_X_XXX_X___X__X_XX
X_X_____XX_XX___XXXX___X_
X_X_X_X_X_X___X_XXXXXXX_X
________XX_X_X__X___X_XX_
XXXXXXX____X__XXX_X_XX_XX
X_____X__X_X_X_XX___X__X_
X_XXX_X_X_XXXXXXXXXXXXX__
X_XXX_X_X__XXX____X_X___X
X_XXX_X_X__X_X_X__XX____X
X_____X___X_XX_X_X_XX___X
XXXXXXX____X__X_X__XX__XX
```
実行するとデコード結果が表示されます。
```
% ./sqrd qr.txt
sample_data
```
