"""
This is new branch to make this interpreter fit the test layouts
"""
__author__ = 'Tomas Sykora sykorto6@fit.cvut.cz'




import sys


class Output():
    def __init__(self):
        self.actual_output = [0] * 30000
        self.positon = 0

    def get(self):
        return self.actual_output[self.positon]

    def set(self, value):
        self.actual_output[self.positon] = value

    def increase(self):
        self.actual_output[self.positon] += 1

    def decrease(self):
        self.actual_output[self.positon] -= 1

    def move_right(self):
        self.positon += 1
        if self.positon > len(self.actual_output):
            self.positon = 0

    def move_left(self):
        self.positon -= 1
        if self.positon < 0:
            self.positon = len(self.actual_output) - 1

    def size(self):
        return self.actual_output.__len__()


def file_source(filename):
    with open(filename, encoding='utf-8') as bf_source_file:
        source = bf_source_file.read()
        return source


def prompt_source():
    print("You have not chosen any file please enter BrainFuck code manually")
    source = input()
    return source


def get_input():
    NONARGV = []
    if sys.argv[1:] == NONARGV:
        source = prompt_source()
        return source
    elif sys.argv[1] == '-f':
        return file_source(sys.argv[2])


def execute_interpreter(code):
    source = code
    output = Output()
    source_position = 0
    while len(source) >= source_position + 1:
        if source[source_position] == '+':
            output.increase()
        elif source[source_position] == '-':
            output.decrease()
        elif source[source_position] == '>':
            output.move_right()
        elif source[source_position] == '<':
            output.move_left()
        elif source[source_position] == ',':
            output.set(ord(sys.stdin.read(1)))
        elif source[source_position] == '[':
            if output.get() == 0:
                loop_counter = 1
                while loop_counter > 0:
                    source_position += 1
                    helper = source[source_position]
                    if helper == '[':
                        loop_counter += 1
                    elif helper == ']':
                        loop_counter -= 1
        elif source[source_position] == ']':
            loop_counter = 1
            while loop_counter > 0:
                source_position -= 1
                helper = source[source_position]
                if helper == '[':
                    loop_counter -= 1
                elif helper == ']':
                    loop_counter += 1
            source_position -= 1
        elif source[source_position] == '.':
            print(chr(output.get()), end=r'')
        elif source[source_position] == ',':
            if 0 <= source_position < 30000:
                x = input()
                output.set(x)
                source_position += 1
        source_position += 1


if __name__ == "__main__":
    execute_interpreter(get_input())



