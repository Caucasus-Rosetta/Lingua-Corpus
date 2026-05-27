# Legacy Abkhaz font encoding in BBC episodes 7, 9, 10

## Problem

The Abkhaz `.doc` files for episodes **7, 9, 10** (`data/raw/ab/docs/bbc/ab/`) were
authored with a pre-Unicode Abkhaz font. The Abkhaz-specific letters were drawn by
placing custom glyphs at ordinary code points (digits, symbols, and some unused
Cyrillic letters). The bytes stored are those code points, not the Abkhaz letters
you see on screen — the mapping lived in the *font*, not the encoding. So any text
extractor (LibreOffice, antiword, …) returns garbage like:

    Аёымшьа6ъа, щапланета=ы иаайоу аё6ъа зегьы рахьтъ х-процентк роуп иҟоу….

Episodes 1, 2, 4, 5 are NOT affected (real Unicode Abkhaz) and extract cleanly.

Affected fraction (garbage-signature tokens): ep9 ≈ 40%, ep10 ≈ 15%, ep7 ≈ 2%.

## It is a monoalphabetic substitution — and crackable

Most base Cyrillic letters pass through as themselves; only the ~13 Abkhaz special
letters are remapped. Solved by dictionary crib-dragging against the clean Abkhaz
monolingual corpus in `data/interim/ab/ab/*.txt` (iterative constraint propagation:
lock a cipher char when the decoded word is uniquely a real corpus word).

### Confirmed mapping (high confidence — decoded forms are real Abkhaz)

| cipher byte | Abkhaz letter | evidence |
|---|---|---|
| `0` | ҭ | `а8с0азаара` → аԥсҭазаара |
| `3` | ҷ | `ма3ымкъа` → маҷымкәа |
| `6` | қ | `…6ъа` → …қәа (plural suffix) |
| `8` | ԥ | `а8с0азаара` → аԥсҭазаара |
| `9` | ш | crib vote |
| `=` | ҿ | `…=ы` → …ҿы |
| `щ` | ҳ | `щапланета` → ҳапланета |
| `ъ` | ә | `…6ъа` → …қәа |
| `ё` | ӡ | `аё6ъа` → аӡқәа ("the waters") — by context, not yet auto-locked |

With the auto-locked subset, ~60% of ep9 tokens already decode to dictionary words.

### Still unresolved (lower frequency — need more crib work or a native speaker)

`1` (×7), `5` (×17), `7` (×104, the noisy `7`→х guess is suspect), `4`, `2`, `%`, `*`, `э`.
`7` is the most important remaining one by frequency.

## Status / next steps

Investigation only — **ep7/9/10 are NOT extracted or aligned**, and decoded text is
NOT committed. To finish:

1. Resolve the remaining cipher bytes (extend the crib pass; `7` especially) and have
   a native Abkhaz speaker verify the full table.
2. Add the table as a normalization step keyed to these documents (e.g. a
   `font="legacy_apsua"` option in `extract.py`'s `normalize()`), then re-extract and
   align ep7/9/10 like ep1/2/4/5.

Episodes 3, 6, 8 have a Russian `.srt` but **no Abkhaz source at all**, so they are out
of scope regardless.
