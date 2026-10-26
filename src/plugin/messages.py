"""read_cipher, decrypt and solution: the puzzle, one attempt at it, and its answer."""

from __future__ import annotations

from pathlib import Path

from contract import CaseInput, CipherOutput, DecryptInput, DecryptOutput, SolutionOutput
from plugin.cases import PUZZLES, ciphertext_of, decipher, places_of


def read_cipher(given: CaseInput, workspace: Path) -> CipherOutput:
    return CipherOutput(case=given.case, ciphertext=ciphertext_of(given.case))


def decrypt(given: DecryptInput, workspace: Path) -> DecryptOutput:
    key = given.key.strip().upper()
    places_of(key)  # raises unless the key is one letter A to Z
    ciphertext = ciphertext_of(given.case)
    return DecryptOutput(
        case=given.case,
        ciphertext=ciphertext,
        key=key,
        plaintext=decipher(ciphertext, key),
    )


def solution(given: CaseInput, workspace: Path) -> SolutionOutput:
    """The task's reference tool: NanoAgent runs it out of the model's sight."""
    key, message = PUZZLES[given.case]
    return SolutionOutput(
        case=given.case,
        ciphertext=ciphertext_of(given.case),
        key=key,
        plaintext=message,
    )
