"""decrypt: one attempt at a case, which must really be what that key reads as."""

from .checks import decipher, key_problem, result, text_problem


def verify_input(value):
    problem = key_problem(value.key.strip().upper())
    if problem:
        return result(False, problem)
    return result(True, "the key is a letter to try")


def verify_output(input_value, output_value, workspace):
    if output_value.case is not input_value.case:
        return result(False, f"the attempt is on {output_value.case.value}, not {input_value.case.value}")
    if output_value.key != input_value.key.strip().upper():
        return result(False, "output must report the key it was given")
    problem = key_problem(output_value.key) or text_problem(output_value.ciphertext, "ciphertext")
    if problem:
        return result(False, problem)
    problem = text_problem(output_value.plaintext, "plaintext")
    if problem:
        return result(False, problem)
    read_as = decipher(output_value.ciphertext, output_value.key)
    if read_as != output_value.plaintext:
        return result(False, f"key {output_value.key} turns the ciphertext into {read_as!r}, not the plaintext given")
    return result(True, f"the ciphertext under key {output_value.key} really reads as the plaintext given")
