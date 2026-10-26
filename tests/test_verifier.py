from __future__ import annotations

from pathlib import Path

import pytest
from slimconfig import build_output, plain_output

import verifier
from contract import TASKS, TOOLS, Case, CaseInput, DecryptInput, SolutionOutput, Task, Tool
from plugin import decrypt, read_cipher, solution
from plugin.cases import PUZZLES, ciphertext_of, decipher


# The verifier gets contract instances, as NanoAgent's sandbox builds them from JSON.
def verify_input(tool: str, value: dict) -> dict:
    return verifier.verify_input(tool, build_output(value, TOOLS[Tool(tool)][0]))


def verify_output(tool: str, input_value: dict, output_value: dict, workspace: Path) -> dict:
    given, made = TOOLS[Tool(tool)]
    return verifier.verify_output(
        tool, build_output(input_value, given), build_output(output_value, made), str(workspace)
    )


def verify_task(task: str, arguments: dict, output: dict, workspace: Path, reference: dict | None = None) -> dict:
    given, made = TASKS[Task(task)]
    pinned = None if reference is None else build_output(reference, SolutionOutput)
    given_value, made_value = build_output(arguments, given), build_output(output, made)
    return verifier.verify_task(task, given_value, made_value, pinned, str(workspace))


def answer(case: Case, workspace: Path) -> dict:
    return plain_output(solution(CaseInput(case=case), workspace))


def crack(case: Case, key: str, plaintext: str, workspace: Path, reference: dict | None = None) -> dict:
    reference = answer(case, workspace) if reference is None else reference
    submitted = {"case": case.value, "key": key, "plaintext": plaintext}
    return verify_task("crack-cipher", {"case": case.value}, submitted, workspace, reference)


def under(case: Case, key: str) -> str:
    """What ``case``'s message reads as under ``key`` — right or wrong."""
    return decipher(ciphertext_of(case), key)


# --- correct ---------------------------------------------------------------


@pytest.mark.parametrize("case", list(Case))
def test_the_real_key_and_message_crack_every_case(tmp_path: Path, case: Case) -> None:
    key, message = PUZZLES[case]
    verdict = crack(case, key, message, tmp_path)
    assert verdict["valid"] is True and verdict["score"] == 1.0


@pytest.mark.parametrize("case", list(Case))
def test_a_lowercase_or_padded_answer_is_still_the_answer(tmp_path: Path, case: Case) -> None:
    # Casing and stray spaces are not the substance of the message.
    key, message = PUZZLES[case]
    assert crack(case, f"  {key.lower()} ", f" {message.lower()}  ", tmp_path)["valid"] is True


# --- incorrect -------------------------------------------------------------


def test_a_wrong_key_with_the_nonsense_it_produces_is_refused(tmp_path: Path) -> None:
    # Self-consistent but not English: the reference is what settles it.
    verdict = crack(Case.POSTCARD, "E", under(Case.POSTCARD, "E"), tmp_path)
    assert verdict["valid"] is False and "is not the key" in verdict["message"]
    assert 0.0 <= verdict["score"] < 1.0


def test_the_right_message_under_a_key_that_does_not_produce_it_is_refused(tmp_path: Path) -> None:
    key, message = PUZZLES[Case.DISPATCH]
    wrong_key = "A" if key != "A" else "B"
    verdict = crack(Case.DISPATCH, wrong_key, message, tmp_path)
    assert verdict["valid"] is False and "not the message submitted" in verdict["message"]


def test_one_wrong_letter_in_the_message_is_refused(tmp_path: Path) -> None:
    key, message = PUZZLES[Case.LEDGER]
    typo = message.replace("COUNT", "COUNS", 1)
    verdict = crack(Case.LEDGER, key, typo, tmp_path)
    assert verdict["valid"] is False
    assert verdict["score"] > 0.9  # almost right, and still not right


def test_the_submitted_case_must_be_the_one_asked_for(tmp_path: Path) -> None:
    key, message = PUZZLES[Case.TELEGRAM]
    submitted = {"case": Case.TELEGRAM.value, "key": key, "plaintext": message}
    verdict = verify_task(
        "crack-cipher", {"case": Case.POSTCARD.value}, submitted, tmp_path, answer(Case.POSTCARD, tmp_path)
    )
    assert verdict["valid"] is False and "not postcard" in verdict["message"]


# --- missing ---------------------------------------------------------------


@pytest.mark.parametrize(
    ("key", "plaintext", "message"),
    [("", "ANY TEXT", "key must not be blank"), ("D", "   ", "plaintext must not be blank")],
)
def test_a_missing_key_or_message_is_refused(tmp_path: Path, key: str, plaintext: str, message: str) -> None:
    verdict = crack(Case.POSTCARD, key, plaintext, tmp_path)
    assert verdict["valid"] is False and message in verdict["message"]


def test_a_reference_whose_key_does_not_fit_its_message_is_refused(tmp_path: Path) -> None:
    # The verifier does not trust the reference tool either: it deciphers the ciphertext again.
    key, message = PUZZLES[Case.POSTCARD]
    tampered = answer(Case.POSTCARD, tmp_path) | {"key": "E"}
    verdict = crack(Case.POSTCARD, key, message, tmp_path, tampered)
    assert verdict["valid"] is False and "the reference key" in verdict["message"]


def test_a_reference_for_another_case_is_refused(tmp_path: Path) -> None:
    key, message = PUZZLES[Case.POSTCARD]
    verdict = crack(Case.POSTCARD, key, message, tmp_path, answer(Case.DISPATCH, tmp_path))
    assert verdict["valid"] is False and "reference answer is for dispatch" in verdict["message"]


# --- malformed -------------------------------------------------------------


@pytest.mark.parametrize(
    ("key", "message"),
    [
        ("AB", "one letter A to Z"),
        ("3", "one letter A to Z"),
        ("-", "one letter A to Z"),
    ],
)
def test_a_key_that_is_not_one_letter_is_refused(tmp_path: Path, key: str, message: str) -> None:
    verdict = crack(Case.POSTCARD, key, "ANY TEXT", tmp_path)
    assert verdict["valid"] is False and message in verdict["message"]


@pytest.mark.parametrize(
    ("plaintext", "message"),
    [
        ("THE HARBOR LIGHTS BLINK TWICE BEFORE DAWN.", "capital letters and spaces"),
        ("THE HARBOR-LIGHTS BLINK TWICE BEFORE DAWN", "capital letters and spaces"),
        ("A" * 401, "at most 400 characters"),
    ],
)
def test_a_message_that_is_not_letters_and_spaces_is_refused(tmp_path: Path, plaintext: str, message: str) -> None:
    verdict = crack(Case.POSTCARD, "D", plaintext, tmp_path)
    assert verdict["valid"] is False and message in verdict["message"]


# --- boundary --------------------------------------------------------------


@pytest.mark.parametrize("key", ["A", "Z"])
def test_the_ends_of_the_alphabet_work_as_keys(tmp_path: Path, key: str) -> None:
    # A moves nothing and Z wraps every letter round, so both are worth their own check.
    given = {"case": Case.POSTCARD.value, "key": key}
    made = plain_output(decrypt(DecryptInput(case=Case.POSTCARD, key=key), tmp_path))
    assert verify_output("decrypt", given, made, tmp_path)["valid"] is True
    assert made["plaintext"] == under(Case.POSTCARD, key)


def test_a_near_miss_scores_higher_than_a_wild_guess(tmp_path: Path) -> None:
    key, message = PUZZLES[Case.TELEGRAM]
    near = crack(Case.TELEGRAM, key, message.replace("PIER", "PIES", 1), tmp_path)
    wild = crack(Case.TELEGRAM, "B", under(Case.TELEGRAM, "B"), tmp_path)
    assert near["valid"] is False and wild["valid"] is False
    assert near["score"] > wild["score"]


# --- the tools' own checks -------------------------------------------------


@pytest.mark.parametrize("case", list(Case))
def test_read_cipher_and_solution_describe_the_same_case(tmp_path: Path, case: Case) -> None:
    given = {"case": case.value}
    puzzle = plain_output(read_cipher(CaseInput(case=case), tmp_path))
    found = answer(case, tmp_path)
    assert verify_output("read_cipher", given, puzzle, tmp_path)["valid"] is True
    assert verify_output("solution", given, found, tmp_path)["valid"] is True
    assert puzzle["ciphertext"] == found["ciphertext"]
    assert verify_output("read_cipher", {"case": _other(case).value}, puzzle, tmp_path)["valid"] is False


def _other(case: Case) -> Case:
    return next(one for one in Case if one is not case)


def test_decrypt_reports_what_that_key_really_reads_as(tmp_path: Path) -> None:
    given = {"case": Case.DISPATCH.value, "key": "n"}
    made = plain_output(decrypt(DecryptInput(case=Case.DISPATCH, key="n"), tmp_path))
    assert verify_input("decrypt", given)["valid"] is True
    assert verify_output("decrypt", given, made, tmp_path)["valid"] is True
    assert made["key"] == "N" and made["plaintext"] == PUZZLES[Case.DISPATCH][1]


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"plaintext": "SOMETHING ELSE ENTIRELY"}, "not the plaintext given"),
        ({"key": "Z"}, "report the key it was given"),
        ({"ciphertext": "ABC DEF"}, "not the plaintext given"),
    ],
)
def test_a_decrypt_report_that_does_not_add_up_is_refused(tmp_path: Path, change: dict, message: str) -> None:
    given = {"case": Case.DISPATCH.value, "key": "N"}
    made = plain_output(decrypt(DecryptInput(case=Case.DISPATCH, key="N"), tmp_path)) | change
    verdict = verify_output("decrypt", given, made, tmp_path)
    assert verdict["valid"] is False and message in verdict["message"]


def test_decrypt_refuses_a_key_it_could_not_use(tmp_path: Path) -> None:
    assert verify_input("decrypt", {"case": Case.LEDGER.value, "key": "AB"})["valid"] is False
    assert verify_input("decrypt", {"case": Case.LEDGER.value, "key": ""})["valid"] is False


def test_a_solution_whose_key_does_not_fit_its_message_is_refused(tmp_path: Path) -> None:
    given = {"case": Case.LEDGER.value}
    made = answer(Case.LEDGER, tmp_path) | {"plaintext": "NOT WHAT THE KEY GIVES"}
    verdict = verify_output("solution", given, made, tmp_path)
    assert verdict["valid"] is False and "does not turn its ciphertext into its plaintext" in verdict["message"]
