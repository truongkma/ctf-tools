#!/usr/bin/env python2
# -*- coding: utf-8 -*-

import sys
import argparse

#位置合わせパターンの座標
alignment_pattern_array = [
[],
[6, 18],
[6, 22],
[6, 26],
[6, 30],
[6, 34],
[6, 22, 38],
[6, 24, 42],
[6, 26, 46],
[6, 28, 50],
[6, 30, 54],
[6, 32, 58],
[6, 34, 62],
[6, 26, 46, 66],
[6, 26, 48, 70],
[6, 26, 50, 74],
[6, 30, 54, 78],
[6, 30, 56, 82],
[6, 30, 58, 86],
[6, 34, 62, 90],
[6, 28, 50, 72, 94],
[6, 26, 50, 74, 98],
[6, 30, 54, 78, 102],
[6, 28, 54, 80, 106],
[6, 32, 58, 84, 110],
[6, 30, 58, 86, 114],
[6, 34, 62, 90, 118],
[6, 26, 50, 74, 98, 122],
[6, 30, 54, 78, 102, 126],
[6, 26, 52, 78, 104, 130],
[6, 30, 56, 82, 108, 134],
[6, 34, 60, 86, 112, 138],
[6, 30, 58, 86, 114, 142],
[6, 34, 62, 90, 118, 146],
[6, 30, 54, 78, 102, 126, 150],
[6, 24, 50, 76, 102, 128, 154],
[6, 28, 54, 80, 106, 132, 158],
[6, 32, 58, 84, 110, 136, 162],
[6, 26, 54, 82, 110, 138, 166],
[6, 30, 58, 86, 114, 142, 170]
]

#型番情報(version information)のテーブル(バージョン7以上)
version_information_table = [
0x07C94,
0x085BC,
0x09A99,
0x0A4D3,
0x0BBF6,
0x0C762,
0x0D847,
0x0E60D,
0x0F928,
0x10B78,
0x1145D,
0x12A17,
0x13532,
0x149A6,
0x15683,
0x168C9,
0x177EC,
0x18EC4,
0x191E1,
0x1AFAB,
0x1B08E,
0x1CC1A,
0x1D33F,
0x1ED75,
0x1F250,
0x209D5,
0x216F0,
0x228BA,
0x2379F,
0x24B0B,
0x2542E,
0x26A64,
0x27541,
0x28C69
]

#形式情報(format information)のテーブル
format_information_table = [
'000000000000000',
'000010100110111',
'000101001101110',
'000111101011001',
'001000111101011',
'001010011011100',
'001101110000101',
'001111010110010',
'010001111010110',
'010011011100001',
'010100110111000',
'010110010001111',
'011001000111101',
'011011100001010',
'011100001010011',
'011110101100100',
'100001010011011',
'100011110101100',
'100100011110101',
'100110111000010',
'101001101110000',
'101011001000111',
'101100100011110',
'101110000101001',
'110000101001101',
'110010001111010',
'110101100100011',
'110111000010100',
'111000010100110',
'111010110010001',
'111101011001000',
'111111111111111'
]

#データコード語数テーブル(M(00), L(01), H(10), Q(11))
data_code_num_table = [
[  16,   19,    9,   13],
[  28,   34,   16,   22],
[  44,   55,   26,   34],
[  64,   80,   36,   48],
[  86,  108,   46,   62],
[ 108,  136,   60,   76],
[ 124,  156,   66,   88],
[ 154,  194,   86,  110],
[ 182,  232,  100,  132],
[ 216,  274,  122,  154],
[ 254,  324,  140,  180],
[ 290,  370,  158,  206],
[ 334,  428,  180,  244],
[ 365,  461,  197,  261],
[ 415,  523,  223,  295],
[ 453,  589,  253,  325],
[ 507,  647,  283,  367],
[ 563,  721,  313,  397],
[ 627,  795,  341,  445],
[ 669,  861,  385,  485],
[ 714,  932,  406,  512],
[ 782, 1006,  442,  568],
[ 860, 1094,  464,  614],
[ 914, 1174,  514,  664],
[1000, 1276,  538,  718],
[1062, 1370,  596,  754],
[1128, 1468,  628,  808],
[1193, 1531,  661,  871],
[1267, 1631,  701,  911],
[1373, 1735,  745,  985],
[1455, 1843,  793, 1033],
[1541, 1955,  845, 1115],
[1631, 2071,  901, 1171],
[1725, 2191,  961, 1231],
[1812, 2306,  986, 1286],
[1914, 2434, 1054, 1354],
[1992, 2566, 1096, 1426],
[2102, 2702, 1142, 1502],
[2216, 2812, 1222, 1582],
[2334, 2956, 1276, 1666]
]

#RSブロック数テーブル(M(00), L(01), H(10), Q(11))
RS_block_num_table = [
[1, 1, 1, 1],
[1, 1, 1, 1],
[1, 1, 2, 2],
[2, 1, 4, 2],
[2, 1, 4, 4],
[4, 2, 4, 4],
[4, 2, 5, 6],
[4, 2, 6, 6],
[5, 2, 8, 8],
[5, 4, 8, 8],
[5, 4, 11, 8],
[8, 4, 11, 10],
[9, 4, 16, 12],
[9, 4, 16, 16],
[10, 6, 18, 12],
[10, 6, 16, 17],
[11, 6, 19, 16],
[13, 6, 21, 18],
[14, 7, 25, 21],
[16, 8, 25, 20],
[17, 8, 25, 23],
[17, 9, 34, 23],
[18, 9, 30, 25],
[20, 10, 32, 27],
[21, 12, 35, 29],
[23, 12, 37, 34],
[25, 12, 40, 34],
[26, 13, 42, 35],
[28, 14, 45, 38],
[29, 15, 48, 40],
[31, 16, 51, 43],
[33, 17, 54, 45],
[35, 18, 57, 48],
[37, 19, 60, 51],
[38, 19, 63, 53],
[40, 20, 66, 56],
[43, 21, 70, 59],
[45, 22, 74, 62],
[47, 24, 77, 65],
[49, 25, 81, 68]
]

#英数字モードのテーブル
alphanumeric_table = [
'0', '1', '2', '3', '4', '5',
'6', '7', '8', '9', 'A', 'B',
'C', 'D', 'E', 'F', 'G', 'H',
'I', 'J', 'K', 'L', 'M', 'N',
'O', 'P', 'Q', 'R', 'S', 'T',
'U', 'V', 'W', 'X', 'Y', 'Z',
' ', '$', '%', '*', '+', '-',
'.', '/', ':']

#色つきで出力
def stdoutColor(text, color):
	dic = {'red': 31, 'green': 32, 'blue': 34}
	sys.stdout.write('\x1b[1m\x1b[{0}m{1}\x1b[0m'.format(dic[color], text))

#モジュールの描画
def printModule(c):
	if c == 0:
		sys.stdout.write('\x1b[47m  \x1b[0m')
	elif c == 1:
		sys.stdout.write('\x1b[40m  \x1b[0m')
	elif c == 2:
		sys.stdout.write('\x1b[44m  \x1b[0m')
	else:
		sys.stderr.write(u'error: 不正な色です\n')
		sys.exit(1)

#QRコードのデータの描画
def showData(data):
	for y in range(len(data)):
		for x in range(len(data)):
			printModule(data[x][y])
		print ''

#位置検出パターン(finder pattern)が間違っていないかどうか
def checkFinder(data, xoffset, yoffset):
	for x in range(7):
		for y in range(7):
			if x == 0 or y == 0 or x == 6 or y == 6 or ((2 <= x <= 4) and (2 <= y <= 4)):
				if data[xoffset + x][yoffset + y] == 0:
					return False
			else:
				if data[xoffset + x][yoffset + y] == 1:
					return False
	return True

#ハミング距離算出
def hammingDistance(s1, s2):
	if len(s1) != len(s2):
		sys.stderr.write(u'error: 文字列の長さが違います\n')
		sys.exit(1)
	r = 0
	for i in range(len(s1)):
		if s1[i] != s2[i]:
			r += 1
	return r

#マスクパターン
def mask(pat, x, y):
	if pat == 0:
		return (x + y) % 2 == 0
	if pat == 1:
		return y % 2 == 0
	if pat == 2:
		return x % 3 == 0
	if pat == 3:
		return (x + y) % 3 == 0
	if pat == 4:
		return ((x // 3) + (y // 2)) % 2 == 0
	if pat == 5:
		return (x * y) % 2 + (x * y) % 3 == 0
	if pat == 6:
		return ((x * y) % 2 + (x * y) % 3) % 2 == 0
	if pat == 7:
		return ((x * y) % 3 + (x + y) % 2) % 2 == 0
	sys.stderr.write(u'error: 不正なパターンです\n')
	sys.exit(1)

#GF(2^8)のalphaの指数からベクトル表現へ変換
def index2vector(index):
	index2vector_table = [
	None, 1, 2, 4, 8, 16, 32, 64, 128, 29, 58, 116, 232, 205, 135, 19,
	38, 76, 152, 45, 90, 180, 117, 234, 201, 143, 3, 6, 12, 24, 48, 96,
	192, 157, 39, 78, 156, 37, 74, 148, 53, 106, 212, 181, 119, 238, 193, 159,
	35, 70, 140, 5, 10, 20, 40, 80, 160, 93, 186, 105, 210, 185, 111, 222,
	161, 95, 190, 97, 194, 153, 47, 94, 188, 101, 202, 137, 15, 30, 60, 120,
	240, 253, 231, 211, 187, 107, 214, 177, 127, 254, 225, 223, 163, 91, 182, 113,
	226, 217, 175, 67, 134, 17, 34, 68, 136, 13, 26, 52, 104, 208, 189, 103,
	206, 129, 31, 62, 124, 248, 237, 199, 147, 59, 118, 236, 197, 151, 51, 102,
	204, 133, 23, 46, 92, 184, 109, 218, 169, 79, 158, 33, 66, 132, 21, 42,
	84, 168, 77, 154, 41, 82, 164, 85, 170, 73, 146, 57, 114, 228, 213, 183,
	115, 230, 209, 191, 99, 198, 145, 63, 126, 252, 229, 215, 179, 123, 246, 241,
	255, 227, 219, 171, 75, 150, 49, 98, 196, 149, 55, 110, 220, 165, 87, 174,
	65, 130, 25, 50, 100, 200, 141, 7, 14, 28, 56, 112, 224, 221, 167, 83,
	166, 81, 162, 89, 178, 121, 242, 249, 239, 195, 155, 43, 86, 172, 69, 138,
	9, 18, 36, 72, 144, 61, 122, 244, 245, 247, 243, 251, 235, 203, 139, 11,
	22, 44, 88, 176, 125, 250, 233, 207, 131, 27, 54, 108, 216, 173, 71, 142
	]
	if index == None:
		return 0b00000000
	else:
		return index2vector_table[(index % 255) + 1]
#GF(2^8)ベクトル表現からalphaの指数への変換
def vector2index(v):
	vector2index_table = [
	None, 255, 1, 25, 2, 50, 26, 198, 3, 223, 51, 238, 27, 104, 199, 75,
	4, 100, 224, 14, 52, 141, 239, 129, 28, 193, 105, 248, 200, 8, 76, 113,
	5, 138, 101, 47, 225, 36, 15, 33, 53, 147, 142, 218, 240, 18, 130, 69,
	29, 181, 194, 125, 106, 39, 249, 185, 201, 154, 9, 120, 77, 228, 114, 166,
	6, 191, 139, 98, 102, 221, 48, 253, 226, 152, 37, 179, 16, 145, 34, 136,
	54, 208, 148, 206, 143, 150, 219, 189, 241, 210, 19, 92, 131, 56, 70, 64,
	30, 66, 182, 163, 195, 72, 126, 110, 107, 58, 40, 84, 250, 133, 186, 61,
	202, 94, 155, 159, 10, 21, 121, 43, 78, 212, 229, 172, 115, 243, 167, 87,
	7, 112, 192, 247, 140, 128, 99, 13, 103, 74, 222, 237, 49, 197, 254, 24,
	227, 165, 153, 119, 38, 184, 180, 124, 17, 68, 146, 217, 35, 32, 137, 46,
	55, 63, 209, 91, 149, 188, 207, 205, 144, 135, 151, 178, 220, 252, 190, 97,
	242, 86, 211, 171, 20, 42, 93, 158, 132, 60, 57, 83, 71, 109, 65, 162,
	31, 45, 67, 216, 183, 123, 164, 118, 196, 23, 73, 236, 127, 12, 111, 246,
	108, 161, 59, 82, 41, 157, 85, 170, 251, 96, 134, 177, 187, 204, 62, 90,
	203, 89, 95, 176, 156, 169, 160, 81, 11, 245, 22, 235, 122, 117, 44, 215,
	79, 174, 213, 233, 230, 231, 173, 232, 116, 214, 244, 234, 168, 80, 88, 175
	]
	return vector2index_table[v]
#GF(2^8)上での掛け算
def mulGF256(v1, v2):
	if v1 == 0b00000000 or v2 == 0b00000000:
		return 0b00000000
	else:
		return index2vector(vector2index(v1) + vector2index(v2))
#シンドロームの計算
def calcSyndrome(RS_block, index):
	s = 0b00000000 #ベクトル表現
	for i in range(len(RS_block)):
		s ^= mulGF256(RS_block[i], index2vector(index * i))
		#print index, bin(s)
	return s
#GF(2^8)を成分に持つ行列A_ijの行列式
def detGF256(A):
	if len(A) != len(A[0]):
		sys.stderr.write(u'error: 正方行列ではありません\n')
		sys.exit(1)
	size = len(A)
	if size == 1:
		return A[0][0]
	#掃き出し
	for i in range(size - 1):
		if A[i][i] == 0b00000000:
			continue
		for j in range(i + 1, size):
			if A[j][i] == 0b00000000:
				continue
			v = index2vector(vector2index(A[j][i]) - vector2index(A[i][i]))
			for k in range(size):
				A[j][k] ^= mulGF256(A[i][k], v)
	#掛ける
	s = 0b00000001
	for i in range(size):
		s = mulGF256(s, A[i][i])
	return s
#掃き出し法による連立一次方程式の計算(A:n行n+1列の拡大係数行列)
def solveSE(A):
	size = len(A)
	#掃き出し
	for i in range(size - 1):
		if A[i][i] == 0b00000000:
			continue
		for j in range(i + 1, size):
			if A[j][i] == 0b00000000:
				continue
			v = index2vector(vector2index(A[j][i]) - vector2index(A[i][i]))
			for k in range(size + 1):
				A[j][k] ^= mulGF256(A[i][k], v)
	#後退代入
	xs = []
	for i in range(size):
		x = A[-(i + 1)][-1]
		for j in range(i):
			x ^= mulGF256(xs[j], A[-(i + 1)][-2 - j])
		if A[-(i + 1)][-2 - i] == 0b00000000: #解が一意に定まらないため、誤り訂正失敗
			sys.stderr.write(u'error: 誤り訂正に失敗しました。--no-correctionオプションの仕様を検討してください\n')
			sys.exit(1)
		x = mulGF256(x, index2vector(-vector2index(A[-(i + 1)][-2 - i])))
		xs.append(x)
	xs.reverse()
	return xs
#誤り位置多項式\sigma(\alpha^{index})の計算
def calcSigma(sigmas, index):
	s = 0b00000000
	for i in range(len(sigmas)):
		s ^= mulGF256(sigmas[-1 - i], index2vector(index * i))
	s ^= index2vector(index * len(sigmas))
	return s

#メイン
if __name__ == '__main__':
	#--------------------------------前処理--------------------------------
	#コマンドライン引数解析
	parser = argparse.ArgumentParser(description = 'sqrd - Strong QR Decoder')
	parser.add_argument('-e', '--error-correction', help = u'エラー訂正レベル(1:L 0:M 3:Q 2:H)')
	parser.add_argument('-m', '--mask', help = u'マスクパターン(0〜7)')
	parser.add_argument('-n', '--no-correction', action = 'store_true', help = u'データブロックの誤り訂正をしない')
	parser.add_argument('-v', '--verbose', action = 'store_true', help = u'詳細な情報を表示')
	parser.add_argument('FILE', nargs = '?', default = '-', help = u'入力ファイル(デフォルトは標準入力)')
	args = parser.parse_args()

	#--------------------------------データ読み込み--------------------------------
	#テキストデータ読み込み
	if args.FILE == '-':
		text = sys.stdin.read()
	else:
		stream = open(args.FILE, 'r')
		text = stream.read()
		stream.close()
	lines = text.split('\n')
	width = len(lines[0])
	for i in range(width):
		if len(lines[i]) != width:
			sys.stderr.write(u'error: 入力が正方形ではありません\n')
			sys.exit(1)
	#型番(version)の計算
	if (width - 21) % 4 != 0 or width < 21 or 177 < width:
		sys.stderr.write(u'error: 辺の長さがおかしいです\n')
		sys.exit(1)
	version = (width - 21) // 4 + 1
	if args.verbose:
		print u'型番:\t{0} ({1} x {1})'.format(version, width)
	#2次元配列data[x][y]の作成
	data = []
	for i in range(width):
		data.append([])
	for line in lines:
		for i in range(len(line)):
			if line[i] in 'XxOo#1': #暗モジュール
				data[i].append(1)
			elif line[i] in '_- 0': #明モジュール
				data[i].append(0)
			elif line[i] in '?': #不明
				data[i].append(2)
			else:
				sys.stderr.write(u'error: 不正な文字が含まれています\n')
				sys.exit(1)
	#読み込んだデータの表示
	if args.verbose:
		print u'読み込んだデータ:'
		showData(data)

	#--------------------------------固定パターンのチェック--------------------------------
	#位置検出パターン(finder pattern)が間違っていないかどうか
	if checkFinder(data, 0, 0) and checkFinder(data, width - 7, 0) and checkFinder(data, 0, width - 7):
		valid_finder_pattern = True
	else:
		valid_finder_pattern = False
	if args.verbose:
		print ''
		if valid_finder_pattern:
			stdoutColor('[ OK ]', 'green')
		else:
			stdoutColor('[ NG ]', 'red')
		print u' 位置検出パターン'
	#分離パターン(separator)が間違っていないかどうか
	valid_separator = True
	for i in range(8):
		if data[i][7] == 1 or data[7][i] == 1 or data[width - 8 + i][7] == 1 or data[width - 8][i] == 1 or data[i][width - 8] == 1 or data[7][width - 8 + i] == 1:
			valid_separator = False
	if args.verbose:
		if valid_separator:
			stdoutColor('[ OK ]', 'green')
		else:
			stdoutColor('[ NG ]', 'red')
		print u' 分離パターン'
	#タイミングパターン(timing pattern)が間違っていないかどうか
	valid_timing_pattern = True
	for i in range(width - 16):
		if data[8 + i][6] == i % 2 or data[6][8 + i] == i % 2:
			valid_timing_pattern = False
	if args.verbose:
		if valid_timing_pattern:
			stdoutColor('[ OK ]', 'green')
		else:
			stdoutColor('[ NG ]', 'red')
		print u' タイミングパターン'
	#位置合わせパターン(alignment pattern)が間違っていないかどうか
	valid_alignment_pattern = True
	array = alignment_pattern_array[version - 1]
	for x in array:
		for y in array:
			if not ((x < 9 and y < 9) or (width - 10 < x and y < 9) or (x < 9 and width - 10 < y)): #位置検出パターンと重なる場合は除外する
				for i in range(-2, -2 + 5):
					for j in range(-2, -2 + 5):
						if max(abs(i), abs(j)) == 1:
							if data[x + i][y + j] == 1:
								valid_alignment_pattern = False
						else:
							if data[x + i][y + j] == 0:
								valid_alignment_pattern = False
	if args.verbose:
		if valid_alignment_pattern:
			stdoutColor('[ OK ]', 'green')
		else:
			stdoutColor('[ NG ]', 'red')
		print u' 位置合わせパターン'
	#is_data_module[x][y]の作成
	is_data_module = []
	for x in range(width):
		t = []
		for y in range(width):
			if (x <= 8 and y <= 8) or (width - 8 <= x and y <= 8) or (x <= 8 and width - 8 <= y) or x == 6 or y == 6:
				t.append(False)
			else:
				t.append(True)
		is_data_module.append(t)
	for x in array:	#位置合わせパターンを除外
		for y in array:
			if not ((x < 9 and y < 9) or (width - 10 < x and y < 9) or (x < 9 and width - 10 < y)): #位置検出パターンと重なる場合は除外する
				for i in range(-2, -2 + 5):
					for j in range(-2, -2 + 5):
						is_data_module[x + i][y + j] = False
	if 7 <= version:
		for i in range(6): #左下型番情報を除外
			for j in range(3):
				is_data_module[i][-11 + j] = False
		for j in range(6): #右上の型番情報を除外
			for i in range(3):
				is_data_module[-11 + i][j] = False

	#--------------------------------型番情報のチェック--------------------------------
	if 7 <= version:
		#左下の型番情報
		left_bottom = ''
		for i in range(6):
			for j in range(3):
				if data[i][-11 + j] == 1:
					left_bottom += '1'
				elif data[i][-11 + j] == 0:
					left_bottom += '0'
				elif data[i][-11 + j] == 2:
					left_bottom += '?'
		left_bottom = left_bottom[::-1]
		if args.verbose:
			print u'\n型番情報(左下):\t\t{0}'.format(left_bottom)
		#右上の型番情報
		right_top = ''
		for j in range(6):
			for i in range(3):
				if data[-11 + i][j] == 1:
					right_top += '1'
				elif data[-11 + i][j] == 0:
					right_top += '0'
				elif data[-11 + i][j] == 2:
					right_top += '?'
		right_top = right_top[::-1]
		if args.verbose:
			print u'型番情報(右上):\t\t{0}'.format(right_top)
		#2つの型番情報の合成
		composed = ''
		diff_format = False
		for i in range(18):
			if left_bottom[i] == '?' and right_top[i] == '?':
				composed += '?'
			elif left_bottom[i] == '?':
				composed += right_top[i]
			elif right_top[i] == '?':
				composed += left_bottom[i]
			elif left_bottom[i] == right_top[i]:
				composed += left_bottom[i]
			else:
				diff_format = True
				composed += left_bottom[i]
		if args.verbose:
			if diff_format:
				stdoutColor('[ NG ]', 'red')
			else:
				stdoutColor('[ OK ]', 'green')
			print u' 2つの型番情報の整合性'
			print u'型番情報(合成):\t\t{0}'.format(composed)
		#誤り訂正
		version_information = composed.replace('?', '0') #不明モジュールを0で埋める
		min_hamming_distance = 18
		index = -1
		for i in range(32):
			d = hammingDistance(version_information, '{0:018b}'.format(version_information_table[i]))
			if d < min_hamming_distance and d <= 3:
				index = i
		if index == -1: #誤り訂正失敗
			if args.verbose:
				stdoutColor('[ NG ]', 'red')
				print u' 型番情報の誤り訂正'
		else:
			if args.verbose:
				stdoutColor('[ OK ]', 'green')
				print u' 誤り訂正'
			version_information = '{0:018b}'.format(version_information_table[index])
			if args.verbose:
				print u'型番情報(誤り訂正後):\t{0}'.format(version_information)

	#--------------------------------形式情報のチェック--------------------------------
	#常に暗であるモジュールが間違っていないかどうか
	if data[8][4 * version + 9] == 0:
		valid_always_black = False
	else:
		valid_always_black = True
	if args.verbose:
		print ''
		if valid_always_black:
			stdoutColor('[ OK ]', 'green')
		else:
			stdoutColor('[ NG ]', 'red')
		print u' 常暗モジュール'
	#形式情報(format information)の取得
	format_mask = '101010000010010'
	#横方向の形式情報
	yoko = ''
	for i in range(15):
		if i <= 5:
			if data[i][8] == 1:
				yoko += '1'
			elif data[i][8] == 0:
				yoko += '0'
			elif data[i][8] == 2:
				yoko += '?'
		elif i == 6:
			if data[i + 1][8] == 1:
				yoko += '1'
			elif data[i + 1][8] == 0:
				yoko += '0'
			elif data[i + 1][8] == 2:
				yoko += '?'
		else:
			if data[width - 8 + i - 7][8] == 1:
				yoko += '1'
			elif data[width - 8 + i - 7][8] == 0:
				yoko += '0'
			elif data[width - 8 + i - 7][8] == 2:
				yoko += '?'
	if args.verbose:
		print u'形式情報(横):\t\t\t{0}'.format(yoko)
	#縦方向の形式情報
	tate = ''
	for i in range(15):
		if i <= 6:
			if data[8][width - 1 - i] == 1:
				tate += '1'
			elif data[8][width - 1 - i] == 0:
				tate += '0'
			elif data[8][width - 1 - i] == 2:
				tate += '?'
		elif i <= 8:
			if data[8][8 - (i - 7)] == 1:
				tate += '1'
			elif data[8][8 - (i - 7)] == 0:
				tate += '0'
			elif data[8][8 - (i - 7)] == 2:
				tate += '?'
		else:
			if data[8][5 - (i - 9)] == 1:
				tate += '1'
			elif data[8][5 - (i - 9)] == 0:
				tate += '0'
			elif data[8][5 - (i - 9)] == 2:
				tate += '?'
	if args.verbose:
		print u'形式情報(縦):\t\t\t{0}'.format(tate)
	#縦横の形式情報の合成
	composed = ''
	diff_format = False
	for i in range(15):
		if yoko[i] == '?' and tate[i] == '?':
			composed += '?'
		elif yoko[i] == '?':
			composed += tate[i]
		elif tate[i] == '?':
			composed += yoko[i]
		elif yoko[i] == tate[i]:
			composed += yoko[i]
		else:
			diff_format = True
			composed += yoko[i]
	if args.verbose:
		if diff_format:
			stdoutColor('[ NG ]', 'red')
		else:
			stdoutColor('[ OK ]', 'green')
		print u' 縦横の形式情報の整合性'
		print u'形式情報(合成):\t\t{0}'.format(composed)
	composed_unmask = ''.join(['0' if x == y else '1' if x in '01' and y in '01' else '?' for (x, y) in zip(composed, format_mask)])
	if args.verbose:
		print u'形式情報(マスク解除):\t{0}'.format(composed_unmask)
	#誤り訂正
	format_information = composed_unmask.replace('?', '0') #不明モジュールを0で埋める
	min_hamming_distance = 15
	index = -1
	for i in range(32):
		d = hammingDistance(format_information, format_information_table[i])
		if d < min_hamming_distance and d <= 3:
			index = i
	if index == -1: #誤り訂正失敗
		if args.verbose:
			stdoutColor('[ NG ]', 'red')
			print u' 形式情報の誤り訂正'
		if '?' in composed_unmask[:5] and not (args.error_correction != None and args.mask != None): #データ部が全て不明で、引数指定もなし
			sys.stderr.write(u'error: 形式情報のデータ部が不明、かつ誤り訂正に失敗しました\n')
			sys.exit(1)
		elif '?' in composed_unmask[:2] and args.error_correction == None: #エラー訂正レベルが不明で、引数指定もなし
			sys.stderr.write(u'error: 形式情報のデータ部が不明、かつ誤り訂正に失敗しました\n')
			sys.exit(1)
		elif '?' in composed_unmask[2:5] and args.mask == None: #マスクパターンが不明で、引数指定もなし
			sys.stderr.write(u'error: 形式情報のデータ部が不明、かつ誤り訂正に失敗しました\n')
			sys.exit(1)
		else: #誤り訂正には失敗したがデータ部は無事、もしくは自分で設定した
			format_information = composed_unmask
	else:
		if args.verbose:
			stdoutColor('[ OK ]', 'green')
			print u' 誤り訂正'
		format_information = format_information_table[index]
		if args.verbose:
			print u'形式情報(誤り訂正後):\t{0}'.format(format_information)
	#誤り訂正レベル(error correction level)の取得
	if args.error_correction != None:
		error_correction_level = int(args.error_correction, 0)
	else:
		error_correction_level = int(format_information[:2], 2)
	if error_correction_level == 0b01:
		m = 'L'
	if error_correction_level == 0b00:
		m = 'M'
	if error_correction_level == 0b11:
		m = 'Q'
	if error_correction_level == 0b10:
		m = 'H'
	if args.verbose:
		print u'\n誤り訂正レベル:\t{0:02b}\t({1})'.format(error_correction_level, m)
	#マスクパターン(mask pattern)の取得
	if args.mask != None:
		mask_pattern = int(args.mask, 0)
	else:
		mask_pattern = int(format_information[2:5], 2)
	if args.verbose:
		if mask_pattern == 0:
			m = '(x + y) mod 2 = 0'
		if mask_pattern == 1:
			m = 'y mod 2 = 0'
		if mask_pattern == 2:
			m = 'x mod 3 = 0'
		if mask_pattern == 3:
			m = '(x + y) mod 3 = 0'
		if mask_pattern == 4:
			m = '((x // 3) + (y // 2)) mod 2 = 0'
		if mask_pattern == 5:
			m = '(x * y) mod 2 + (x * y) mod 3 = 0'
		if mask_pattern == 6:
			m = '((x * y) mod 2 + (x * y) mod 3) mod 2 = 0'
		if mask_pattern == 7:
			m = '((x * y) mod 3 + (x + y) mod 2) mod 2 = 0'
		print u'マスクパターン:\t{0}\t[ {1} ]'.format(mask_pattern, m)

	#--------------------------------マスク解除--------------------------------
	#マスク(mask)を解除
	for y in range(width):
		for x in range(width):
			if is_data_module[x][y] and mask(mask_pattern, x, y):
				if data[x][y] == 0:
					data[x][y] = 1
				elif data[x][y] == 1:
					data[x][y] = 0
	if args.verbose:
		print u'\nマスク解除後のデータ:'
		showData(data)

	#--------------------------------コード語列読み込み--------------------------------
	#コード語列読み込み
	blocks = []
	block = ''
	count = 0
	x = width - 1
	y = width - 1
	while True:
		if x < 0 or y < 0:
			break
		if is_data_module[x][y]:
			block += '?' if data[x][y] == 2 else str(data[x][y])
			count += 1
			if count == 8:
				blocks.append(block)
				block = ''
				count = 0
		tx = x if x < 7 else x - 1 #タイミングパターンを考慮
		if tx % 2 == 1:
			x -= 1
		else:
			if (tx // 2) % 2 == 1:
				#上へ行く
				if y == 0:
					x -= 1
				else:
					y -= 1
					x += 1
			else:
				#下へ行く
				if y == width - 1:
					if (tx // 2) == 3: #縦のタイミングパターンをとばす
						x -= 1
					x -= 1
				else:
					y += 1
					x += 1
	if args.verbose:
		print u'\n総コード語数: {0}'.format(len(blocks))
		print u'データブロック: {0}'.format(repr(blocks))
	#RSブロックに分割する
	RS_blocks = []
	block_num = RS_block_num_table[version - 1][error_correction_level]
	offset = data_code_num_table[version - 1][error_correction_level]
	for i in range(block_num):
		t = []
		for j in range(offset // block_num): #データ部
			t.append(blocks[j * block_num + i])
		if offset % block_num != 0: #端数のある場合
			remain = offset % block_num
			if (block_num - remain) <= i:
				t.append(blocks[(offset // block_num) * block_num + (i - (block_num - remain))])
		for j in range((len(blocks) - offset) // block_num): #誤り訂正符号部
			t.append(blocks[offset + j * block_num + i])
		t.reverse()
		RS_blocks.append(t)
	if args.verbose:
		print u'RSブロック数:\t{0}'.format(len(RS_blocks))
		print u'RSブロック分割後:'
		for i in range(len(RS_blocks)):
			print '{0}'.format(repr(RS_blocks[i]))
	#不明モジュールを含むコードワードの数を数える
	unknown_code_nums = []
	for bs in RS_blocks:
		s = 0
		for c in bs:
			if '?' in c:
				s += 1
		unknown_code_nums.append(s)
	if args.verbose:
		print u'各RSブロック中の不明データコード数: {0}'.format(repr(unknown_code_nums))
	#不明モジュールを0で埋める
	for i in range(block_num):
		for j in range(len(RS_blocks[i])):
			RS_blocks[i][j] = int(RS_blocks[i][j].replace('?', '0'), 2)
	#誤り訂正
	# (最大)誤り訂正数を求める
	if version == 1:
		if error_correction_level == 0b01: #L
			limit_error_correction_num = 2
		elif error_correction_level == 0b00: #M
			limit_error_correction_num = 4
		elif error_correction_level == 0b11: #Q
			limit_error_correction_num = 6
		elif error_correction_level == 0b10: #H
			limit_error_correction_num = 8
	elif version == 2 and error_correction_level == 0b01:
		limit_error_correction_num = 4
	elif version == 3 and error_correction_level == 0b01:
		limit_error_correction_num = 7
	else:
		limit_error_correction_num = (len(blocks) - offset) // block_num // 2
	if args.verbose:
		print u'\n(最大)誤り訂正数: {0}'.format(limit_error_correction_num)
	for i in range(block_num): #各RSブロックについて個別に誤り訂正する
		if args.verbose:
			print u'\nRSブロック {0}'.format(i)
		#不明モジュール数が誤り訂正数を超えていた場合は訂正不能
		if limit_error_correction_num < unknown_code_nums[i]:
			if args.verbose:
				print u'不明モジュールを含むブロック数が(最大)誤り訂正数を超えています'
			continue
		#シンドロームの計算
		syndrome_length = (len(blocks) - offset) // block_num #誤り訂正数、len(syndromes)
		if args.verbose:
			print u'シンドローム数:\t{0}'.format(syndrome_length)
		syndromes = []
		for j in range(syndrome_length):
			syndromes.append(calcSyndrome(RS_blocks[i], j))
		if args.verbose:
			print u'シンドローム: {0}'.format(repr(map(hex, syndromes)))
		no_error = True
		for j in range(syndrome_length):
			if syndromes[j] != 0b00000000:
				no_error = False
		if args.verbose:
			if no_error:
				stdoutColor('[ N O ]', 'green')
			else:
				stdoutColor('[ YES ]', 'red')
			print u' 誤り訂正の必要性'
		if no_error or args.no_correction: #誤りはない
			continue #次のブロックへ
		#誤りの個数の計算
		for size in range(syndrome_length // 2 - 1, 0, -1):
			#拡大係数行列の作成
			A = []
			for j in range(size):
				row = []
				for k in range(size):
					row.append(syndromes[j + k])
				A.append(row)
			det = detGF256(A)
			if det != 0b00000000:
				break
		num_error = len(A)
		if args.verbose:
			print u'誤り個数:\t{0}'.format(num_error)
		#誤り位置変数\sigma_iの計算
		A = []
		for j in range(num_error):
			row = []
			for k in range(num_error + 1):
				row.append(syndromes[j + k])
			A.append(row)
		sigmas = solveSE(A)
		sigmas.reverse()
		if args.verbose:
			print u'誤り位置多項式の係数: {0}'.format(repr(sigmas))
		#誤り位置の計算
		indexes = []
		for j in range(len(RS_blocks[i])):
			s = calcSigma(sigmas, j)
			if s == 0b00000000:
				indexes.append(j)
		if args.verbose:
			print u'誤り位置: {0}'.format(repr(indexes))
		#誤りの大きさを求める
		A = []
		for j in range(len(indexes)):
			row = []
			for k in range(len(indexes)):
				row.append(index2vector(j * indexes[k]))
			row.append(syndromes[j])
			A.append(row)
		errors = solveSE(A)
		if args.verbose:
			print u'誤りの大きさ: {0}'.format(repr(map(lambda x: '{0:08b}'.format(x), errors)))
		#誤りを訂正する
		for j in range(len(indexes)):
			RS_blocks[i][indexes[j]] ^= errors[j]
		if args.verbose:
			print u'誤り訂正後のRSブロック: {0}'.format(repr(map(lambda x: '{0:08b}'.format(x), RS_blocks[i])))
	map(lambda xs: xs.reverse(), RS_blocks)

	#--------------------------------データ読み出し--------------------------------
	#最終的なデータバイト列の取り出し
	data_bytes = []
	for i in range(len(RS_blocks)):
		data_bytes.extend(RS_blocks[i][:offset // block_num + (1 if (block_num - (offset % block_num)) <= i else 0)])
	if args.verbose:
		print u'\n最終的なデータバイト列: {0} ({1}バイト)'.format(repr(map(hex, data_bytes)), len(data_bytes))
	data_bits = ''
	for block in data_bytes:
		data_bits += '{0:08b}'.format(block)
	if args.verbose:
		print u'最終的なデータビット列: {0}'.format(data_bits)
	#データを読み終えるまで繰り返し
	data = []
	while len(data_bits) != 0:
		#モード指示子(mode indicator)の取得
		if len(data_bits[:4]) != 4:
			print u'\n残りビット数が4ビット未満のため終了'
			break
		mode = int(data_bits[:4], 2)
		m = ''
		if mode == 0b0001:
			m = u'数字'
		elif mode == 0b0010:
			m = u'英数字'
		elif mode == 0b0100:
			m = u'8ビットバイト'
		elif mode == 0b1110:
			m = u'埋め草コード語'
		elif mode == 0b0000:
			m = u'終端パターン'
		else:
			sys.stderr.write(u'error: 未対応のモード指示子です\n')
			sys.exit(1)
		if args.verbose:
			print u'\nモード指示子:\t{0} ({1})'.format('{0:04b}'.format(mode), m)
		data_bits = data_bits[4:]
		#数字のとき
		if mode == 0b0001:
			#文字数指示子を取得
			if version <= 9:
				length_indicator_length = 10
			elif version <= 26:
				length_indicator_length = 12
			else:
				length_indicator_length = 16
			length = int(data_bits[:length_indicator_length], 2)
			data_bits = data_bits[length_indicator_length:]
			if args.verbose:
				print u'文字数:\t{0}'.format(length)
			#データを読む
			for i in range((length + 2) // 3):
				if i == (length + 2) // 3 - 1: #最後の1または2けた
					if length % 3 == 0:
						num = int(data_bits[:10], 2)
						data_bits = data_bits[10:]
						data.extend(map(ord, '{0:03d}'.format(num)))
					elif length % 3 == 1:
						num = int(data_bits[:4], 2)
						data_bits = data_bits[4:]
						data.extend(map(ord, '{0:01d}'.format(num)))
					else:
						num = int(data_bits[:7], 2)
						data_bits = data_bits[7:]
						data.extend(map(ord, '{0:02d}'.format(num)))
				else:
					num = int(data_bits[:10], 2)
					data_bits = data_bits[10:]
					data.extend(map(ord, str(num)))
			if args.verbose:
				print u'デコードされたデータ: {0}'.format(repr(map(hex, data)))
		#英数字のとき
		if mode == 0b0010:
			#文字数指示子を取得
			if version <= 9:
				length_indicator_length = 9
			elif version <= 26:
				length_indicator_length = 11
			else:
				length_indicator_length = 13
			length = int(data_bits[:length_indicator_length], 2)
			data_bits = data_bits[length_indicator_length:]
			if args.verbose:
				print u'文字数:\t{0}'.format(length)
			#データを読む
			for i in range((length + 1) // 2):
				if i == (length + 1) // 2 - 1: #最後の1または2けた
					if length % 2 == 0:
						num = int(data_bits[:11], 2)
						data_bits = data_bits[11:]
						data.extend([ord(alphanumeric_table[num // 45]), ord(alphanumeric_table[num % 45])])
					else:
						num = int(data_bits[:6], 2)
						data_bits = data_bits[6:]
						data.extend([ord(alphanumeric_table[num])])
				else:
					num = int(data_bits[:11], 2)
					data_bits = data_bits[11:]
					data.extend([ord(alphanumeric_table[num // 45]), ord(alphanumeric_table[num % 45])])
			if args.verbose:
				print u'デコードされたデータ: {0}'.format(repr(map(hex, data)))
		#8ビットバイトのとき
		if mode == 0b0100:
			#文字数指示子を取得
			if version <= 9:
				length_indicator_length = 8
			else:
				length_indicator_length = 16
			length = int(data_bits[:length_indicator_length], 2)
			data_bits = data_bits[length_indicator_length:]
			if args.verbose:
				print u'文字数:\t{0}'.format(length)
			#データを読む
			for i in range(length):
				data.append(int(data_bits[:8], 2))
				data_bits = data_bits[8:]
			if args.verbose:
				print u'デコードされたデータ: {0}'.format(repr(map(hex, data)))
		#終端パターンのとき
		if mode == 0b0000:
			break
		if args.verbose:
			print '残りのビット列: {0}'.format(data_bits)
			print 'デコード済み文字列: {0}'.format(''.join(map(chr, data)))
	if args.verbose:
		print ''
	print ''.join(map(chr, data))
	

