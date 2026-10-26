# Cipher Crack

Each case holds a short message enciphered by moving every letter on by a fixed
amount, and the key is not given. The task is to find it. The plugin is a
standard MCP server over stdio; NanoAgent owns its launch command, environment,
input and output checks and lifecycle.

## Tools

| Tool | Does | Code |
|---|---|---|
| `read_cipher` | Returns a case's intercepted message, still enciphered. Spaces were left alone, so word lengths survive | `src/plugin/messages.py` |
| `decrypt` | Returns what a case's message reads as under one key letter. It says nothing about whether that key is the right one | `src/plugin/messages.py` |
| `solution` | Returns a case's key, ciphertext and message. It is `crack-cipher`'s reference tool, so no task lists it and the model never sees its output | `src/plugin/messages.py` |

### Tasks

| Task | Does | Runner |
|---|---|---|
| `crack-cipher` | Finds the key a case's message was enciphered with and reads the message | `agent`, with `read_cipher` and `decrypt`, against the `solution` reference |

The four messages (`postcard`, `dispatch`, `ledger`, `telegram`) are invented,
so the plaintext cannot be recalled from anywhere: the only way to it is
through the key. Each case uses a different key letter.

Deciphering under a given key follows from the rule, so `decrypt` computes it.
What no rule settles is which of the twenty-six readings is English, and that
is the whole of the model's job. The verifier never has to make that judgement:
it compares the submission against the reference answer.

A submission is a case, a key and a message, and it has to hold together.
`verify_task` deciphers the reference ciphertext under the submitted key and
checks that it really gives the submitted message, then checks that message
against the reference. Those two checks also settle the key, because a shift
cipher sends different keys to different messages. A wrong answer is scored by
how many characters it gets right, so a single wrong letter scores just under
one while a wrong key scores near zero.

## Layout

It has the standard plugin layout, which NanoAgent requires:

```text
.
├── nanoagent.yaml   # manifest (a slimconfig ManifestConfig): id, runtime, permissions, tools, tasks
├── contract.py      # each tool's and task's typed input and output: slimconfig Output classes
├── README.md
├── LICENSE
├── pyproject.toml
├── uv.lock
├── .gitignore
├── .env             # needed environment variable names (none here)
├── src/plugin/      # the MCP server (__main__.py, its IMPLEMENTATIONS table), cases.py and the tools
├── tests/           # test_verifier.py and test_cipher.py, the design's invariants
├── ui/              # how the page draws the outputs: renderers.js and renderers.css
├── product/         # the product page a catalog shows: product.yaml and icon.svg
└── verifier/        # deterministic verifier package: checks.py, cipher.py, attempt.py and answer.py
```

`contract.py` types every value: the server builds each call's input into its
class and checks its output against its own, and NanoAgent and the verifier
get the same classes. A failing tool raises, and the MCP server returns an
error result.

`verifier/` is deterministic and imports nothing but `contract` and its own
package. Because it may not import the plugin, it writes the shift cipher out
again and deciphers everything itself: it takes no tool's word for what a key
does, including the reference tool's, whose key and message it checks against
each other before using them. `tests/test_cipher.py` holds the two
implementations in step and keeps every case's key distinct.

A case's ciphertext is derived from its message, never stored, so the two
cannot drift apart.

## Develop and run

```bash
uv sync --extra dev
uv run pytest
```

NanoAgent passes the folder the plugin may write to as `NANOAGENT_WORKSPACE`.
No tool writes to it: every case is held in `src/plugin/cases.py`, so a run
needs no network and no files.
