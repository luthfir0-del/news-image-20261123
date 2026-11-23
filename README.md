# The World in One Day — Monday 23 November 2026

[![news-image-20261123](https://img.shields.io/badge/make.fun-news--image--20261123-blue)](https://make.fun/bounty/news-image-20261123)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A single-file Python program that draws an Economist-style "World Ahead"
cover for one day of world news: **Monday 23 November 2026**. The cover
carries twelve verified stories from that day on a twelve-slice clock wheel,
with the masthead *The World In One Day*, a condensed headline, a red date
line, a four-line serif subtitle, and a pictogram in every slice.

## The twelve stories

1. NATO holds an emergency Brussels session after three Russian Kh-101
   missiles cross into Polish airspace.
2. A drone strike on Dymer, Ukraine, kills 11; a seven-year-old boy is
   pulled out alive after about fourteen hours.
3. The Nikkei drops 5.06% as an AI sell-off spreads; the S&P 500 falls 3.7%.
4. Iran vows to use all available means against a US naval blockade; a
   nuclear deal may have to wait until 2027.
5. Oxfam reports war has left toxic pollution across 99% of Gaza.
6. Zelenskyy pushes for four-way talks with Russia as soon as possible.
7. Belgian air-traffic controllers join an anti-austerity strike; airports
   shut and flights are grounded.
8. India pledges $1.6bn in aid to Nepal as Prime Minister Balen Shah makes
   his first foreign trip.
9. BepiColombo enters Mercury orbit after eight years; ESA probes a
   thruster glitch.
10. Trump signs the Common Cents Act, ending the penny's 232-year run.
11. South Korea's education minister resigns over an exam-cheating
    scandal.
12. Houthis claim a strike on the Rabigh refinery; a Saudi strike on
    Hodeida kills four and wounds eighteen.

## Run it

Python 3.13, standard library only — no third-party packages, no fonts,
no network. The program writes a 1024×1024 PNG:

```sh
python3 main.py
```

It writes to `$MAKEFUN_OUTPUT_DIR/entry.png` (default `/output`).
Output is deterministic: two runs produce byte-identical files.
All letterforms are drawn from a built-in 5×7 bitmap font, and the PNG
is encoded with the standard library (`struct` + `zlib`). The program
also prints a fit warning to stderr if any line would overflow its
wedge, so a bad line break is caught before the image ships.

## Layout

The wheel is centred at (512, 664) with a 290 px rim and a rosette
marked "23". Each slice's text block is centred on its mid-ray at
radius 190 px, in plain screen coordinates, so the sideways slices
read left to right like the top and bottom ones. Every line is checked
against its wedge span before it is drawn.
