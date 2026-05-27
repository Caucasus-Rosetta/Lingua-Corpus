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

**Reused Cyrillic letters (none is a native single Abkhaz letter) → always the letter.**
Capital forms (used at sentence starts) map to the capital Abkhaz letter:

| byte | letter |   | byte | letter |
|---|---|---|---|---|
| `=` | ҿ |   | `й` | ҟ |
| `щ` | ҳ / `Щ` Ҳ |   | `ю` | ҩ |
| `ъ` | ә / `Ъ` Ә |   | `Й` | Ҟ |
| `ё` | ӡ / `Ё` Ӡ |   | `Ю` | Ҩ |
| `э` | ҽ / `Э` Ҽ |   |  |  |

Because `й → ҟ`, the cluster `йь` decodes to the genuine Abkhaz digraph `ҟь` with no special
case (e.g. `шеилйьоу → еилҟьоу`).

**Not remapped (already correct Unicode where present):** all base Cyrillic letters, and the
real `ҟ`/`ҩ` that some docs *also* contain (see "mixed encoding" below). **Genuine digits
(never letters):** `1 2 4` and any of `0 3 5 6 7 8` appearing in a pure-number token. `9` is
left as a digit (only seen in proper nouns like `север-9`).

**Mixed encoding within a document:** the three docs are not uniformly legacy. ep7 carries
real Unicode `ҟ` (×154) and `ҩ` (×40) *alongside* a handful of `й`/`ю` font glyphs
(`ийоуп`, `Амюан`, `Ақәаршюы`…); ep10 likewise mixes real `ҟ`/`ҩ` with `й`/`ю`; ep9 is
almost entirely legacy (`ҟ` ×1). Mapping `й→ҟ`/`ю→ҩ` cannot double-map — the real `ҟ`/`ҩ`
are already those codepoints, not `й`/`ю`.

### Validation

After decoding, the garbage signature drops to ~0% on all three episodes, and decoded
word-tokens hit the clean corpus dictionary at **ep7 91% / ep9 86% / ep10 87%** (after the
`й`/`ю`/capital additions; up from 87/74/80% before — misses are proper nouns, documentary
terms, and rare inflections not in the sampled vocab, not decode errors). No `й`/`ю`/`Й`/`Ю`/
`Щ`/`Э` glyphs remain in any of the three files. Spot-checked output reads as fluent Abkhaz,
e.g.:

    Аӡымшьақәа, ҳапланетаҿы иаайоу аӡқәа зегьы рахьтә х-процентк роуп иҟоу….
    Адгьыл аҿы ийоу аԥсҭазаара зегьы аӡымшьоуп изхьыԥшу.

Confirmed letters appear in known words (`џьоукы`, `иџьаушьаратәы`, `аҵаулараҿы`, `даҽа`).

## Caveats / remaining limitations

- Derived without a native speaker. Recommend an Abkhaz speaker spot-check ep7/9/10
  before the decoded text is used as final training data. One rare term to check:
  `хәйьайьарақәа → хәҟьаҟьарақәа` (mountain ranges) has no corpus hit — the mapping is
  consistent with all other evidence, but the word itself is unverified.
- **Capital** special letters at sentence starts are now handled (`Щ Ъ Ё Э Й Ю` →
  `Ҳ Ә Ӡ Ҽ Ҟ Ҩ`). A few stray bytes (`“ ” ´ \ _`, single occurrences) are LibreOffice
  conversion noise, not font glyphs, and are left untouched.
- A digit glued directly onto a Cyrillic word (rare) would be mis-decoded as a letter.
- `looks_legacy_apsua` keys only on digit glyphs; all three episodes trigger via those. A
  hypothetical doc with *only* `й`/`ю` glyphs (no digit glyphs) would not auto-detect.

Episodes 3, 6, 8 have a Russian `.srt` but **no Abkhaz source at all** — out of scope.
