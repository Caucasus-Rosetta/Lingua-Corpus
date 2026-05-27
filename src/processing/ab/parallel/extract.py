#!/usr/bin/env python3
"""Generic source -> normalized plain text extraction for parallel-text alignment.

This is the FORMAT layer that feeds the (format-agnostic) alignment engine in
align_bbc.py / the `bitext-aligner` subagent. The alignment stage only ever sees
plain UTF-8 text, so supporting a new container format (HTML, PDF, ODT, RTF, ...)
means adding ONE branch in `raw_text()` — nothing downstream changes. That is the
"universal/generic" property we want: extraction is pluggable, alignment is not
coupled to any source format.

Two stages, deliberately separated:

  1. raw_text(path)        container format  -> raw text
       - .srt              strip SubRip indices + timestamp lines (pure Python)
       - .doc .docx .odt   LibreOffice headless -> "Text (encoded):UTF8"
         .rtf .html .pdf     (LibreOffice honors the original encoding, which
                              matters for legacy cp1251 Abkhaz .doc files)
       - .txt              read as-is

  2. normalize(text, lang)  raw text -> canonical text  (FAITHFUL, not destructive)
       - Unicode NFC; drop BOM
       - lang="ab": Abkhaz homoglyph fixes (ҧ->ԥ, ҕ->ӷ, caps too) to match the
         codepoints used across the rest of the corpus (see process-text_ab.sh)
       - strip combining acute U+0301, soft hyphen U+00AD, form feed U+000C;
         thin space U+2009 -> normal space; join hyphenated line breaks
       - per-line trim + collapse internal runs of spaces; collapse blank-line runs

   Unlike process-text_ab.sh (the MONOLINGUAL pipeline) this does NOT lowercase,
   sentence-split, strip numbers/punctuation, sort or dedupe — alignment needs the
   text verbatim so word-index spans stay faithful and numbers/proper nouns survive
   as anchors.

For BBC, sources auto-discover from data/raw/ab/docs/bbc/{ab,ru}/ by leading
episode number. Usage:

    python extract.py --episodes 1 2 4 7 9 10   # or --all
    python extract.py --check 5                 # re-extract ep5, diff vs committed
"""
import argparse
import re
import subprocess
import sys
import tempfile
import unicodedata
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
RAW_BBC = REPO / "data" / "raw" / "ab" / "docs" / "bbc"
AB_SRC_DIR = RAW_BBC / "ab"
RU_SRC_DIR = RAW_BBC / "ru"

# Container formats LibreOffice can flatten to text. Add suffixes here to extend.
LIBRE_SUFFIXES = {".doc", ".docx", ".odt", ".rtf", ".html", ".htm", ".pdf"}

# Abkhaz homoglyphs: legacy codepoints (in many .doc files) -> canonical corpus form.
AB_HOMOGLYPHS = {"ҧ": "ԥ", "Ҧ": "Ԥ", "ҕ": "ӷ", "Ҕ": "Ӷ"}

# Characters to drop / fold regardless of language.
_DROP = {
    "\u0301": "",    # combining acute accent (stress marks)
    "\u00ad": "",    # soft hyphen
    "\u000c": "",    # form feed
    "\ufeff": "",    # BOM / zero-width no-break space
    "\u2009": " ",   # thin space -> normal space
    "\u00a0": " ",   # no-break space -> normal space
}


def strip_srt(text: str) -> str:
    """Drop SubRip cue indices and timestamp lines; keep cue text + blank lines."""
    ts = re.compile(r"^\d{2}:\d{2}:\d{2}[,.]\d{3}\s*-->")
    out = []
    for line in text.splitlines():
        s = line.strip()
        if s.isdigit():            # cue index line
            continue
        if ts.match(s):            # timestamp line
            continue
        out.append(line)
    return "\n".join(out)


def libreoffice_to_text(path: Path) -> str:
    """Convert a rich/binary document to UTF-8 plain text via headless LibreOffice."""
    with tempfile.TemporaryDirectory() as tmp:
        profile = Path(tmp) / "profile"
        cmd = [
            "soffice", "--headless",
            f"-env:UserInstallation=file://{profile}",
            "--convert-to", "txt:Text (encoded):UTF8",
            "--outdir", tmp, str(path),
        ]
        res = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
        produced = Path(tmp) / (path.stem + ".txt")
        if not produced.exists():
            raise RuntimeError(
                f"LibreOffice produced no output for {path.name}\n"
                f"stdout: {res.stdout}\nstderr: {res.stderr}"
            )
        return produced.read_text(encoding="utf-8")


def raw_text(path: Path) -> str:
    """Container format -> raw text. Dispatch by suffix (the only format-aware step)."""
    suf = path.suffix.lower()
    if suf == ".srt":
        return strip_srt(path.read_text(encoding="utf-8-sig"))
    if suf in LIBRE_SUFFIXES:
        return libreoffice_to_text(path)
    if suf == ".txt":
        return path.read_text(encoding="utf-8-sig")
    raise ValueError(f"No extractor for suffix {suf!r} ({path.name})")


def normalize(text: str, lang: str | None = None) -> str:
    """Faithful canonical normalization (see module docstring)."""
    text = unicodedata.normalize("NFC", text)
    for bad, good in _DROP.items():
        text = text.replace(bad, good)
    if lang == "ab":
        for bad, good in AB_HOMOGLYPHS.items():
            text = text.replace(bad, good)
    text = re.sub(r"(\w)-\n(\w)", r"\1\2", text)  # join intra-word hyphenated breaks only
                                                  # (leave standalone dashes, e.g. "X -\nY")
    lines = [re.sub(r"[ \t]+", " ", ln).strip() for ln in text.split("\n")]
    out, blank = [], False                       # collapse runs of blank lines
    for ln in lines:
        if ln:
            out.append(ln)
            blank = False
        elif not blank:
            out.append("")
            blank = True
    return "\n".join(out).strip("\n") + "\n"


def extract(path: Path, lang: str) -> str:
    return normalize(raw_text(path), lang=lang)


def discover() -> dict[int, dict]:
    """Map episode number -> {'ab': path, 'ru': path} by leading episode number."""
    eps: dict[int, dict] = {}
    for p in sorted(AB_SRC_DIR.glob("*")):
        m = re.match(r"\s*(\d+)\b", p.name)
        if m and p.suffix.lower() in LIBRE_SUFFIXES | {".txt"}:
            eps.setdefault(int(m.group(1)), {})["ab"] = p
    for p in sorted(RU_SRC_DIR.glob("*.srt")):
        m = re.match(r"\s*ВВС\s*(\d+)\b", p.name)
        if m:
            eps.setdefault(int(m.group(1)), {})["ru"] = p
    return eps


def out_names(ep: int) -> tuple[Path, Path]:
    return RAW_BBC / f"ВВС {ep} ab", RAW_BBC / f"ВВС {ep} ru"


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--episodes", type=int, nargs="+", help="episode numbers to extract")
    ap.add_argument("--all", action="store_true", help="extract every episode with both sides")
    ap.add_argument("--check", type=int, metavar="EP",
                    help="re-extract EP and diff against the committed 'ВВС EP ... ab/ru' files")
    args = ap.parse_args()

    eps = discover()
    if args.check is not None:
        ep = args.check
        src = eps.get(ep, {})
        committed = {
            "ab": next(RAW_BBC.glob(f"ВВС {ep}.* ab"), None),
            "ru": next(RAW_BBC.glob(f"ВВС {ep}.* ru"), None),
        }
        for side in ("ab", "ru"):
            if not src.get(side) or not committed[side]:
                print(f"  ep{ep} {side}: missing source or committed file — skip")
                continue
            got = extract(src[side], side)
            ref = committed[side].read_text(encoding="utf-8-sig")
            gw, rw = got.split(), ref.split()
            same = sum(1 for a, b in zip(gw, rw) if a == b)
            print(f"  ep{ep} {side}: extracted {len(gw)} words vs committed {len(rw)}; "
                  f"first-{min(len(gw),len(rw))} word match {same}/{min(len(gw),len(rw))}")
        return 0

    targets = sorted(eps) if args.all else (args.episodes or [])
    if not targets:
        print("Discovered episodes (ab+ru present):",
              sorted(e for e, s in eps.items() if "ab" in s and "ru" in s))
        print("ru-only (no Abkhaz source):",
              sorted(e for e, s in eps.items() if "ru" in s and "ab" not in s))
        print("\nNothing to do. Pass --episodes N... or --all.")
        return 0

    for ep in targets:
        src = eps.get(ep, {})
        if "ab" not in src or "ru" not in src:
            print(f"ep{ep}: SKIP (have {sorted(src)}, need both ab+ru)")
            continue
        ab_out, ru_out = out_names(ep)
        ab_txt = extract(src["ab"], "ab")
        ru_txt = extract(src["ru"], "ru")
        ab_out.write_text(ab_txt, encoding="utf-8")
        ru_out.write_text(ru_txt, encoding="utf-8")
        print(f"ep{ep}: {src['ab'].name} -> {ab_out.name} ({len(ab_txt.split())} words) | "
              f"{src['ru'].name} -> {ru_out.name} ({len(ru_txt.split())} words)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
