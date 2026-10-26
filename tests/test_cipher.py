"""The invariants the design rests on: the two shift implementations agree, and no two cases
share a key, so a wrong key is always a distinguishable answer."""

from __future__ import annotations

import pytest

from contract import Case
from plugin.cases import ALPHABET, PUZZLES, ciphertext_of, decipher, encipher
from verifier.checks import decipher as verifier_decipher
from verifier.checks import text_problem


def test_every_case_has_a_puzzle() -> None:
    assert set(PUZZLES) == set(Case)


def test_no_two_cases_share_a_key() -> None:
    keys = [key for key, _ in PUZZLES.values()]
    assert len(set(keys)) == len(keys)


@pytest.mark.parametrize("case", list(Case))
def test_each_key_is_one_letter_and_each_message_is_letters_and_spaces(case: Case) -> None:
    key, message = PUZZLES[case]
    assert len(key) == 1 and key in ALPHABET
    assert text_problem(message, "message") is None
    assert text_problem(ciphertext_of(case), "ciphertext") is None


@pytest.mark.parametrize("case", list(Case))
def test_the_ciphertext_reads_back_as_the_message(case: Case) -> None:
    key, message = PUZZLES[case]
    assert decipher(ciphertext_of(case), key) == message


@pytest.mark.parametrize("case", list(Case))
def test_the_verifier_deciphers_exactly_as_the_plugin_does(case: Case) -> None:
    # The verifier may not import the plugin, so it writes the cipher out again on purpose.
    ciphertext = ciphertext_of(case)
    for key in ALPHABET:
        assert verifier_decipher(ciphertext, key) == decipher(ciphertext, key), key


@pytest.mark.parametrize("case", list(Case))
def test_only_the_real_key_gives_the_message_back(case: Case) -> None:
    key, message = PUZZLES[case]
    wrong = [other for other in ALPHABET if other != key and decipher(ciphertext_of(case), other) == message]
    assert wrong == []


@pytest.mark.parametrize("case", list(Case))
def test_enciphering_leaves_the_spaces_where_they_were(case: Case) -> None:
    _, message = PUZZLES[case]
    gaps = [index for index, character in enumerate(message) if character == " "]
    assert [index for index, character in enumerate(ciphertext_of(case)) if character == " "] == gaps


def test_a_key_that_moves_nothing_and_one_that_wraps_round_both_round_trip() -> None:
    message = "EDGE CASES AT BOTH ENDS"
    for key in ("A", "Z"):
        assert decipher(encipher(message, key), key) == message
