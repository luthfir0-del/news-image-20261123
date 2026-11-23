#!/usr/bin/env python3
"""The World in One Day — Monday 23 November 2026.

Economist-cover edition (v3.2 design, adapted for 23 Nov): the day's
world news as The Economist "The World Ahead 2027" cover — off-white
page, small red masthead box, huge bold condensed black title, serif
teaser subtitle naming all eight stories, and a big clock-wheel below
with 12 numbered slices. Every slice carries its own line of writing
(a short headline) PLUS the news content itself: a compact summary
with the key facts and numbers (who/what/where/how many). Eight
verified stories (NATO emergency session over Poland missiles, Dymer
strike toll 11, Nikkei falls 5.06% in the AI sell-off, Iran vows all
means against a US blockade, Gaza 99% toxic, Zelenskyy seeks four-way
talks, Belgium airports shut in strike, India offers Nepal $1.6bn aid)
plus four also-today slices (BepiColombo reaches Mercury, the penny
ends, Seoul's education minister resigns, Houthis hit a Saudi
refinery), all in black and vermilion red only, each with a small flat
pictogram.

Layout verification (zoomed crops of all four wheel quadrants): the
v3.2 wedge-fit rule is kept — every line is fitted to the intersection
of the wedge spans at y-8/y/y+8, so no text is clipped by the rim or
overlaps a pictogram. One new defect was found and fixed in the 23 Nov
render: the IRAN tanker's pictogram sat on the "Trump: deal may wait"
line, hiding the word "wait" inside the black hull — the pictogram
was moved 8 degrees off the wedge mid-line (same trick as the v3.2
DEMOCRATS fix) and the line is now fully legible. Two content lines
were shortened so nothing is dropped (NATO, Mercury).

The image is drawn at build time and shipped in this repository as
entry.png; this program, the competition entrypoint, copies it to
/output/entry.png using only the standard library, so it runs in the
grading sandbox, which installs nothing and gives the program no network.

Deterministic: the same bytes every run.
"""

import os
import shutil
import struct
import sys

HERE = os.path.dirname(os.path.abspath(__file__))


def check_png(path):
    """Stdlib-only sanity check: PNG signature + 1024x1024 IHDR."""
    with open(path, "rb") as fh:
        head = fh.read(33)
    assert head[:8] == b"\x89PNG\r\n\x1a\n", "entry.png is not a PNG"
    assert head[12:16] == b"IHDR", "entry.png has no IHDR chunk"
    w, h = struct.unpack(">II", head[16:24])
    assert (w, h) == (1024, 1024), "image must be 1024x1024, got %dx%d" % (w, h)


def main():
    src = os.path.join(HERE, "entry.png")
    check_png(src)
    out = os.environ.get("ENTRY_OUT", "/output/entry.png")
    try:
        os.makedirs(os.path.dirname(out), exist_ok=True)
        shutil.copyfile(src, out)
    except OSError:
        out = os.path.join(HERE, "out", "entry.png")
        os.makedirs(os.path.dirname(out), exist_ok=True)
        shutil.copyfile(src, out)
        print("note: /output not writable, wrote", out, file=sys.stderr)
    size = os.path.getsize(out)
    print("wrote %s %d bytes" % (out, size))
    assert size <= 1024 * 1024, "image must be at most 1 MiB"
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
