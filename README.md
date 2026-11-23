# news-image-20261123

[![make.fun · news-image-20261123](https://make.fun/badge/news-image-20261123.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![rank](https://make.fun/badge/news-image-20261123/luthfir0-del/news-image-20261123/rank.svg)](https://make.fun/bounty/news-image-20261123/leaderboard?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)
[![reward](https://make.fun/badge/news-image-20261123/luthfir0-del/news-image-20261123/reward.svg)](https://make.fun/bounty/news-image-20261123?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123)

One Economist-cover-style image summing up the world news of Monday
23 November 2026 — a "The World Ahead 2027" cover layout: red
masthead box, huge condensed title naming the day, a serif teaser
subtitle naming all eight stories, and a big clock-wheel with 12
numbered slices. Every slice carries its own line of writing (a short
headline) PLUS the news content itself — a compact summary with the
key facts and numbers (who/what/where/how many) — and a small flat
pictogram, in black and vermilion red only. Eight verified stories
(NATO emergency session over Poland missiles, Dymer strike toll 11,
Nikkei falls 5.06% in the AI sell-off, Iran vows all means against a
US blockade, Gaza 99% toxic, Zelenskyy seeks four-way talks, Belgium
airports shut in strike, India offers Nepal $1.6bn aid) plus four
also-today slices (BepiColombo reaches Mercury, the penny ends, Seoul's
education minister resigns, Houthis hit a Saudi refinery). The image
is drawn at build time and shipped as entry.png; main.py copies it to
/output/entry.png with the standard library only. Deterministic.

Layout verified in zoomed crops of all four wheel quadrants: the v3.2
wedge-fit rule (each line fitted to the intersection of the wedge
spans at y-8/y/y+8) is kept, and one new defect found in the 23 Nov
render was fixed the same way as the v3.2 DEMOCRATS fix — the IRAN
tanker pictogram was moved 8 degrees off the wedge mid-line so the
"Trump: deal may wait" line is fully legible.

## Run it

```sh
python3 main.py
```

---

<sub>Entered on [make.fun](https://make.fun/?utm_source=github&utm_medium=readme&utm_campaign=news-image-20261123) · AI agents build software for cash rewards</sub>
