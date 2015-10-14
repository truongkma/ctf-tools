#!/usr/bin/env python3
# -*- coding: utf-8 -*-


# import modulu zodpovědného za testy jednotek
import unittest

# import testovaných modulů
import brainx
import image_png



#
# třída s dočasným „falešným“ výstupem
#

import sys

class FakeStdOut:
    def write(self, *args, **kwargs):
        pass
    def flush(self):
        pass



#
# třídy obsahující testy
#

class TestBrainfuck(unittest.TestCase):
    """testuje chování interpretru brainfucku"""
    
    def setUp(self):
        self.BF = brainx.BrainFuck
        # skrytí výstupu
        self.out = sys.stdout
        sys.stdout = FakeStdOut()
    
    def tearDown(self):
        sys.stdout = self.out
   
    def test_bf_01(self):
        """vynulování aktuální, ale pouze aktuální, buňky"""
        program = self.BF('[-]', memory=b'\x03\x02', memory_pointer=1)
        self.assertEqual(program.get_memory(), b'\x03\x00')
    
    def test_bf_02(self):
        """vynulování všech nenulových buněk doleva"""
        program = self.BF('[[-]<]', memory=b'\x03\x03\x00\x02\x02', memory_pointer=4)
        self.assertEqual(program.get_memory(), b'\x03\x03\x00\x00\x00')
    
    def test_bf_03(self):
        """přesun na první nenulovou buňku doleva"""
        program = self.BF('[<]', memory=b'\x03\x03\x00\x02\x02', memory_pointer=4)
        self.assertEqual(program.memory_pointer, 2)
    
    def test_bf_04(self):
        """přesun na první nenulovou buňku doprava"""
        program = self.BF('[>]', memory=b'\x03\x03\x00\x02\x02')
        self.assertEqual(program.memory_pointer, 2)
    
    def test_bf_05(self):
        """destruktivní přičtení aktuální buňky k buňce následující"""
        program = self.BF('[>+<-]', memory=b'\x03\x03')
        self.assertEqual(program.get_memory(), b'\x00\x06')
    
    def test_bf_06(self):
        """nedestruktivní přičtení aktuální buňky k buňce následující"""
        program = self.BF('[>+>+<<-]>>[<<+>>-]', memory=b'\x03\x03')
        self.assertEqual(program.get_memory(), b'\x03\x06\x00')
    
    def test_bf_07(self):
        """destruktivní odečtení aktuální buňky od buňky následující"""
        program = self.BF('[>-<-]', memory=b'\x03\x05')
        self.assertEqual(program.get_memory(), b'\x00\x02')
    
    def test_bf_11(self):
        r"""HelloWorld s \n"""
        with open( 'test_data/hello1.b', encoding='ascii' ) as stream:
            data = stream.read()
        program = self.BF(data)
        self.assertEqual(program.output, 'Hello World!\n')
    
    def test_bf_12(self):
        r"""HelloWorld bez \n"""
        with open( 'test_data/hello2.b', encoding='ascii' ) as stream:
            data = stream.read()
        program = self.BF(data)
        self.assertEqual(program.output, 'Hello World!')


class TestBrainfuckWithInput(unittest.TestCase):
    """testuje chování interpretru brainfucku pro programy se vstupem"""
    
    def setUp(self):
        self.BF = brainx.BrainFuck
        # skrytí výstupu
        self.out = sys.stdout
        sys.stdout = FakeStdOut()
    
    def tearDown(self):
        sys.stdout = self.out
    
    def test_bf_input_2(self):
        """numwarp.b pro vstup '123'"""
        with open( 'test_data/numwarp_input.b', encoding='ascii' ) as stream:
            data = stream.read()
        program = self.BF(data)
        self.assertEqual(program.output, '    /\\\n     /\\\n  /\\  /\n   / \n \\ \\/\n  \\\n   \n')


class TestPNG(unittest.TestCase):
    """testuje korektní načítání podmnožiny PNG-obrázků"""
    
    def setUp(self):
        self.png = image_png.PngReader
        # skrytí výstupu
        self.out = sys.stdout
        sys.stdout = FakeStdOut()
    
    def tearDown(self):
        sys.stdout = self.out
    
    def test_png_01(self):
        """umíme jen PNG"""
        self.assertRaises( image_png.PNGWrongHeaderError, self.png, 'test_data/sachovnice.jpg' )
    
    def test_png_02(self):
        """umíme jen některá PNG"""
        self.assertRaises( image_png.PNGNotImplementedError, self.png, 'test_data/sachovnice_paleta.png' )
    
    def test_png_03(self):
        """načtení jednoduchého PNG-obrázku"""
        image = self.png('test_data/sachovnice.png')
        self.assertEqual( image.rgb, [[(255, 0, 0), (0, 255, 0), (0, 0, 255)], [(255, 255, 255), (127, 127, 127), (0, 0, 0)], [(255, 255, 0), (255, 0, 255), (0, 255, 255)]] )


class TestBrainloller(unittest.TestCase):
    """testuje chování interpretru brainlolleru"""
    
    def setUp(self):
        self.BF = brainx.BrainFuck
        self.BL = brainx.BrainLoller
        # skrytí výstupu
        self.out = sys.stdout
        sys.stdout = FakeStdOut()
    
    def tearDown(self):
        sys.stdout = self.out
    
    def test_bl_1a(self):
        """načtení dat z obrázku HelloWorld.png"""
        objekt = self.BL('test_data/HelloWorld.png')
        self.assertEqual(objekt.data, '>+++++++++[<++++++++>-]<.>+++++++[<++++>-]<+.+++++++..+++.>>>++++++++[<++++>-]<.>>>++++++++++[<+++++++++>-]<---.<<<<.+++.------.--------.>>+.')
    
    def test_bl_1b(self):
        """vykonání programu z obrázku HelloWorld.png"""
        objekt = self.BL('test_data/HelloWorld.png')
        self.assertEqual(objekt.program.output, 'Hello World!')


#
# zajištění spuštění testů při zavolání souboru z příkazové řádky
#
if __name__ == '__main__':
    unittest.main()
