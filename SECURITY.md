# Security

## Reporting a problem

Use the private report form: this repository's **Security** tab, then **Report a vulnerability**. Only the maintainer can read it. Please don't open a public issue for a security problem.

What counts:

- A secret, token, private file or personal detail in the repo or its history
- A piece of Samsung's firmware or code committed here. The repo is meant to hold only short quoted strings, addresses and key fingerprints
- A script in `tools/` that runs a command or writes a file you didn't point it at, because of what a firmware file or bundle contains
- A step in the [how-to](docs/lineageos-howto.md) that would damage a tablet in a way the page doesn't warn about

The write-up isn't a vulnerability report: it only reads how the locks work and bypasses nothing. The unlock in the how-to is the one Samsung's own bootloader offers. A wrong claim in either is a normal issue, so use the "Something's wrong" form.

## What to expect

This is a hobby project kept by one person. A first reply usually comes within a week. Only the latest commit on the default branch is supported.
