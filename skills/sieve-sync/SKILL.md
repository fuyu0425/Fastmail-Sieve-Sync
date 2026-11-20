---
name: sieve-sync
description: Edit Fastmail mail filters as Sieve code with the `sieve-sync` CLI. Use when asked to add, change, or remove Fastmail filter rules or custom Sieve code, or to pull or push the Fastmail Sieve script.
---

# sieve-sync

`sieve-sync` pulls the Fastmail Sieve script to a local file and pushes the **managed blocks** back. A managed block is the text between `#### Managed by Sieve Sync Start ####` and `#### Managed by Sieve Sync End ####`. Only managed-block text goes to Fastmail. Everything else in the file is Fastmail-generated and is overwritten on every pull or push.

Repo: `/Users/fuyu0425/tools/Fastmail-Sieve-Sync`. Config: `~/.config/sieve-sync/config.toml`.

## Steps

1. **Find the file.** Read `SAVE_LOCATION` from the config. If the path is relative, run every command in the repo folder. Done when you know the absolute path of the rules file.
2. **Pull before edit.** A pull overwrites the local file with no check, so pull first and edit after:
   ```bash
   sieve-sync --pull
   ```
   Done when the output says `updated rules is saved to …`.
3. **Pick the managed block.** The file has three, in this order:
   - **Top**, after `require`: runs before blocked senders and spam scoring.
   - **Middle**, inside Fastmail's `if not string :is "${spam}" "Y"` wrapper: runs only on non-spam, before the UI rules. Use this one by default.
   - **Bottom**, at the end: runs after the UI rules. Mail that a rule sends to Trash or Spam never gets here.
4. **Write the Sieve.** Edit only between the markers. Keep every marker line exact. Use only capabilities in the file's `require` line. Read `/Users/fuyu0425/tools/Fastmail-Sieve-Sync/docs/fastmail-sieve.md` before you write the rule. It lists the supported capabilities, the rule variables you can set in the middle block (`skipinbox`, `stop`, `read`, …), and Fastmail quirks. Done when every action and test in your code has a matching capability.
5. **Check it offline.** The parse must give back your blocks:
   ```bash
   cd /Users/fuyu0425/tools/Fastmail-Sieve-Sync && uv run python -c "from sieve_sync.sieve import Sieve; import sys; print(Sieve.from_file(open(sys.argv[1]).read()).get_blocks())" <rules-file>
   ```
6. **Get approval.** A push changes the live mail filters of a real account. Show the user the new managed-block text and get a yes for this exact change.
7. **Push:**
   ```bash
   sieve-sync --push
   ```
   The output says `push to remote` or `no change so far; skip pushing`.
8. **Confirm with a fresh pull.** The CLI does not check the JMAP result, so a script that Fastmail rejects fails silently. Pull again (step 2) and run the step 5 check. Done when the pulled managed blocks equal what you pushed.

## Failures

- **HTTP 401** at `/jmap/session`: the token or the cookie has expired. Ask the user to copy fresh values from the browser (see the repo `README.md`): the `fma1-…` bearer token and the `__Http-s_<id>` cookie. Pasting the whole `Cookie` header also works.
- **A managed block is missing remotely**: the next run of either command adds it, pushes, writes the file, and exits. Run the command again to do the real pull or push.
- **Time-based actions** (for example "delete after 10 minutes"): Sieve runs once at delivery and has no timer. Tell the user that this needs an external job.
