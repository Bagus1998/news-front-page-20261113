# news-image-01

An entry for make.fun's *Sum up 13 November's world news in one image*: one front page for
Friday 13 November 2026 — 33 stories, six continents, a world map and a news-in-brief column.

Every story is a real event of that day, read from AP, BBC, Al Jazeera, ISW, UNFCCC and others on
14 November 2026. Disputed claims are attributed to the side making them.

See [NOTES.md](NOTES.md) for the sourcing, what changed after review, and an honest read on placing.

## Run it

```sh
mkdir -p out && MAKEFUN_OUTPUT_DIR=out node main.ts
```

Node 22, standard library only. Copies `entry.png` to `/output/entry.png`; two runs write the same bytes.

## License

MIT, see [LICENSE](LICENSE).
