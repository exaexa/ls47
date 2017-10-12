#!/usr/bin/python2
# -*- coding: utf-8 -*-

import random

letters = "_abcdefghijklmnopqrstuvwxyz.0123456789,-+*/:?!'()"
tiles = zip(letters, map(lambda x: (x / 7, x % 7), range(7 * 7)))
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
    m = filter(lambda (l, pos): l == letter, tiles)
    if len(m) != 1:
        raise ValueError('Letter ' + letter + ' not in LS47!')
    for (l, pos) in m:
        return pos


def find_pos(key, letter):
    p = key.find(letter)
    if p >= 0 and p < 7 * 7:
        return (p / 7, p % 7)
    raise ValueError('Letter ' + letter + ' not in key?!')


def add_pos((ax, ay), (bx, by)):
    return ((ax + bx) % 7, (ay + by) % 7)


def sub_pos((ax, ay), (bx, by)):
    return ((ax - bx) % 7, (ay - by) % 7)


def find_at_pos(key, (row, col)):
    return key[col + row * 7]


def rotate_right(key, row, n):
    mid = key[7 * row:7 * (row + 1)]
    n = (7 - n % 7) % 7
    return key[:7 * row] + mid[n:] + mid[:n] + key[7 * (row + 1):]


def rotate_down(key, col, n):
    lines = map(lambda i: key[i * 7:(i + 1) * 7], range(7))
    lefts = map(lambda l: l[:col], lines)
    mids = map(lambda l: l[col], lines)
    rights = map(lambda l: l[col + 1:], lines)
    n = (7 - n % 7) % 7
    mids = mids[n:] + mids[:n]
    return reduce(lambda a, b: a + b, map(lambda i: lefts[i] + mids[i] \
                  + rights[i], range(7)))


def rotate_marker_right((mrow, mcol), row, n):
    if mrow != row:
        return (mrow, mcol)
    else:
        return (mrow, (mcol + n) % 7)


def rotate_marker_down((mrow, mcol), col, n):
    if mcol != col:
        return (mrow, mcol)
    else:
        return ((mrow + n) % 7, mcol)


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
        mp = rotate_marker_right(mp, pp[0], 1)
        cp = find_pos(key, c)
        key = rotate_down(key, cp[1], 1)
        mp = rotate_marker_down(mp, cp[1], 1)
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
        mp = rotate_marker_right(mp, pp[0], 1)
        cp = find_pos(key, c)
        key = rotate_down(key, cp[1], 1)
        mp = rotate_marker_down(mp, cp[1], 1)
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

    key = derive_key('s3cret_p4ssw0rd/31337')
    print 'key:', key
    enc = encrypt_pad(key, 'conflagrate_the_rose_bush_at_six!',
                      'peace-vector-3')
    print 'encrypted:', enc
    dec = decrypt_pad(key, enc)
    print 'decrypted:', dec
