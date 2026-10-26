"""Each case's key and message, and the shift cipher itself.

The messages are invented, so they cannot be recalled from somewhere else: the only way to the
plaintext is to find the key. A case's ciphertext is derived, never stored, so it cannot drift
from the message it is meant to encipher.
"""

from __future__ import annotations

from contract import Case

ALPHABET = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

# case -> (key letter, message). The keys are spread out so no two cases share a shift.
PUZZLES = {
    Case.POSTCARD: ("D", "THE HARBOR LIGHTS BLINK TWICE BEFORE DAWN"),
    Case.DISPATCH: ("N", "SEND THE SPARE ROTOR BY THE MORNING TRAIN"),
    Case.LEDGER: ("W", "COUNT NINE CRATES OF AMBER GLASS IN THE WEST SHED"),
    Case.TELEGRAM: ("Q", "MEET THE GREY BOAT AT THE OLD STONE PIER"),
}


def shift(text: str, places: int) -> str:
    """``text`` with every letter moved on by ``places``; anything else is left alone."""
    moved = []
    for character in text:
        if character in ALPHABET:
            moved.append(ALPHABET[(ALPHABET.index(character) + places) % len(ALPHABET)])
        else:
            moved.append(character)
    return "".join(moved)


def places_of(key: str) -> int:
    """How far ``key`` moves a letter: A is 0, B is 1, and so on."""
    if len(key) != 1 or key not in ALPHABET:
        raise ValueError(f"key must be one letter A to Z, not {key!r}")
    return ALPHABET.index(key)


def encipher(message: str, key: str) -> str:
    return shift(message, places_of(key))


def decipher(ciphertext: str, key: str) -> str:
    return shift(ciphertext, -places_of(key))


def ciphertext_of(case: Case) -> str:
    key, message = PUZZLES[case]
    return encipher(message, key)
