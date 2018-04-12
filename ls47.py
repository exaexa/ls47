#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# This software is hereby released into public domain. Use it wisely.
#
# Originally written by Mirek Kratochvil (2017)
# Python3 port by Bernhard Esslinger (Feb 2018)

import random

letters = "_abcdefghijklmnopqrstuvwxyz.0123456789,-+*/:?!'()"
tiles = list(zip(letters, map(lambda x: (x // 7, x % 7), range(7 * 7))))
padding_size = 10


def check_key(key):
    if len(key) != len(letters):
        raise ValueError('Wrong key size')
    cnts = {}
    for c in letters:
        cnts[c] = 0
    for c in key:
        if not c in cnts:
            raise ValueError('Letter ' + c + ' not in LS47!')
        cnts[c] += 1
        if cnts[c] > 1:
            raise ValueError('Letter ' + c + ' duplicated in key!')


def find_ix(letter):
    m = [l for l in tiles if l[0] == letter]
    if len(m) != 1:
        raise ValueError('Letter ' + letter + ' not in LS47!')
    for (l, pos) in m:
        return pos


def find_pos(key, letter):
    p = key.find(letter)
    if p >= 0 and p < 7 * 7:
        return (p // 7, p % 7)
    raise ValueError('Letter ' + letter + ' not in key?!')


def add_pos(a, b):
    return ((a[0] + b[0]) % 7, (a[1] + b[1]) % 7)


def sub_pos(a, b):
    return ((a[0] - b[0]) % 7, (a[1] - b[1]) % 7)


def find_at_pos(key, coord):
    return key[coord[1] + coord[0] * 7]


def rotate_right(key, row, n):
    mid = key[7 * row:7 * (row + 1)]
    n = (7 - n % 7) % 7
    return key[:7 * row] + mid[n:] + mid[:n] + key[7 * (row + 1):]


def rotate_down(key, col, n):
    lines  = [key[i * 7:(i + 1) * 7] for i in range(7)]
    lefts  = [l[:col] for l in lines]
    mids   = [l[col] for l in lines]
    rights = [l[col + 1:] for l in lines]
    n = (7 - n % 7) % 7
    mids = mids[n:] + mids[:n]
    return ''.join(lefts[i] + mids[i] + rights[i] for i in range(7))


def rotate_marker_right(m, row, n):
    if m[0] != row:
        return (m[0], m[1])
    else:
        return (m[0], (m[1] + n) % 7)


def rotate_marker_down(m, col, n):
    if m[1] != col:
        return (m[0], m[1])
    else:
        return ((m[0] + n) % 7, m[1])


def derive_key(password):
    i = 0
    k = letters
    for c in password:
        (row, col) = find_ix(c)
        k = rotate_down(rotate_right(k, i, col), i, row)
        i = (i + 1) % 7
    return k


def encrypt(key, plaintext):
    check_key(key)
    mp = (0, 0)
    ciphertext = ''
    for p in plaintext:
        pp = find_pos(key, p)
        mix = find_ix(find_at_pos(key, mp))
        cp = add_pos(pp, mix)
        c = find_at_pos(key, cp)
        ciphertext += c

        key = rotate_right(key, pp[0], 1)
        cp = find_pos(key, c)
        key = rotate_down(key, cp[1], 1)
        mp = add_pos(mp, find_ix(c))
    return ciphertext


def decrypt(key, ciphertext):
    check_key(key)
    mp = (0, 0)
    plaintext = ''
    for c in ciphertext:
        cp = find_pos(key, c)
        mix = find_ix(find_at_pos(key, mp))
        pp = sub_pos(cp, mix)
        p = find_at_pos(key, pp)
        plaintext += p

        key = rotate_right(key, pp[0], 1)
        cp = find_pos(key, c)
        key = rotate_down(key, cp[1], 1)
        mp = add_pos(mp, find_ix(c))
    return plaintext


def encrypt_pad(key, plaintext, signature):

    # TODO it would also be great to randomize the message length.

    check_key(key)
    padding = ''.join(map(lambda x: letters[random.randint(0,
                      len(letters) - 1)], range(padding_size)))

    return encrypt(key, padding + plaintext + '---' + signature)


def decrypt_pad(key, ciphertext):
    check_key(key)
    return decrypt(key, ciphertext)[padding_size:]


if __name__ == '__main__':

    # a bit of test!

    print('letters in this implementation (line by line):')
    print(letters)
    # print('tiles positions: ' + str(tiles))

    key = derive_key('s3cret_p4ssw0rd/31337')
    print('test key: ' + key)
    enc = encrypt_pad(key, 'conflagrate_the_rose_bush_at_six!',
                      'peace-vector-3')

    print('encrypted test: ' + enc)
    dec = decrypt_pad(key, enc)
    print('decrypted test: ' + dec)
