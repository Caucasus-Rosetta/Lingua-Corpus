# Legacy Abkhaz font encoding in BBC episodes 7, 9, 10  — SOLVED

## Problem

The Abkhaz `.doc` files for episodes **7, 9, 10** (`data/raw/ab/docs/bbc/ab/`) were
authored with a pre-Unicode Abkhaz font. The Abkhaz-specific letters were drawn by
placing custom glyphs at ordinary code points (digits and a few unused Cyrillic
letters). The bytes stored are those code points, not the Abkhaz letters you see on
screen — the mapping lived in the *font*, not the encoding. So any extractor
(LibreOffice, antiword, …) returns garbage like:

    Аёымшьа6ъа, щапланета=ы иаайоу аё6ъа зегьы рахьтъ х-процентк роуп иҟоу….

Episodes 1, 2, 4, 5 are real Unicode Abkhaz and extract cleanly (unaffected).
Garbage-signature tokens before decoding: ep9 ≈ 40%, ep10 ≈ 15%, ep7 ≈ 2%.

## Solution — a monoalphabetic glyph substitution, cracked

Most base Cyrillic letters pass through unchanged; only the Abkhaz special letters were
remapped. Recovered by dictionary crib-dragging against the clean Abkhaz monolingual
corpus (`data/interim/ab/ab/*.txt`): greedy assignment that maximizes the number of
decoded tokens that are real corpus words, pooling all three legacy docs for signal.

Implemented in `extract.py` (`decode_legacy_apsua`, auto-triggered by
`looks_legacy_apsua`). Two classes of byte:

**Digit glyphs → letters — but only inside a Cyrillic-bearing token** (in a pure-number
token like `150` or `2,5` the digit is a real digit and is left alone):

| byte | letter |   | byte | letter |
|---|---|---|---|---|
| `0` | ҭ |   | `6` | қ |
| `3` | ҷ |   | `7` | ҵ |
| `5` | џ |   | `8` | ԥ |

**Reused Cyrillic letters (not native single Abkhaz letters) → always the letter:**

| byte | letter |
|---|---|
| `=` | ҿ |
| `щ` | ҳ |
| `ъ` | ә |
| `ё` | ӡ |
| `э` | ҽ |

**Not remapped (already correct Unicode in these docs):** `ҟ` (×256), `ҩ` (×81), and all
base Cyrillic letters. **Genuine digits (never letters):** `1 2 4` and any of `0 3 5 6 7 8`
appearing in a pure-number token. `9` is left as a digit (only seen in proper nouns like
`север-9`).

### Validation

After decoding, the garbage signature drops to ~0% on all three episodes, and decoded
word-tokens hit the clean corpus dictionary at **ep7 87% / ep9 74% / ep10 80%** (misses
are proper nouns, documentary terms, and rare inflections not in the sampled vocab — not
decode errors). Spot-checked output reads as fluent Abkhaz, e.g.:

    Аӡымшьақәа, ҳапланетаҿы иаайоу аӡқәа зегьы рахьтә х-процентк роуп иҟоу….
    Адгьыл аҿы ийоу аԥсҭазаара зегьы аӡымшьоуп изхьыԥшу.

Confirmed letters appear in known words (`џьоукы`, `иџьаушьаратәы`, `аҵаулараҿы`, `даҽа`).

## Caveats / remaining limitations

- Derived without a native speaker. Recommend an Abkhaz speaker spot-check ep7/9/10
  before the decoded text is used as final training data.
- **Capital** special letters at sentence starts may be slightly off (the analysis was
  done lowercased; the `%`/`*` bytes, seen only a handful of times, are likely
  capital-letter or punctuation positions and are left untouched).
- A digit glued directly onto a Cyrillic word (rare) would be mis-decoded as a letter.

Episodes 3, 6, 8 have a Russian `.srt` but **no Abkhaz source at all** — out of scope.
