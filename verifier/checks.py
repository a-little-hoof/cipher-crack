"""Checks shared by the tool verifiers. Pure functions of their arguments.

The shift cipher here is the verifier's own implementation, written out again rather than imported:
the verifier may not import the plugin, and it should not take a tool's word for what a key does.
tests/test_cipher.py holds the two implementations in step.
"""

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
LONGEST_PLAINTEXT = 400


def result(valid, message, *, score=None, **details):
    return {
        "valid": valid,
        "score": float(valid) if score is None else score,
        "message": message,
        "details": details,
    }


def places_of(key):
    """How far ``key`` moves a letter: A is 0, B is 1, and so on. None when it is not one letter."""
    if len(key) != 1 or key not in ALPHABET:
        return None
    return ALPHABET.index(key)


def decipher(ciphertext, key):
    """``ciphertext`` with every letter moved back by ``key``; anything else is left alone."""
    places = places_of(key)
    moved = []
    for character in ciphertext:
        if character in ALPHABET:
            moved.append(ALPHABET[(ALPHABET.index(character) - places) % len(ALPHABET)])
        else:
            moved.append(character)
    return "".join(moved)


def key_problem(key):
    """What is wrong with ``key`` as a key letter, or None."""
    if not key:
        return "key must not be blank"
    if key != key.strip():
        return "key must have no surrounding spaces"
    if places_of(key) is None:
        return f"key must be one letter A to Z, not {key!r}"
    return None


def text_problem(text, label):
    """What is wrong with ``text`` as an enciphered or deciphered message, or None."""
    if not text.strip():
        return f"{label} must not be blank"
    if len(text) > LONGEST_PLAINTEXT:
        return f"{label} must be at most {LONGEST_PLAINTEXT} characters, not {len(text)}"
    stray = sorted({character for character in text if character not in ALPHABET + " "})
    if stray:
        return f"{label} must hold only capital letters and spaces, but also holds {stray}"
    return None


def agreement(said, wanted):
    """The share of ``wanted``'s characters ``said`` gets right, position by position."""
    if not wanted:
        return 0.0
    right = sum(one == two for one, two in zip(said, wanted))
    return right / max(len(said), len(wanted))
