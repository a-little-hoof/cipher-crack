"""read_cipher: the puzzle as it is handed to the model."""

from .checks import result, text_problem


def verify_input(value):
    # case is an Enum member, so the only wrong value is one the type already refuses.
    return result(True, f"{value.case.value} is a case")


def verify_output(input_value, output_value, workspace):
    if output_value.case is not input_value.case:
        return result(False, f"the message is for {output_value.case.value}, not {input_value.case.value}")
    problem = text_problem(output_value.ciphertext, "ciphertext")
    if problem:
        return result(False, problem)
    return result(True, "the ciphertext is a message to work on", letters=len(output_value.ciphertext))
