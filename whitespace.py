#!/usr/bin/env python

# Inspired vaguely by http://compsoc.dur.ac.uk/whitespace/
# Not a language, just an encoding

r"""
This defines an encoding, 'whitespace', so::

    >>> 'test'.encode('whitespace')
    ' \t\n \t\t \t\t\t\t\n \t\n \t  \t\n \t\t'
    >>> _.decode('whitespace')
    'test'
    >>> 'asfdasdfasdf'.decode('whitespace', 'replace')
    '??'

You can insert non-whitespace anywhere, and it doesn't matter::
    
    >>> 'blah \t\nx \ty\t \tz\t\t\t\n \t\n \t  \t\n \t\tblah'.decode('whitespace')
    'test'
"""

from cStringIO import StringIO
import sys
import re
import codecs

def catcher(default=None, printit=False):
    def decorator(func):
        def replacement(*args, **kw):
            if printit:
                print 'Call %s %s %s' % (
                    func.func_name, args, kw)
            try:
                value = func(*args, **kw)
                if printit:
                    print 'Returned %r' % (value,)
                return value
            except Exception, e:
                print 'Got exception in %s: %s' % (func, e)
                return default
        return replacement
    return decorator

numbers = ['  ', ' \t', ' \n', '\t ', '\t\t', '\t\n', '\n ', '\n\t']

char_numbers = {}
whitespace_numbers = {}
for i, n in enumerate(numbers):
    char_numbers[str(i)] = n
    whitespace_numbers[n] = i

def enc_char(c):
    """
    Takes a single character and returns it as a six-character
    set of whitespace.
    """
    octal = oct(ord(c))
    if len(octal) == 1:
        return '      '
    elif len(octal) == 2:
        return '    ' + char_numbers[octal[1]]
    elif len(octal) == 3:
        return '  ' + char_numbers[octal[1]] + char_numbers[octal[2]]
    else:
        return (char_numbers[octal[1]] + char_numbers[octal[2]]
                + char_numbers[octal[3]])

def dec_triplet(c):
    try:
        code = (whitespace_numbers[c[0:2]]*64
                + whitespace_numbers[c[2:4]]*8
                + whitespace_numbers[c[4:6]])
        if code > 255:
            raise ValueError(
                "Bad whitespace triplet: %r" % c)
        return chr(code)
    except KeyError:
        raise ValueError, "Bad whitespace triplet: %r" % c

def enc_stream(input, output):
    while 1:
        s = input.read(4096)
        if not s:
            break
        for c in s:
            output.write(enc_char(c))

@catcher(('', 0))
def codec_encode(s, errors='strict'):
    result = []
    for c in s:
        #if c not in ' \t\n':
        #    result.append(c)
        result.append(enc_char(c))
    return (''.join(result), len(s))

def dec_stream(input, output):
    s = ''
    while 1:
        data = input.read(36)
        if not data:
            break
        s += data
        s = re.sub(r'[^ \t\n]', '', s)
        while len(s) > 6:
            output.write(dec_triplet(s[:6]))
            s = s[6:]

_whitespace_re = re.compile(r'^[ \t\n]*$')
_not_whitespace_re = re.compile(r'[^ \t\n]')

_encoding_comment_re = re.compile(r'#[^\n]*coding:\s*[a-z][a-z0-9_-]+[^\n]*\n', re.I)

#@catcher((0, ''))
def codec_decode(s, errors='strict', extra=None):
    if extra is not None:
        fp = s
        s = errors
        errors = extra
    errors = 'strict'
    result = []
    extra_used = 0
    match = _encoding_comment_re.match(s)
    if match:
        s = s[match.end():]
        extra_used += match.end()
    if (errors == 'ignore' or errors == 'strict'
        and not _whitespace_re.match(s)):
        last_good = ''
        next_good = ''
        last_bad = 0
        next_bad = 0
        for c in s:
            if c in ' \t\n':
                next_good += c
            else:
                next_bad += 1
            if len(next_good) == 6:
                last_good += next_good
                last_bad += next_bad
                next_good, next_bad = '', 0
        extra_used = last_bad
        s = last_good
    length = len(s)
    for i in xrange(0, length/6):
        try:
            result.append(dec_triplet(s[i*6:i*6+6]))
        except ValueError:
            if errors == 'replace':
                result.append('?')
            elif errors == 'ignore':
                pass
            else:
                raise
    used = length - (length % 6) + extra_used
    return (''.join(result), used)

### Codec APIs

class StreamWriter(codecs.StreamWriter):
    encode = codec_encode

class StreamReader(codecs.StreamReader):
    decode = codec_decode

def find_codec(codec_name):
    if codec_name.lower() == 'whitespace':
        return (codec_encode, codec_decode, StreamReader, StreamWriter)
    return None

codecs.register(find_codec)

### Command-line usage

def main(args=None):
    if args is None:
        args = sys.argv[1:]
    import optparse
    parser = optparse.OptionParser(usage="%prog [OPTIONS]")
    parser.add_option(
        '-r', '--repr',
        action="store_true",
        dest="repr",
        help="Use repr() on output")
    parser.add_option(
        '-e', '--encode',
        action="store_true",
        dest="encode",
        help="Encode input")
    parser.add_option(
        '-d', '--decode',
        action="store_true",
        dest="decode",
        help="Decode input")
    parser.add_option(
        '--doctest',
        action="store_true",
        dest="doctest",
        help="Run doctests")
    options, args = parser.parse_args()
    if args:
        parser.print_help()
        return
    if options.doctest:
        import doctest
        doctest.testmod()
        return
    if options.encode:
        streamer = enc_stream
    elif options.decode:
        streamer = dec_stream
    else:
        print 'You must give -e or -d'
        parser.print_help()
        return
    if options.repr:
        output = StringIO()
    else:
        output = sys.stdout
    streamer(sys.stdin, output)
    if options.repr:
        print repr(output.getvalue())
        
if __name__ == '__main__':
    main()
 