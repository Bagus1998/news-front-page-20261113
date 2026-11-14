// news-image-01 entry: copy the front page beside this file to /output/entry.png.
//
// The image is the entry: a one-page front page for Friday 13 November 2026, 33 verified stories
// across six continents, a world map and a news-in-brief column. It is drawn by compose.py in the
// build session, not by this program; see NOTES.md for the sources and the design reasoning.

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';

const OUT = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(OUT, { recursive: true });
copyFileSync(new URL('./entry.png', import.meta.url), join(OUT, 'entry.png'));
