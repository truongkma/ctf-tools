#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
from image_png import PngReader


class BrainFuck:

    """Interpret of brainfuck."""

    def __init__(self, data, memory=b'\x00', memory_pointer=0):
        """Initialization of brainfuck interpreter."""

        # data of program
        self.data = data

        # initializcodeation of varialbles
        self.memory = bytearray(memory)
        self.memory_pointer = memory_pointer

        # DEBUG and tests
        # a) output memory
        self.output = ''

        try:
            with open(data, mode='r') as f:
                self.c = f.read()
        except:
            self.c = data

        self.user = self._findExMark()
        self._interpret(self.c)

    #
    # for test purposes
    #
    def get_memory(self):
        # Do not forget to change this acording to your implementation
        return self.memory

    def _interpret(self, c):
        """This is where the magic is going on"""

        c_i = 0
        while c_i < len(c):

            # incrementation
            if c[c_i] == '+':
                if self.memory[self.memory_pointer] != 255:
                    self.memory[self.memory_pointer] += 1
                # too much
                else:
                    self.memory[self.memory_pointer] = 0

            # decrementation
            elif c[c_i] == '-':
                if self.memory[self.memory_pointer] != 0:
                    self.memory[self.memory_pointer] -= 1
                else:
                    self.memory[self.memory_pointer] = 255

            # right shift
            elif c[c_i] == '>':
                self.memory_pointer += 1
                # make bigger
                if len(self.memory) == self.memory_pointer:
                    self.memory += bytearray([0])

            # left shift
            elif c[c_i] == '<':
                if self.memory_pointer > 0:
                    self.memory_pointer -= 1

            # read input
            elif c[c_i] == ',':
                self.memory[self.memory_pointer] = ord(self._readchar())

            # begining of loop
            elif c[c_i] == '[':
                if self.memory[self.memory_pointer] == 0:
                    loop_counter = 1
                    while loop_counter > 0:
                        c_i += 1
                        helper = c[c_i]
                        if helper == '[':
                            loop_counter += 1
                        elif helper == ']':
                            loop_counter -= 1

            # end of loop
            elif c[c_i] == ']':
                loop_counter = 1
                while loop_counter > 0:
                    c_i -= 1
                    helper = c[c_i]
                    if helper == '[':
                        loop_counter -= 1
                    elif helper == ']':
                        loop_counter += 1
                c_i -= 1

            # prompt char
            elif c[c_i] == '.':
                print(chr(self.memory[self.memory_pointer]), end=r'')
                self.output += chr(self.memory[self.memory_pointer])

            c_i += 1

    def _readchar(self):
        """Simple method for reading input."""
        if len(self.user) == 0:
            return sys.stdin.read(1)

        else:
            iRet = self.user[0]
            self.user = self.user[1:]
            return iRet

    def _findExMark(self):
        """finfing the stupid !"""
        c_i = 0
        while c_i < len(self.c) and self.c[c_i] != '!':
            c_i += 1

        if c_i + 1 < len(self.c):
            iRet = self.c[c_i + 1:]
            self.code = self.c[:c_i]
            return iRet

        return ''


class BrainLoller():

    """Class for managing brainloller."""

    def __init__(self, filename):
        """Initialization of brainloller"""
        rgb = PngReader(filename).rgb
        pointer = (0, 0)
        way = 0  # right
        # self.data contains parsed brainfuck code
        self.data = ''
        while True:
            if pointer[0] >= len(rgb) or pointer[0] < 0 or pointer[1] >= len(rgb[0]) or pointer[1] < 0:
                break
            elif rgb[pointer[0]][pointer[1]] == (255, 0, 0):
                self.data += '>'
            elif rgb[pointer[0]][pointer[1]] == (128, 0, 0):
                self.data += '<'
            elif rgb[pointer[0]][pointer[1]] == (0, 255, 0):
                self.data += '+'
            elif rgb[pointer[0]][pointer[1]] == (0, 128, 0):
                self.data += '-'
            elif rgb[pointer[0]][pointer[1]] == (0, 0, 255):
                self.data += '.'
            elif rgb[pointer[0]][pointer[1]] == (0, 0, 128):
                self.data += ','
            elif rgb[pointer[0]][pointer[1]] == (255, 255, 0):
                self.data += '['
            elif rgb[pointer[0]][pointer[1]] == (128, 128, 0):
                self.data += ']'
            elif rgb[pointer[0]][pointer[1]] == (0, 255, 255):
                way += 1
                way %= 4
            elif rgb[pointer[0]][pointer[1]] == (0, 128, 128):
                way -= 1
                way %= 4
            if way == 0:
                # right
                pointer = pointer[0], pointer[1] + 1
            elif way == 1:
                # down
                pointer = pointer[0] + 1, pointer[1]
            elif way == 2:
                # left
                pointer = pointer[0], pointer[1] - 1
            else:
                # up
                pointer = pointer[0] - 1, pointer[1]

        # ..which we give to interpreter
        self.program = BrainFuck(self.data)


class BrainCopter():

    """Class for managing braincopter."""

    def __init__(self, filename):
        """Initialization of braincopter."""
        rgb = PngReader(filename).rgb
        pointer = (0, 0)
        way = 0  # right
        # self.data contains parsed brainfuck code
        self.data = ''
        while True:
            if pointer[0] >= len(rgb) or pointer[0] < 0 or pointer[1] >= len(rgb[0]) or pointer[1] < 0:
                break
            pixel = rgb[pointer[0]][pointer[1]]
            cmd = (-2 * pixel[0] + 3 * pixel[1] + pixel[2]) % 11
            if cmd == 0:
                self.data += '>'
            elif cmd == 1:
                self.data += '<'
            elif cmd == 2:
                self.data += '+'
            elif cmd == 3:
                self.data += '-'
            elif cmd == 4:
                self.data += '.'
            elif cmd == 5:
                self.data += ','
            elif cmd == 6:
                self.data += '['
            elif cmd == 7:
                self.data += ']'
            elif cmd == 8:
                way += 1
                way %= 4
            elif cmd == 9:
                way -= 1
                way %= 4
            if way == 0:
                # right
                pointer = pointer[0], pointer[1] + 1
            elif way == 1:
                # down
                pointer = pointer[0] + 1, pointer[1]
            elif way == 2:
                # left
                pointer = pointer[0], pointer[1] - 1
            else:
                # up
                pointer = pointer[0] - 1, pointer[1]
        # ..which we give to interpreter
        self.program = BrainFuck(self.data)

if __name__ == "__main__":
    from optparse import OptionParser
    usage = "usage: %prog switch argument"
    parser = OptionParser(usage=usage)
    parser.add_option("-f", "--brainfuck",
                      action="store_true", dest="brainfuck",
                      help="Runs given file thought brainfuck interpreter")
    parser.add_option("-l", "--brainloller",
                      action="store_true", dest="brainloller",
                      help="Runs given file thought brainloller interpreter")
    parser.add_option("-c", "--braincopter",
                      action="store_true", dest="braincopter",
                      help="Runs given file thought braincopter interpreter")
    parser.add_option("-t", "--braintext",
                      action="store_true", dest="braintext",
                      help="Runs given text thought brainfuck interpreter")

    (options, args) = parser.parse_args()

    if len(args) == 0:
        parser.error("Too few arguments!")
    if bool(options.braincopter) + bool(options.brainfuck) + bool(options.brainloller) + bool(options.braintext) != 1:
        parser.error("Use only one switch!")

    if not options.braintext:
        try:
            with open(args[0]):
                pass
        except IOError:
            parser.error("This is not a file!")

    if options.braincopter:
        BrainCopter(args[0])
    elif options.brainfuck:
        BrainFuck(args[0])
    elif options.brainloller:
        BrainLoller(args[0])
    elif options.braintext:
        BrainFuck(args[0])
