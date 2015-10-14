#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import zlib


class PNGWrongHeaderError(Exception):
    """Výjimka oznamující, že načítaný soubor zřejmě není PNG-obrázkem."""
    pass


class PNGNotImplementedError(Exception):
    """Výjimka oznamující, že PNG-obrázek má strukturu, kterou neumíme zpracovat."""
    pass


class PngReader():
    """Třída pro práci s PNG-obrázky."""
    
    def __init__(self, filepath):
        with open(filepath, mode='rb') as f:
            self.png_source = f.read()

        #check if the file is PNG
        if self.png_source[:8] != b'\x89\x50\x4e\x47\x0d\x0a\x1a\x0a':
            raise PNGWrongHeaderError()

        self._read_png()
        self._find_IHDR()
        self._find_IDAT()
        self._filtering()

    def _read_png(self):
        pointer = 8
        self.chunks = []
        while pointer < len(self.png_source):
            h = self.png_source[pointer:pointer+4]
            chunk_size = h[0] * 256 ** 3 + h[1] * 256 ** 2 + h[2] * 256 + h[3]
            self.chunks += [{'type': self.png_source[pointer + 4:pointer + 8],
                             'data': self.png_source[pointer + 8: pointer + 8 + chunk_size]}]
            pointer += 12 + chunk_size

    def _find_IHDR(self):
        for chunk in self.chunks:
            if chunk['type'] == b'IHDR':
                if chunk['data'][8:13] != b'\x08\x02\x00\x00\x00':
                    raise PNGNotImplementedError()
                h = chunk['data'][:4]
                self.width = h[0] * 256 ** 3 + h[1] * 256 ** 2 + h[2] * 256 + h[3]
                h = chunk['data'][4:8]
                self.height = h[0] * 256 ** 3 + h[1] * 256 ** 2 + h[2] * 256 + h[3]
            break

    def _find_IDAT(self):
        self.png_data = b''
        for chunk in self.chunks:
            if chunk['type'] == b'IDAT':
                self.png_data += chunk['data']
        self.png_data = zlib.decompress(self.png_data)

    def _add_triplet(self, a, b):
        return (a[0] + b[0]) % 256, (a[1] + b[1]) % 256, (a[2] + b[2]) % 256

    def _average_triplet(self, a, b, c):
        return a[0] + int((b[0] + c[0])/2), a[1] + int((b[1] + c[1])/2), a[2] + int((b[2] + c[2])/2)

    def _paeth(self, a, b, c):
        ret = tuple()
        for i in range(3):

            p = a[i] + b[i] - c[i]
            pa = abs(p - a[i])
            pb = abs(p - b[i])
            pc = abs(p - c[i])
            if pa <= pb and pa <= pc:
                ret += (a[i],)
            elif pb <= pc:
                ret += (b[i],)
            else:
                ret += (c[i],)
        return ret

    def _filtering(self):
        self.rgb = []
        pointer = 0
        for row in range(self.height):
            filter = self.png_data[pointer]
            pointer += 1
            row_array = []
            left_pixel = (0, 0, 0)
            up_left_pixel = (0, 0, 0)
            for column in range(self.width):
                pixel = (self.png_data[pointer], self.png_data[pointer + 1], self.png_data[pointer + 2])
                pointer += 3
                if filter == 0:
                    left_pixel = pixel
                    row_array += [pixel]
                elif filter == 1:
                    left_pixel = self._add_triplet(pixel, left_pixel)
                    row_array += [left_pixel]
                elif filter == 2:
                    left_pixel = self._add_triplet(pixel, self.rgb[row - 1][column])
                    row_array += [left_pixel]
                elif filter == 3:
                    left_pixel = self._average_triplet(pixel, left_pixel, self.rgb[row - 1][column])
                    row_array += [left_pixel]
                elif filter == 4:
                    up_pixel = self.rgb[row - 1][column]
                    current_pixel = self._add_triplet(pixel, self._paeth(left_pixel, up_pixel, up_left_pixel))
                    left_pixel = current_pixel
                    up_left_pixel = up_pixel
                    row_array += [current_pixel]

            self.rgb += [row_array]

if __name__ == "__main__":
    x = PngReader(filepath="test_data/sachovnice.png")
    for line in x.rgb:
        for pixel in line:
            print(pixel)