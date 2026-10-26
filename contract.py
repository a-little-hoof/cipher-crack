"""Each tool's and task's typed input and output (see nanoagent.plugin.v0001.contract): declarations only."""

from dataclasses import dataclass
from enum import Enum
from typing import Annotated

from slimconfig import Output


class Tool(Enum):
    READ_CIPHER = "read_cipher"
    DECRYPT = "decrypt"
    SOLUTION = "solution"


class Task(Enum):
    CRACK_CIPHER = "crack-cipher"


class Case(Enum):
    POSTCARD = "postcard"
    DISPATCH = "dispatch"
    LEDGER = "ledger"
    TELEGRAM = "telegram"


CASE = "Which intercepted message to work on; each one was shifted by a different letter"
CIPHERTEXT = "The intercepted message, uppercase letters and spaces; spaces are not enciphered"
KEY = "The key letter, A to Z: A leaves a letter alone, B moves it on by one, and so on"
PLAINTEXT = "The message the key turns the ciphertext into, uppercase letters and spaces"


@dataclass
class CaseInput(Output):
    case: Annotated[Case, CASE]


@dataclass
class CipherOutput(Output):
    case: Annotated[Case, "The case the message belongs to"]
    ciphertext: Annotated[str, CIPHERTEXT]


@dataclass
class DecryptInput(Output):
    case: Annotated[Case, CASE]
    key: Annotated[str, "The key letter to try, A to Z"]


@dataclass
class DecryptOutput(Output):
    case: Annotated[Case, "The case the message belongs to"]
    ciphertext: Annotated[str, CIPHERTEXT]
    key: Annotated[str, "The key letter that was tried, as given without surrounding spaces"]
    plaintext: Annotated[str, "What the ciphertext reads as under that key; only one key reads as English"]


@dataclass
class SolutionOutput(Output):
    case: Annotated[Case, "The case the message belongs to"]
    ciphertext: Annotated[str, CIPHERTEXT]
    key: Annotated[str, KEY]
    plaintext: Annotated[str, PLAINTEXT]


@dataclass
class CrackOutput(Output):
    case: Annotated[Case, "The case the message belongs to, as the task gave it"]
    key: Annotated[str, KEY]
    plaintext: Annotated[str, PLAINTEXT]


TOOLS = {
    Tool.READ_CIPHER: (CaseInput, CipherOutput),
    Tool.DECRYPT: (DecryptInput, DecryptOutput),
    Tool.SOLUTION: (CaseInput, SolutionOutput),
}
TASKS = {
    Task.CRACK_CIPHER: (CaseInput, CrackOutput),
}
