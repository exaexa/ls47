
# LS47 hand-computable cipher

This is a slight improvement of the ElsieFour cipher as described by Alan Kaminsky [1]. We use 7x7 characters instead of previous (barely fitting) 6x6 to be able to encrypt some structured information and add a simple key-expansion algorithm. Similar security considerations hold.

There's 3D-printable SCAD model of the whole thing.

### Character board

We have added some real punctuation, basic stuff for writing a bit of markdown,
and quotes&parens for writing structured information. The letters of the board
now look like this:

```
_ a b c d e f
g h i j k l m
n o p q r s t
u v w x y z .
0 1 2 3 4 5 6
7 8 9 , - + *
/ : ? ! ' ( )
```

Zoomed in, it's nice to have extra position information written on the tiles:

```
/-----\  /-----\  /-----\  /-----\  /-----\  
|     |  |     |  |     |  |     |  |     |  
| _  0|  | a  1|  | b  2|  | c  3|  | d  4|  ...
|   0 |  |   0 |  |   0 |  |   0 |  |   0 |  
\-----/  \-----/  \-----/  \-----/  \-----/  

/-----\  /-----\  
|     |  |     |  
| g  0|  | h  1|  ...
|   1 |  |   1 |  
\-----/  \-----/  
   .        .
   .        .
   .        .
```

You also need some kind of a marker (e.g. a small shiny stone, bolt nut or similar kinds of well-shaped trash).

## How-To

You may as well see the paper [1], there are also pictures. This is somewhat more concentrated:

### Encryption

1. The symmetric key is the initial state of the board. Arrange your tiles to 7x7 square according to the key.
2. Put the marker on (0,0).
3. Find the next letter you want to encrypt on the board, its position is `P`.
4. Look at the marker; numbers written on the marked tile are coordinates `M`.
5. Compute position of the ciphertext as `C := P + M mod (7,7)`. Output the letter found on position `C` as ciphertext.
6. Rotate the row that contains the plaintext letter one position to the right, carry the marker if present.
7. Rotate the column that now (after the first rotation) contains the ciphertext letter one position down, carry the marker if present.
8. Update the position of the marker: `M := M + C' mod (7,7)` where `C'` are the numbers written on the ciphertext tile.
9. Repeat from 3 as many times as needed to encrypt the whole plaintext.

### Decryption

Decryption procedure is basically the same, except that in step 5 you know `C`
and `M`, and need to produce `P` by subtraction: `P := C - M mod (7,7)`.
Otherwise (except that you input ciphertext and output plaintext) everything
stays the same.

### Key generation

Grab a bag full of tiles and randomly draw them one by one. Key is the 49-item permutation of them.

### Key expansion from a password

Remembering 49-position random permutation that includes weird characters is
not very handy. You can instead derive the keys from an arbitrary string of
sufficient length.

"Sufficient" means "provides enough entropy". Full keys store around 208 bits
of entropy. To reach that, your password should have:

- at least around 61 decimal digits if made only from random decimal digits
- at least around 44 letters if made only from completely random letters
- at least around 40 alphanumeric characters if made randomly only from them

To have the "standard" 128 bits of entropy, the numbers reduce to roughly 39,
28 and 25, respectively.

Note that you can save the expanded tile board for later if you don't want to
expand the passwords before each encryption/decryption.

The actual expansion can be as simple as this:

1. initialize `I:=0`, put the tiles on the board sorted by their numbers (i.e. as on the picture above)
2. Take the first letter of the password and see the numbers on its tile; mark them `Px, Py`.
3. Rotate `I`-th row `Px` positions right
4. Rotate `I`th column `Py` positions down
5. `I := I + 1 mod 7`, repeat from 2 with next letter of the password.
6. Resulting tile positions are the expanded key

### Undistinguishable ciphertexts

To get a different ciphertext even if the same plaintext is encrypted; prepend
it with a nonce. A nonce is a completely random sequence of letters of a
pre-negotiated length (at least 10 tiles drawn randomly from a bag is
adviseable).

You may also want to add a random number of spaces to the end of the ciphertext
-- it prevents the enemy from seeing the difference between ciphertexts for
'yes please' and 'no', which would otherwise encrypt to easily measurable
gibberish like `qwc3w_cs'(` and `+v`.

### Authenticated encryption

Because ciphertext may be altered in the transfer or during the error-prone
human processing, it is advised to append a simple "signature" to the end of
the message; e.g. a simple string `__YourHonorableNameHere`. If the signature
doesn't match expectations (which happens with overwhelming probability if
there was any error in the process), you discard the message and ask the sender
to re-transmit.

This works because the cipher output is message-dependent: Having a wrong bit
somewhere in the middle causes avalanche effect and breaks the signature.

## References

[1] *Kaminsky, Alan. "ElsieFour: A Low-Tech Authenticated Encryption Algorithm For Human-to-Human Communication." IACR Cryptology ePrint Archive 2017 (2017): 339.*
