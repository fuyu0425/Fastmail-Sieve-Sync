# Fastmail Sieve support

Scraped on 2026-11-20 from:

- [Using Sieve scripts in Fastmail](https://www.fastmail.help/hc/en-us/articles/1500000280481)
- [How to use Sieve](https://www.fastmail.help/hc/en-us/articles/360060591373)
- [Sieve frequently asked questions](https://www.fastmail.help/hc/en-us/articles/360058753814)
- [Sieve examples](https://www.fastmail.help/hc/en-us/articles/360058753794)
- The live **Edit Sieve script** screen (Settings → Filters & Rules → Edit custom Sieve code)
- Cyrus docs: [Cyrus Sieve](https://www.cyrusimap.org/imap/reference/admin/sieve.html), [Cyrus Sieve extensions](https://www.cyrusimap.org/dev/reference/extensions/sieve.html)

## Version

Sieve has no version number. A server states what it supports with the base RFC plus a list of extension capabilities.

- Base language: [RFC 5228](https://datatracker.ietf.org/doc/html/rfc5228). The Fastmail help page links "Sieve language reference" to RFC 6785. That is an error: RFC 6785 is the IMAP Events extension.
- Engine: Cyrus IMAP Sieve. The `vnd.cyrus.*` capabilities in the `require` line show this.
- The `require` line in the generated script is the source of truth for the capabilities that you can use.

## Capabilities

The live editor shows this `require` line:

```sieve
require ["fileinto", "reject", "vacation", "envelope", "body", "relational", "regex", "subaddress", "copy", "mailbox", "mboxmetadata", "servermetadata", "date", "index", "comparator-i;ascii-numeric", "variables", "imap4flags", "editheader", "duplicate", "vacation-seconds", "fcc", "vnd.cyrus.jmapquery", "vnd.cyrus.log", "mailboxid", "special-use", "vnd.cyrus.snooze", "processcalendar", "vnd.cyrus.implicit_keep_target"];
```

The help page shows an older line. It has `vnd.cyrus.imip` where the live editor has `processcalendar`.

| Capability | Adds | Spec |
|---|---|---|
| `fileinto` | `fileinto` action | [RFC 5228](https://datatracker.ietf.org/doc/html/rfc5228) |
| `envelope` | `envelope` test | [RFC 5228](https://datatracker.ietf.org/doc/html/rfc5228) |
| `reject` | `reject` action | [RFC 5429](https://datatracker.ietf.org/doc/html/rfc5429) |
| `vacation` | `vacation` action (autoreply) | [RFC 5230](https://datatracker.ietf.org/doc/html/rfc5230) |
| `vacation-seconds` | `:seconds` for `vacation` | [RFC 6131](https://datatracker.ietf.org/doc/html/rfc6131) |
| `relational` | `:count`, `:value` match types | [RFC 5231](https://datatracker.ietf.org/doc/html/rfc5231) |
| `comparator-i;ascii-numeric` | numeric comparator | [RFC 4790](https://datatracker.ietf.org/doc/html/rfc4790), [RFC 5228 §2.7.3](https://datatracker.ietf.org/doc/html/rfc5228#section-2.7.3) |
| `body` | `body` test | [RFC 5173](https://datatracker.ietf.org/doc/html/rfc5173) |
| `regex` | `:regex` match type (POSIX extended) | [draft-murchison-sieve-regex-07](https://datatracker.ietf.org/doc/draft-murchison-sieve-regex/) (IANA), [draft-ietf-sieve-regex](https://datatracker.ietf.org/doc/draft-ietf-sieve-regex/) (Cyrus). Both expired |
| `subaddress` | `:user`, `:detail` address parts | [RFC 5233](https://datatracker.ietf.org/doc/html/rfc5233) |
| `copy` | `:copy` for `fileinto` / `redirect` | [RFC 3894](https://datatracker.ietf.org/doc/html/rfc3894) |
| `mailbox` | `mailboxexists` test, `:create` | [RFC 5490](https://datatracker.ietf.org/doc/html/rfc5490) |
| `mboxmetadata`, `servermetadata` | `metadata`, `servermetadata` tests | [RFC 5490](https://datatracker.ietf.org/doc/html/rfc5490) |
| `date` | `date`, `currentdate` tests | [RFC 5260](https://datatracker.ietf.org/doc/html/rfc5260) |
| `index` | `:index`, `:last` | [RFC 5260](https://datatracker.ietf.org/doc/html/rfc5260) |
| `variables` | `set`, `${var}`, `string` test | [RFC 5229](https://datatracker.ietf.org/doc/html/rfc5229) |
| `imap4flags` | `setflag`, `addflag`, `removeflag`, `hasflag` | [RFC 5232](https://datatracker.ietf.org/doc/html/rfc5232) |
| `editheader` | `addheader`, `deleteheader` | [RFC 5293](https://datatracker.ietf.org/doc/html/rfc5293) |
| `duplicate` | `duplicate` test | [RFC 7352](https://datatracker.ietf.org/doc/html/rfc7352) |
| `fcc` | `:fcc` for `vacation` | [RFC 8580](https://datatracker.ietf.org/doc/html/rfc8580) |
| `mailboxid` | `:mailboxid` for `fileinto` | [RFC 9042](https://datatracker.ietf.org/doc/html/rfc9042) |
| `special-use` | `:specialuse` for `fileinto` | [RFC 8579](https://datatracker.ietf.org/doc/html/rfc8579) |
| `processcalendar` | `processcalendar` action (calendar invites) | [RFC 9671](https://datatracker.ietf.org/doc/html/rfc9671) |
| `vnd.cyrus.jmapquery` | `jmapquery` test with a JSON [JMAP Email filter](https://datatracker.ietf.org/doc/html/rfc8621#section-4.4.1) | [Cyrus](https://www.cyrusimap.org/dev/reference/extensions/sieve.html#vnd-cyrus-jmapquery) |
| `vnd.cyrus.log` | `log` action (server syslog) | [Cyrus](https://www.cyrusimap.org/dev/reference/extensions/sieve.html#vnd-cyrus-log) |
| `vnd.cyrus.snooze` | `snooze` action (`:mailbox`, `:weekdays`, `:tzid`, `:addflags`, `:removeflags`) | [Cyrus](https://www.cyrusimap.org/dev/reference/extensions/sieve.html#snooze), [draft-ietf-extra-sieve-snooze](https://datatracker.ietf.org/doc/draft-ietf-extra-sieve-snooze/) (expired) |
| `vnd.cyrus.implicit_keep_target` | `implicit_keep_target` action: send the implicit keep to a mailbox other than INBOX | [Cyrus](https://www.cyrusimap.org/dev/reference/extensions/sieve.html#vnd-cyrus-implicit-keep-target) |

RFC numbers match the [IANA Sieve extensions registry](https://www.iana.org/assignments/sieve-extensions/sieve-extensions.xhtml), checked on 2026-11-20.

Cyrus also supports `enotify`, `include`, `extlists`, and `ihave`. Fastmail does not list them in the `require` line.

## Execution model

- Sieve runs only on incoming mail, on the server, at delivery. It does not filter sent mail.
- Sieve runs after the SMTP connection closes. A `reject` cannot refuse mail before SMTP `DATA`.
- The script runs for all clients (web, IMAP, POP).
- Fastmail generates Sieve code from the Settings screens (rules, spam protection, blocked senders). The help page says the editor shows four generated blocks, separated by four editable text areas. The live API has only three editable fields (see below).
- Code runs top to bottom. Put custom code below the spam block in most cases. Put it in the top area only to run before spam filtering.

## Live script layout

Checked on 2026-11-20 against a full copy from the Fastmail editor and a live `SieveBlocks/get` response.

| # | Part | Editable | Field |
|---|---|---|---|
| 1 | `require [...]` | no | `sieveRequire` |
| 2 | Top custom area | yes | `sieveAtStart` |
| 3 | Save-on-SMTP identities, blocked senders, disabled masked email, spam protection, MailFetch implicit keep, MailFetch junk source, address rules | no | `sieveForBlocked` |
| 4 | Middle custom area, inside `if not string :is "${spam}" "Y" { ... }` | yes | `sieveAtMiddle` |
| 5 | "Calculate rule actions", then "Execute rule actions" (calendar, deferred `fileinto`, vacation), then an empty `if string :is "${stop}" "Y"` | no | `sieveForRules` |
| 6 | Bottom custom area | yes | `sieveAtEnd` |

What each custom area sees:

- **Top** runs before spam scoring. Blocked senders and the spam check have not run yet.
- **Middle** runs only when the message is not spam. The `if not string :is "${spam}" "Y" { … }` wrapper, with a comment "added by Fastmail", is stored inside `sieveAtMiddle`. It runs before the rules, so it can set the variables that the rules read.
- **Bottom** runs after the rule actions. A message that a rule sends to Trash or Spam stops before this area.

Variables that the generated rules use. Code in the middle area can set them:

| Variable | Effect when `"Y"` |
|---|---|
| `stop` | Skip every later rule |
| `skipinbox` | No Inbox copy. Archive, unless a rule filed the message into a folder |
| `read` | Mark read |
| `flagged` | Flag |
| `deletetotrash` | Move to Trash and stop |
| `notify` | `addflag "$notify"` (push notification) |
| `spam` | Set by the spam block. `"Y"` sends the message to Spam |
| `L<n>_<folder>` | File a copy into that folder (`fileinto :copy :mailboxid`) |

Rules test a folder with `mailboxidexists "<id>"` and file by mailbox ID, so a renamed folder keeps working.

## Editing and testing

- Fastmail does not support ManageSieve. The web UI is the only official way to edit the script.
- Settings → Filters & Rules → **Import** / **Export** moves scripts as `.json` files.
- The [Sieve tester](https://app.fastmail.com/sievetester/) runs a full script against a pasted raw message.

## Fastmail-specific behavior

- Folder names are `INBOX.<name>`, or `INBOX` for the Inbox. They are case-sensitive. Copy the name from Settings → Filters & Rules.
- `fileinto` to a missing folder files the message into the Inbox and runs no other action. A renamed folder causes the same result.
- `discard` deletes mail permanently and bypasses Fastmail backups. Test a rule with `fileinto` first.
- `addflag "$notify";` sends a push notification to the Fastmail app.
- `addflag "\\Seen"`, `"\\Deleted"`, `"\\Flagged"` mark a message read, deleted, or flagged.
- `X-Spam-known-sender: yes` marks mail from a contact. See [email delivery headers](https://www.fastmail.help/hc/en-us/articles/1500000278262#headers) for the other headers that Fastmail adds. S/MIME results are in `Authentication-Results`.
- `redirect :copy` forwards **and** keeps the Inbox copy. Plain `redirect` cancels the implicit keep, so no Inbox copy stays ([RFC 3894 §3](https://datatracker.ietf.org/doc/html/rfc3894#section-3)). The FAQ answers "Why do I get copies in the Inbox when using forwarding rules?" with `redirect :copy`. That answer conflicts with the RFC. Follow the RFC, and test with the Sieve tester.
- For a backup forward, run exactly one of `keep` or `fileinto` for each message, in addition to the `redirect`.
- `:over` and `:under` work only with the `size` test.
- The FAQ warns that a match against `""` sometimes fails. Use `exists` to test for a header.
