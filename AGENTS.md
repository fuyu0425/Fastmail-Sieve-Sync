# Fastmail Sieve Sync

A CLI (`sieve-sync`) that pulls and pushes the hand-written parts of a Fastmail Sieve script. It uses Fastmail's **unpublished** JMAP Sieve API. The project is a proof of concept: no tests, no linter, no CI.

Read `docs/fastmail-sieve.md` before you write or validate Sieve code. It lists the capabilities Fastmail supports and its delivery quirks.

## How it works

Fastmail stores the Sieve script as one `SieveBlocks` object with the id `singleton`. The object has six sections, in this order:

| JMAP field         | `Sieve` attribute | Owner                       |
|--------------------|-------------------|-----------------------------|
| `sieveRequire`     | `require`         | Fastmail (generated)        |
| `sieveAtStart`     | `_start`          | user, synced                |
| `sieveForBlocked`  | `blocked`         | Fastmail (blocked senders)  |
| `sieveAtMiddle`    | `_middle`         | user, synced                |
| `sieveForRules`    | `rules`           | Fastmail (UI rules)         |
| `sieveAtEnd`       | `_end`            | user, synced                |

A live `SieveBlocks/get` (2026-11-20) returns exactly these six fields plus `id`. The Fastmail help page says "four editable areas", but only three exist. `sieveAtMiddle` stores Fastmail's not-spam `if` wrapper around the managed block. The wrapper survives sync because only the text between the markers changes.

- `TinyJMAPClient.set_sieve` writes only `sieveAtStart`, `sieveAtMiddle`, and `sieveAtEnd`. Keep the Fastmail-owned sections read-only.
- Each user section holds one **managed block** between the exact marker lines in `sieve.py` (`HEADER_START` / `HEADER_END`). Only the text between the markers syncs. Text outside the markers stays as the remote has it.
- The local file is `str(Sieve)`: the six sections joined by `\n`. `Sieve.from_file` parses it by position. It expects exactly three marker pairs in start, middle, end order. A changed or extra marker breaks the parse silently.
- `from_file` recovers only the managed-block contents. Text outside the markers moves into the neighboring Fastmail section, so a parsed `Sieve` does not equal the original. That is why `--push` copies only `start`/`middle`/`end`.
- `Sieve.__eq__` compares only the raw `_start`, `_middle`, `_end` strings. `edit_content` calls `.strip()`, so whitespace changes can count as a change.

`main()` in `sieve_sync/sieve_sync.py` runs this flow:

1. Load the config from `--config`, or else from `$XDG_CONFIG_HOME/sieve-sync/config.toml`.
2. Get the remote script.
3. If a managed block is missing, insert it, push, write the local file, and exit. This first run ignores `--pull` and `--push`.
4. `--pull`: overwrite `SAVE_LOCATION` with the remote script. No check for local edits.
5. `--push`: copy the three managed blocks from `SAVE_LOCATION` into the remote script. Push only if they changed. Then rewrite `SAVE_LOCATION`, which also refreshes the non-managed sections from the remote.

## API gotchas

- Auth needs **both** the `fma1-…` bearer token and the `__Http-s_<id>` session cookie. Either one alone gets HTTP 401. Fastmail renamed this cookie from `__Host-s_` before 2026-11. If auth fails, test each cookie on its own against `/jmap/session`. The README shows how to get them from the browser.
- The calls use the capabilities `https://www.fastmail.com/dev/rules` and `https://www.fastmail.com/dev/user`. Fastmail checks only these two.
- `tiny_jmap_library.py` is a copy of Fastmail's `JMAP-Samples` client, with the cookie header and the `get_sieve`/`set_sieve` methods added.

## Safety

- A push or a first run changes the **live mail filters** of a real account. Get the user's approval before you run the CLI against Fastmail.
- `main()` prints the whole config, which includes the token and the cookie. Do not copy that output into commits, issues, or PRs.
- The repo `config.toml` is a template with placeholder values. Put real values only in the XDG config file. `rules.sieve` is in `.gitignore`.

## Develop

- Python `>=3.11` (for `tomllib`) and uv. Run `uv sync` to install, and `uv run sieve-sync --pull` to run. `uv tool install .` installs the CLI globally.
- Do an offline check of parser changes: compare `Sieve.from_file(str(s)).get_blocks()` with `s.get_blocks()` on a sample script. No network is necessary.
- Commit subjects use a bracket tag: `[fix] …`, `[docs] …`.
