# -*- coding: utf-8 -*-
from base64 import urlsafe_b64decode, urlsafe_b64encode


def dotnet_b64decode(s):
    '''Decode .NET Web-Base64 encoded data.'''
    s, pad_bytes = s[:-1], int(s[-1])
    s += ('=' * pad_bytes)
    return urlsafe_b64decode(s)


def dotnet_b64encode(s):
    '''.NET Web-Base64 encode data.'''
    s = urlsafe_b64encode(s)
    pad_bytes = s.count('=')
    return s[:-pad_bytes or len(s)] + str(pad_bytes)


def is_vulnerable(encrypted):
    '''
    Checks encrypted token from ScriptResource.axd or WebResource.axd
    to determine if application is vulnerable to MS10-070.

    :returns: True if vulnerable, else False
    '''
    if len(dotnet_b64decode(encrypted)) % 8 == 0:
        return True

    return False
