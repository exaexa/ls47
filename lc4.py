#!/usr/bin/python2
# -*- coding: utf-8 -*-
# This software is hereby released into public domain. Use it wisely.
#
# ElsieFour (LC4) and its enhancement LS47
# version 2.8.1 (2018-07-24)
#
# Original paper by Alan Kaminsky: https://eprint.iacr.org/2017/339.pdf
# Original LC4 Java source: https://www.cs.rit.edu/~ark/parallelcrypto/elsiefour/
#
# - Python 2 script for LS47 originally written by Mirek Kratochvil (2017)
#   See https://gitea.blesmrt.net/exa/ls47
# - Python 3 port by Bernhard Esslinger / AK (Feb 2018)
#   See www.mysterytwisterc3.org
# - New options by CrypTool project (www.cryptool.org) (Feb 2018) in order to
#   support both ciphers LC4 and LS47 in one program, to support both ways to
#   deal with nonces and keywords, to support reading from file and commandline,
#   and to extend test outputs (v2.7).
# - v2.8 extended the testcase and added the fix of the fixpoint-ish problem for ls47 (option -m1):
#   python lc4.py -6 -ws thisismysecretkey -es ############## -ns igxf5e -m1
#   igxf5egcyhoo#ny#o5i5
#   python lc4.py -6 -ws thisismysecretkey -es ############## -ns igxf5e -m0
#   igxf5e##############
#
# Sample calls:
#
# 1) Using cipher LC4, enforced with option -6:
# // encrypt (key, message). Following example returns tk5j23tq94_gw9c#lhzs
# python lc4.py -6 -ks s2ferw_nx346ty5odiupq#lmz8ajhgcvk79b  -es aaaaaaaaaaaaaaaaaaaa
# // decrypt (key, message). Following example returns aaaaaaaaaaaaaaaaaaaa
# python lc4.py -6 -ks s2ferw_nx346ty5odiupq#lmz8ajhgcvk79b  -ds tk5j23tq94_gw9c#lhzs
# python lc4.py -6 -ws thisismysecretkey -es its_my_fathers_son_but_not_my_brother
# python lc4.py -6 -ws thisismysecretkey -ds 6dudfy3u7omoxy4jbscgn37c2se_d8gx6ogk9
# python lc4.py -6 -ws thisismysecretkey -es its_my_fathers_son_but_not_my_brother -v -nl 6
# python lc4.py -6 -ws thisismysecretkey -ds q6xojffkncfyz#f5czs49#3mbsco#2iscvbnm#bymaf -v -nl 6
#
# 2) Using cipher LS47, enforced with option -7:
# python lc4.py -7 -ws s3cret_p4ssw0rd/31337 -es conflagrate_the_rose_bush_at_six!---peace-vector-3  -v -ns 8y(l._4ct'  -m0
# python lc4.py -7 -ws s3cret_p4ssw0rd/31337 -ds y'zbvvs+d2,ky4sy?w(_wkz*7'90v:./s)kcz?mj+gyu8-'h(y,i+v,z+1ws -v -nl 10  -m0
# python lc4.py -7 -ws s3cret_p4ssw0rd/31337 -ds y'zbvvs+d2,ky4sy?w(_wkz*7'90v:./s)kcz?mj+gyu8-'h(y,i+v,z+1ws -v -ns 8y(l._4ct'  -m0
#
# 3) Using the automatic test (option -t can be combined with options -s and -ws)
# python lc4.py -t
# python lc4.py -t  -ws s3cret_p4sswxyz  -s peacevector_34


from __future__ import print_function
import sys
import os
import random
import argparse


version = "v2.8.1 (2018-07-24)"

# define alphabet
letters6 = "#_23456789abcdefghijklmnopqrstuvwxyz"
letters7 = "_abcdefghijklmnopqrstuvwxyz.0123456789,-+*/:?!'()"


def missing_letters(s,t):
    return ''.join(sorted(set(c for c in s if c not in t)))


def check_key(key):
    illegal = missing_letters(key,letters)
    missing = missing_letters(letters,key)
    duplicates = ''.join(sorted(c for c in letters if key.count(c)>1))

    errors = []
    if illegal: errors.append( "Key contains illegal letters: '%s'" % illegal )
    if missing: errors.append( "Key misses some letters: '%s'" % missing )
    if duplicates: errors.append( "Key contains duplicate letters: '%s'" % duplicates )

    if errors:
        errors.append( "The key must be a permutation of the alphabet: %s" % letters )
        raise ValueError("\n".join(errors))


def check_nonce(nonce):
    illegal = missing_letters(nonce,letters)
    if illegal:
        raise ValueError("Nonce contains illegal letters: '%s'" % illegal)


def check_plaintext(s):
    illegal = missing_letters(s,letters)
    if illegal:
        raise ValueError("Plaintext contains illegal letters: '%s'" % illegal)


def check_ciphertext(s):
    illegal = missing_letters(s,letters)
    if illegal:
        raise ValueError("Ciphertext contains illegal letters: '%s'" % illegal)


def find_ix(letter):
    m = [l[1] for l in tiles if l[0] == letter]
    if len(m) != 1:
        raise ValueError("Letter '%c' not in the alphabet!" % letter)
    return m[0]


def find_pos(key, letter):
    p = key.find(letter)
    if not (0 <= p < size * size):
        raise ValueError("Letter '%c' not in key?!" % letter)
    return (p // size, p % size)


def add_pos(a, b):
    return ((a[0] + b[0]) % size, (a[1] + b[1]) % size)


def sub_pos(a, b):
    return ((a[0] - b[0]) % size, (a[1] - b[1]) % size)


def find_at_pos(key, coord):
    return key[coord[1] + coord[0] * size]


def rotate_right(key, row, n):
    mid = key[size * row:size * (row + 1)]
    return key[:size * row] + mid[-n:] + mid[:-n] + key[size * (row + 1):]


def rotate_down(key, col, n):
    lines  = [key[i * size:(i + 1) * size] for i in range(size)]
    lefts  = [l[:col] for l in lines]
    mids   = [l[col] for l in lines]
    rights = [l[col + 1:] for l in lines]
    mids = mids[-n:] + mids[:-n]
    return ''.join(lefts[i] + mids[i] + rights[i] for i in range(size))


def rotate_marker_right(m, row, n):
    if m[0] != row:
        return (m[0], m[1])
    else:
        return (m[0], (m[1] + n) % size)


def rotate_marker_down(m, col, n):
    if m[1] != col:
        return (m[0], m[1])
    else:
        return ((m[0] + n) % size, m[1])


def derive_key(password):
    i = 0
    k = letters
    for c in password:
        (row, col) = find_ix(c)
        k = rotate_down(rotate_right(k, i, col), i, row)
        i = (i + 1) % size
    return k


def encrypt(plaintext):
    global key, mp

    ciphertext = ''
    for p in plaintext:
        pp = find_pos(key, p)
        mix = find_ix(find_at_pos(key, mp))
        cp = add_pos(pp, mix)
        c = find_at_pos(key, cp)
        ciphertext += c

        key = rotate_right(key, pp[0], 1)
        if marker_mode==1: mp = rotate_marker_right(mp, pp[0], 1)
        cp = find_pos(key, c)
        key = rotate_down(key, cp[1], 1)
        if marker_mode==1: mp = rotate_marker_down(mp, cp[1], 1)
        mp = add_pos(mp, find_ix(c))
    return ciphertext


def decrypt(ciphertext):
    global key, mp

    plaintext = ''
    for c in ciphertext:
        cp = find_pos(key, c)
        mix = find_ix(find_at_pos(key, mp))
        pp = sub_pos(cp, mix)
        p = find_at_pos(key, pp)
        plaintext += p

        key = rotate_right(key, pp[0], 1)
        if marker_mode==1: mp = rotate_marker_right(mp, pp[0], 1)
        cp = find_pos(key, c)
        key = rotate_down(key, cp[1], 1)
        if marker_mode==1: mp = rotate_marker_down(mp, cp[1], 1)
        mp = add_pos(mp, find_ix(c))
    return plaintext


def create_random_nonce(size):
    return ''.join(random.choice(letters) for i in range(size))


def encrypt_with_nonce(plaintext):
    global nonce, nonce_enc

    ciphertext = encrypt(nonce + plaintext)
    nonce_enc = ciphertext[:nonce_size]

    if nonce_mode==1:
        return nonce + ciphertext[nonce_size:]
    else:
        return ciphertext


def decrypt_with_nonce(ciphertext):
    global nonce, nonce_enc

    if nonce_mode==1:
        nonce = ciphertext[:nonce_size]
        nonce_enc = encrypt(nonce)
        return decrypt(ciphertext[nonce_size:])
    else:
        plaintext = decrypt(ciphertext)
        nonce = plaintext[:nonce_size]
        nonce_enc = ciphertext[:nonce_size]
        return plaintext[nonce_size:]


def eprint(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def printinfo(enc=False):  # used by test1() and when option -v
    eprint('CIPHER    : ' + ("LC4" if size==6 else "LS47"))
    eprint('ALPHABET  : ' + letters)
    if szkeyword:
        eprint('KEYWORD   : ' + szkeyword)
    eprint('KEY       : ' + initialkey)  # key variable modified during process?
    eprint('NONCE     : ' + nonce)
    eprint('NONCE ENC : ' + nonce_enc)
    eprint('NONCEMODE : ' + ("Kaminsky" if nonce_mode==1 else "Kratochvil"))
    eprint('MARKER    : ' + ("Kaminsky" if marker_mode==1 else "Kratochvil"))
    if enc:
        # if args.signature: print ("args.SIGNA:", args.signature)
        if szsignature: print ("SIGNATURE: ", szsignature)
        eprint('PLAINTEXT : ' + plaintext)
        eprint('CIPHERTEXT: ' + ciphertext)
    else:
        eprint('CIPHERTEXT: ' + ciphertext)
        eprint('PLAINTEXT : ' + plaintext)


def test1(size, fixednonce):
    # Declaration "global" only needed if you like to write to a global variable
    # [here, this is necessary only if the global var. is used within a fct. called by test1()]
    # As test1() is called several times don't change args components within this fct.
    global letters, nonce_mode, marker_mode, tiles, noncelen, nonce, nonce_size, nonce_enc
    global ciphertext, plaintext, key, initialkey, mp
    global szkeyword, szsignature

    if size == 7:
        CIPHERNAME = "LS47"
        letters = letters7
        nonce_mode = 2
        marker_mode = 2
        if fixednonce == 0:
            noncelen=10; nonce = create_random_nonce(noncelen)
        else:
            nonce = 'dr0+:_pij2'  # just a sample for testing fixed nonce
    else:
        CIPHERNAME = "LC4"
        letters = letters6
        nonce_mode = 1
        marker_mode = 1
        if fixednonce == 0:
            noncelen=6; nonce = create_random_nonce(noncelen)
        else:
            nonce = 'pjpm5i'  # just a sample for testing fixed nonce

    tiles = list(zip(letters, [(x // size, x % size) for x in range(size * size)]))
    check_nonce(nonce)
    nonce_size = len(nonce)
    nonce_enc = ""

    print('\n' + CIPHERNAME)

    if size == 7:
        if args.keywordstring:
            keyword = args.keywordstring  # Allows to use -ws besides -t
        else:
            keyword = 's3cret_p4ssw0rd/31337'
        szkeyword = keyword # This statement needed to show keyword in printinfo() [don't change args.keywordstring within test1()!]
        key = derive_key(keyword)
    else:
        key = letters
    initialkey = key
    check_key(key)
    mp = (0, 0)

    if size == 7:
        # signature = 'peace-vector-3'   # just to name a meaningful value for size=7
        plaintext = 'conflagrate_the_rose_bush_at_six!'
        if szsignature: plaintext += szsignature
    else:
        # signature = '#its_me'  # Notice: with size=6 the chars "#", "0", "1", "-" aren't part of the alphabet
        plaintext = 'its_my_fathers_son_but_not_my_brother'
        if szsignature: plaintext += szsignature

    check_plaintext(plaintext)
    ciphertext = encrypt_with_nonce(plaintext)

    key = initialkey; mp = (0, 0)  # initialization again
    check_ciphertext(ciphertext)
    decryptedtext = decrypt_with_nonce(ciphertext)
    print('decrypted text: ' + decryptedtext)

    printinfo(True) # Called from test1() with arg TRUE = assume to do decryption

    szkeyword=''



if __name__ == '__main__':

    parser = argparse.ArgumentParser() # how to enforce, that (either no arg), (or only one arg -t, -v), (or give key and enc mode)

    parser.add_argument("-v", "--verbose", help="output additional information on stderr", action="count", default=0)

    mgroup1 = parser.add_mutually_exclusive_group()
    mgroup1.add_argument("-6", "--lc4", help="use ElsieFour cipher (6x6 table) (default)", action="store_true")
    mgroup1.add_argument("-7", "--ls47", help="use LS47 cipher (7x7 table)", action="store_true")

    mgroup2 = parser.add_mutually_exclusive_group()
    mgroup2.add_argument("-ks", "--keystring", metavar="STRING", help="use STRING as key")
    mgroup2.add_argument("-kf", "--keyfile", metavar="FILE", help="read key from FILE")
    mgroup2.add_argument("-ws", "--keywordstring", metavar="STRING", help="generate key from keyword STRING", default=None)
    mgroup2.add_argument("-wf", "--keywordfile", metavar="FILE", help="read keyword from FILE to generate key", default=None)

    mgroup4 = parser.add_mutually_exclusive_group()
    mgroup4.add_argument("-es", "--encryptstring", metavar="STRING", help="encrypt STRING")
    mgroup4.add_argument("-ef", "--encryptfile", metavar="FILE", help="read plaintext from FILE and encrypt it")
    mgroup4.add_argument("-ds", "--decryptstring", metavar="STRING", help="decrypt STRING")
    mgroup4.add_argument("-df", "--decryptfile", metavar="FILE", help="read ciphertext from FILE and decrypt it")
    mgroup4.add_argument("-t", "--test", help="encrypt and decrypt a string with a given key (with LC4, the given key equals the alphabet). Four cases tested: random/fixed nonce, each with LC4 and LS47", action="store_true")

    mgroup3 = parser.add_mutually_exclusive_group()
    mgroup3.add_argument("-nl", "--noncelen", metavar="LENGTH", help="use random nonce of length LENGTH (default: no nonce)", type=int, default=0)
    mgroup3.add_argument("-ns", "--noncestring", metavar="STRING", help="use STRING as nonce (default: no nonce)")

    mgroup5 = parser.add_mutually_exclusive_group()
    mgroup5.add_argument("-n0", "--nKaminsky", help="use nonce in Kaminsky mode (default for LC4)", action="store_true")
    mgroup5.add_argument("-n1", "--nKratochvil", help="use nonce in Kratochvil mode (default for LS47)", action="store_true")

    mgroup6 = parser.add_mutually_exclusive_group()
    mgroup6.add_argument("-m0", "--mKaminsky", help="use marker in Kaminsky mode (default for LC4)", action="store_true")
    mgroup6.add_argument("-m1", "--mKratochvil", help="use marker in Kratochvil mode (default for LS47)", action="store_true")


    parser.add_argument("-s", "--signature", help="append SIGNATURE to plaintext when encrypting (default: no signature)")

    args = parser.parse_args()

    if len(sys.argv)==1:
        parser.print_help()
        sys.exit(1)
    if args.verbose and len(sys.argv)==2:
        print('Version: ' + version)
        # parser.print_help()
        sys.exit(1)

    # set cipher

    if args.ls47:
        size = 7
        letters = letters7
    else:
        size = 6
        letters = letters6

    tiles = list(zip(letters, [(x // size, x % size) for x in range(size * size)]))

    # set nonce

    if args.noncestring:
        nonce = args.noncestring
    elif args.noncelen:
        nonce = create_random_nonce(args.noncelen)
    else:
        nonce = ""

    check_nonce(nonce)
    nonce_size = len(nonce)
    nonce_enc = ""

    # set nonce mode

    nonce_mode = 1 if size==6 else 2
    if args.nKaminsky: nonce_mode = 1
    if args.nKratochvil: nonce_mode = 2

    # set marker mode

    marker_mode = 1 if size==6 else 2
    if args.mKaminsky: marker_mode = 1
    if args.mKratochvil: marker_mode = 2

    # set key

    key = letters

    # helper variables for verbose printing via printinfo()

    szkeyword = '' # global variable which can be changed in test1() [so it can be used as test condition in printinfo() instead of args.keywordstring and instead of test1() manipulating args.keywordstring]
    szsignature = '' # global variable which can be changed in test1() [so it can be used as test condition in printinfo() instead of args.keywordstring and instead of test1() manipulating args.keywordstring].  # Allows to use -s besides -t

    if args.signature: # This case here is only necessary if -s should be used together with -t
        szsignature = args.signature


    if args.keywordfile: args.keywordstring = open(args.keywordfile, 'r').read().rstrip('\r\n')
    if args.keywordstring:
        szkeyword = args.keywordstring
        key = derive_key(args.keywordstring)

    if args.keyfile: args.keystring = open(args.keyfile, 'r').read().rstrip('\r\n')
    if args.keystring: key = args.keystring;

    initialkey = key
    check_key(key)

    mp = (0, 0)

    # encrypt / decrypt / test

    if args.encryptfile:
        args.encryptstring = open(args.encryptfile, 'r').read().rstrip('\r\n')

    if args.decryptfile:
        args.decryptstring = open(args.decryptfile, 'r').read().rstrip('\r\n')

    if args.encryptstring:
        plaintext = args.encryptstring
        if args.signature:
            plaintext += args.signature
        check_plaintext(plaintext)
        ciphertext = encrypt_with_nonce(plaintext)
        if args.verbose:
            printinfo(True)
        else:
            print(ciphertext)

    elif args.decryptstring:
        ciphertext = args.decryptstring
        check_ciphertext(ciphertext)
        plaintext = decrypt_with_nonce(ciphertext)
        if args.signature and args.verbose:
            eprint("--Warning--: the given signature is ignored during decryption")
            # Maybe later return result of a check whether given signature equals the end of the decrypted string.
        if args.verbose:
            printinfo()
        else:
            print(plaintext)

    elif args.test:
        print('\nVersion: ' + version)
        print('\n---Test: No nonce provided (only its length), so each call will produce a different ciphertext.')
        size = 7; test1(size, 0)
        size = 6; test1(size, 0)
        print('\n---Test: Nonce provided as string.')
        size = 7; test1(size, 1)
        size = 6; test1(size, 1)
        sys.exit(1)

    else: # you'll never get here (handled via argparse)
        # if args.verbose: print('Version   : ' + version)
        print('ALPHABET  : ' + letters)
        print('KEY       : ' + initialkey)
        print('NONCE     : ' + nonce)
