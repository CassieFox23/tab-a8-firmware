# security

## reporting a problem

use the private report form: this repository's **Security** tab, then **Report a vulnerability**. only the maintainer can read it. please don't open a public issue for a security problem.

what counts:

- a secret, token, private file or personal detail in the repo or its history
- a piece of Samsung's firmware or code committed here. the repo is meant to hold only short quoted strings, addresses and key fingerprints
- a script in `tools/` that runs a command or writes a file you didn't point it at, because of what a firmware file or bundle contains
- a step in the [how-to](docs/lineageos-howto.md) that would damage a tablet in a way the page doesn't warn about

the write-up isn't a vulnerability report: it only reads how the locks work and bypasses nothing. the unlock in the how-to is the one Samsung's own bootloader offers. a wrong claim in either is a normal issue, so use the "something's wrong" form.

## what to expect

this is a hobby project kept by one person. a first reply usually comes within a week. only the latest commit on the default branch is supported.
