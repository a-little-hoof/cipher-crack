"""solution (the crack-cipher reference) and the crack-cipher task's own check."""

from .checks import agreement, decipher, key_problem, result, text_problem


def verify_input(value):
    return result(True, f"{value.case.value} is a case")


def _answer_problem(value, label):
    """What is wrong with a (ciphertext, key, plaintext) triple, or None."""
    problem = (
        key_problem(value.key)
        or text_problem(value.ciphertext, f"{label} ciphertext")
        or text_problem(value.plaintext, f"{label} plaintext")
    )
    if problem:
        return problem
    if decipher(value.ciphertext, value.key) != value.plaintext:
        return f"{label} key {value.key} does not turn its ciphertext into its plaintext"
    return None


def verify_output(input_value, output_value, workspace):
    if output_value.case is not input_value.case:
        return result(False, f"the answer is for {output_value.case.value}, not {input_value.case.value}")
    problem = _answer_problem(output_value, "the answer's")
    if problem:
        return result(False, problem)
    return result(True, f"{input_value.case.value} is answered by key {output_value.key}")


def verify_task(arguments, output, reference, workspace):
    """crack-cipher: the submitted key and message judged against the answer the model never saw."""
    if output.case is not arguments.case:
        return result(False, f"the answer is for {output.case.value}, not {arguments.case.value}")
    key = output.key.strip().upper()
    said = output.plaintext.strip().upper()
    problem = key_problem(key) or text_problem(said, "plaintext")
    if problem:
        return result(False, problem)
    if reference.case is not arguments.case:
        return result(False, f"the reference answer is for {reference.case.value}, not {arguments.case.value}")
    # The verifier does not take the reference tool's word for it either.
    problem = _answer_problem(reference, "the reference")
    if problem:
        return result(False, problem)
    # These two checks also settle the key: a shift cipher sends different keys to different
    # messages, so a submission that is self-consistent and reads right can only be key reference.key.
    reads_as = decipher(reference.ciphertext, key)
    if reads_as != said:
        return result(
            False,
            f"key {key} turns the ciphertext into {reads_as!r}, which is not the message submitted",
            score=agreement(said, reference.plaintext),
        )
    if said != reference.plaintext:
        return result(
            False,
            f"key {key} is not the key: the message was enciphered with {reference.key}",
            score=agreement(said, reference.plaintext),
            submitted=said,
        )
    return result(True, f"{arguments.case.value} is cracked: key {key}", letters=len(reference.plaintext))
