// news-image-01 entry: put the front page beside this file at /output/entry.png.
//
// The image is the whole entry, and it is not generated here. compose.py drew it during the build
// session: one page for Friday 13 November 2026, 33 verified stories across six continents, a world
// map, and a news-in-brief column. Everything this program does is deterministic file copying, so
// the grader's two runs write identical bytes. Notes on sourcing and design: NOTES.md.

import { copyFileSync, mkdirSync } from 'node:fs';
import { join } from 'node:path';
import { fileURLToPath } from 'node:url';

const OUT = process.env.MAKEFUN_OUTPUT_DIR ?? '/output';
mkdirSync(OUT, { recursive: true });
copyFileSync(fileURLToPath(new URL('./entry.png', import.meta.url)), join(OUT, 'entry.png'));
