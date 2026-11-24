#!/usr/bin/env python3
"""The One-Line Exit — entry program.

Publishes the authored entry in entry.txt (shipped beside this file)
to /output/entry.txt, byte for byte: the raw bytes are read from
entry.txt and written unchanged, so the published file is identical
to the authored one. No trailing newline is added or stripped.

The gate requires UTF-8 text of 1 to 140 characters, not only white
space, on exactly one line — one resignation letter, funny, that a
person could actually send.
"""

import argparse
import os
import sys

MAX_CHARS = 140
DEFAULT_OUTPUT = "/output/entry.txt"


def entry_path():
    """Return the path of the authored entry file shipped with this program."""
    here = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(here, "entry.txt")


def load_bytes(path=None):
    """Read the authored entry as raw bytes, unchanged.

    The bytes are returned exactly as stored in entry.txt: nothing is
    stripped, re-encoded, or reformatted, so a trailing newline in the
    file would survive into the published output — the file is
    authored without one.
    """
    with open(path or entry_path(), "rb") as handle:
        return handle.read()


def decode_entry(raw):
    """Decode the raw entry bytes as UTF-8 text for validation."""
    return raw.decode("utf-8")


def validate(line, max_chars=MAX_CHARS):
    """Check the decoded line against the competition gate.

    Returns a list of problems; an empty list means the line is valid.
    The gate is: 1 to ``max_chars`` characters, not only white space,
    and a single line (no embedded newline characters).
    """
    problems = []
    if not line:
        problems.append("entry is empty")
    if line.strip() == "":
        problems.append("entry is only white space")
    if len(line) > max_chars:
        problems.append(
            "entry is %d characters, over the %d-character limit"
            % (len(line), max_chars)
        )
    if "\n" in line or "\r" in line:
        problems.append("entry must be exactly one line")
    if line != line.strip():
        problems.append("entry has leading or trailing white space")
    lowered = line.lower()
    resign_words = ("resign", "quit", "leaving", "notice", "farewell",
                    "last day", "stepping down")
    if not any(word in lowered for word in resign_words):
        problems.append("entry should read like a resignation letter")
    return problems


def publish(raw, path=DEFAULT_OUTPUT):
    """Write the raw entry bytes unchanged to ``path``.

    The file is opened in binary mode and the bytes are written as
    read, so the published file is byte-identical to entry.txt.
    """
    directory = os.path.dirname(path)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(path, "wb") as handle:
        handle.write(raw)
    return path


def describe(line):
    """Return a one-line summary of the entry for local checks."""
    words = line.split()
    return "%d characters, %d words, %d bytes as UTF-8" % (
        len(line),
        len(words),
        len(line.encode("utf-8")),
    )


def parse_args(argv=None):
    """Parse the command-line options.

    ``--out`` chooses where the entry is written (default
    /output/entry.txt, the path the grader reads). ``--check-only``
    validates the entry and writes nothing, for a quick local check.
    ``--max-chars`` lets a local check enforce a tighter limit than
    the competition gate.
    """
    parser = argparse.ArgumentParser(
        description="Publish the one-line resignation letter."
    )
    parser.add_argument(
        "--out",
        default=DEFAULT_OUTPUT,
        help="path to write the entry to (default: %(default)s)",
    )
    parser.add_argument(
        "--check-only",
        action="store_true",
        help="validate the entry without writing anything",
    )
    parser.add_argument(
        "--max-chars",
        type=int,
        default=MAX_CHARS,
        help="character limit to validate against (default: %(default)s)",
    )
    return parser.parse_args(argv)


def main(argv=None):
    """Read entry.txt, validate it, and publish its bytes verbatim."""
    args = parse_args(argv)
    try:
        raw = load_bytes()
    except OSError as exc:
        print("cannot read entry.txt: %s" % exc, file=sys.stderr)
        return 1
    try:
        line = decode_entry(raw)
    except UnicodeDecodeError:
        print("invalid entry: entry.txt is not valid UTF-8", file=sys.stderr)
        return 1
    problems = validate(line, max_chars=args.max_chars)
    if problems:
        for problem in problems:
            print("invalid entry: %s" % problem, file=sys.stderr)
        return 1
    if args.check_only:
        print("entry valid: %s" % describe(line))
        return 0
    publish(raw, path=args.out)
    print("wrote %d bytes to %s" % (len(raw), args.out))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
