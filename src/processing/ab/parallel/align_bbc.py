#!/usr/bin/env python3
"""Feasibility experiment: LLM sentence-alignment of BBC parallel text (ab <-> ru).

The Abkhaz side is prose narration extracted from Word docs; the Russian side is
subtitle text (cues) extracted from .srt. The two are segmented completely
differently, so this aligns them with an LLM (via OpenRouter, OpenAI-compatible).

Design: NO heuristic sentence segmentation. Each side is split only into numbered
*word tokens*. The LLM owns both segmentation and alignment by returning inclusive
*word-range spans* (so it can split within a line). It emits only word indices,
never text; the script rebuilds every pair by joining the source words in the
range, so the output text is provably verbatim from the source.

Usage:
    OPENROUTER_API_KEY=... python align_bbc.py --episode 5 \
        [--models google/gemini-3.1-pro-preview anthropic/claude-opus-4.7]
"""
import argparse
import json
import os
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[4]
RAW_BBC = REPO / "data" / "raw" / "ab" / "docs" / "bbc"
OUT_DIR = REPO / "data" / "interim" / "ab" / "bbc"

# episode -> (ab filename, ru filename) of the already-extracted plain-text pair.
# Produced by extract.py. ep5 keeps its original (manually-curated) filenames.
# ep7/9/10 use a legacy non-Unicode Abkhaz font, recovered by extract.py's
# decode_legacy_apsua (see legacy_abkhaz_font.md). ep3/6/8 have no Abkhaz source.
EPISODES = {
    1: ("ВВС 1 ab", "ВВС 1 ru"),
    2: ("ВВС 2 ab", "ВВС 2 ru"),
    4: ("ВВС 4 ab", "ВВС 4 ru"),
    5: ("ВВС 5. Ашьхақәа ab", "ВВС 5. Ашьхақәа ru"),
    7: ("ВВС 7 ab", "ВВС 7 ru"),
    9: ("ВВС 9 ab", "ВВС 9 ru"),
    10: ("ВВС 10 ab", "ВВС 10 ru"),
}

DEFAULT_MODELS = [
    "google/gemini-3.1-pro-preview",
    "anthropic/claude-opus-4.7",
]


def tokenize(path: Path) -> list[str]:
    """Split a plain-text file into word tokens on whitespace.

    Punctuation stays attached to its word (e.g. 'аҭаҳароуп.'). This is the only
    preprocessing; it never decides sentence boundaries, so it cannot "fail" the
    way a sentence regex could.
    """
    text = path.read_text(encoding="utf-8").lstrip("﻿")
    return text.split()


def numbered_words(prefix: str, words: list[str]) -> str:
    """Render words as inline numbered tokens: '1:Ари 2:Данакил ...'."""
    return " ".join(f"{i}:{w}" for i, w in enumerate(words, 1))


def numbered_lines(prefix: str, words: list[str]) -> str:
    """One token per line, for the debug .words.txt files."""
    return "\n".join(f"{prefix}{i}\t{w}" for i, w in enumerate(words, 1))


SYSTEM_PROMPT = (
    "You are a bitext alignment engine. You are given two texts that are translations "
    "of the same nature-documentary narration: AB is Abkhaz prose, RU is Russian "
    "subtitle text. Each text is presented as a sequence of WORD TOKENS, each prefixed "
    "with its 1-based index, like `14:аҭаҳароуп.`.\n\n"
    "The two sides are segmented differently (subtitles are chopped by screen timing; "
    "the prose is wrapped differently), so a single sentence on one side may correspond "
    "to a different word span on the other. Your job: produce an ordered list of aligned "
    "spans that re-segments and links the two texts into parallel sentence-level units.\n\n"
    "Each link is a pair of INCLUSIVE word-index ranges: "
    '{"ab": [start, end], "ru": [start, end]}. A span may start or end anywhere — you may '
    "split within a line. If a span on one side has no counterpart (intro titles, on-screen "
    "credits, untranslated lines), set that side to null.\n\n"
    "Rules:\n"
    "- Output indices ONLY. Never output the text itself.\n"
    "- Keep links in monotonic order; within each side, spans must NOT overlap (each word "
    "belongs to at most one link) and should be contiguous where text is translated.\n"
    "- Group so each link is ONE coherent meaning unit (typically one sentence).\n"
    "- Use numbers, proper nouns and loan words as anchors (e.g. 150↔150, Данакил↔Данакиль, "
    "Девид Аттенборо↔Девид Аттенборо).\n"
    "- CRITICAL — gaps: end credits, on-screen production text (producers, camera operators, "
    "composer, studio), song lyrics, standalone titles, or ANY run present on only one side "
    "MUST be its own link with the other side set to null. NEVER pad or force-match a real "
    "narration sentence onto untranslated credits/titles — doing so misaligns everything after "
    "it. When in doubt, prefer a null gap over a forced match.\n\n"
    'Return STRICT JSON only, no prose: {"links": [{"ab": [s,e], "ru": [s,e]}, ...]}'
)


def build_user_prompt(ab_words: list[str], ru_words: list[str]) -> str:
    return (
        f"AB word tokens (Abkhaz, 1..{len(ab_words)}):\n"
        + numbered_words("AB", ab_words)
        + f"\n\nRU word tokens (Russian, 1..{len(ru_words)}):\n"
        + numbered_words("RU", ru_words)
        + "\n\nReturn the alignment JSON now."
    )


def call_llm(model: str, ab_words: list[str], ru_words: list[str]) -> tuple[str, dict]:
    """Return (raw response string, meta). Parsing happens in the caller."""
    from openai import OpenAI

    client = OpenAI(
        base_url="https://openrouter.ai/api/v1",
        api_key=os.environ["OPENROUTER_API_KEY"],
    )
    resp = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(ab_words, ru_words)},
        ],
        temperature=0,
        max_tokens=60000,
        response_format={"type": "json_object"},
        # Reasoning models (e.g. Gemini 3.x) otherwise spend the whole token budget
        # on hidden thinking and truncate the JSON. Cap thinking, keep room for output.
        extra_body={"reasoning": {"effort": "low"}},
    )
    choice = resp.choices[0]
    meta = {
        "finish_reason": choice.finish_reason,
        "usage": resp.usage.model_dump() if resp.usage else None,
    }
    return choice.message.content or "", meta


def parse_links(content: str) -> dict:
    """Parse the model JSON, tolerating markdown fences / leading-trailing prose."""
    text = content.strip()
    # strip ```json ... ``` fences if present
    fence = re.match(r"^```[a-zA-Z]*\s*(.*?)\s*```$", text, re.DOTALL)
    if fence:
        text = fence.group(1).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # fall back to the outermost {...} block
        start, end = text.find("{"), text.rfind("}")
        if start != -1 and end > start:
            return json.loads(text[start : end + 1])
        raise


def dedup_overlaps(links: list[dict]) -> int:
    """Clip spans so each source word belongs to at most one link.

    Order-INDEPENDENT: a model may legitimately link a span out of sequence (e.g. a
    title matched ahead of the surrounding narration), so we clip only *genuinely
    reused* words, not earlier ones. For each span we trim words already claimed by
    an earlier link from its front/back; a span fully inside claimed territory is
    dropped (set null). Returns the number of spans that were trimmed or dropped.
    """
    clipped = 0
    claimed = {"ab": set(), "ru": set()}
    for link in links:
        for side in ("ab", "ru"):
            span = link.get(side)
            if not span or len(span) != 2 or not all(isinstance(x, int) for x in span):
                continue
            s, e = (span[0], span[1]) if span[0] <= span[1] else (span[1], span[0])
            cl = claimed[side]
            orig = (s, e)
            while s <= e and s in cl:
                s += 1
            while s <= e and e in cl:
                e -= 1
            if s > e:
                link[side] = None
                clipped += 1
            else:
                if (s, e) != orig:
                    clipped += 1
                cl.update(range(s, e + 1))
                link[side] = [s, e]
    return clipped


def span_to_text(span, words: list[str]) -> str:
    """Join source words[start..end] (inclusive, 1-based). Clamp/skip bad spans."""
    if not span or not isinstance(span, (list, tuple)) or len(span) != 2:
        return ""
    start, end = span
    if not isinstance(start, int) or not isinstance(end, int):
        return ""
    start = max(1, start)
    end = min(len(words), end)
    if start > end:
        return ""
    return " ".join(words[start - 1 : end])


def evaluate(links: list[dict], n_ab: int, n_ru: int) -> dict:
    kinds = {"pair": 0, "ab-gap": 0, "ru-gap": 0, "empty": 0}
    covered = {"ab": set(), "ru": set()}
    reused = {"ab": 0, "ru": 0}            # genuine word reuse (should be 0 post-dedup)
    reorders = {"ab": 0, "ru": 0}          # span starts before the previous span (informational)
    prev_start = {"ab": None, "ru": None}

    def norm(span):
        if not span or len(span) != 2 or not all(isinstance(x, int) for x in span):
            return None
        s, e = span
        return (s, e) if s <= e else (e, s)

    for link in links:
        ab, ru = norm(link.get("ab")), norm(link.get("ru"))
        if ab and ru:
            kinds["pair"] += 1
        elif ab:
            kinds["ru-gap"] += 1
        elif ru:
            kinds["ab-gap"] += 1
        else:
            kinds["empty"] += 1
        for side, span in (("ab", ab), ("ru", ru)):
            if not span:
                continue
            s, e = span
            words = set(range(s, e + 1))
            reused[side] += len(words & covered[side])
            covered[side] |= words
            if prev_start[side] is not None and s <= prev_start[side]:
                reorders[side] += 1
            prev_start[side] = s

    return {
        "n_ab_words": n_ab,
        "n_ru_words": n_ru,
        "n_links": len(links),
        "link_types": kinds,
        "ab_word_coverage": round(len(covered["ab"]) / n_ab, 3) if n_ab else 0,
        "ru_word_coverage": round(len(covered["ru"]) / n_ru, 3) if n_ru else 0,
        "reused_words": reused["ab"] + reused["ru"],
        "reordered_links": reorders["ab"] + reorders["ru"],
    }


def slug(model: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", model.lower()).strip("-")


def run_model(model: str, ep: int, ab_words: list[str], ru_words: list[str]) -> dict:
    """Align with one model; write per-model outputs; return stats."""
    print(f"\nCalling {model} via OpenRouter ...")
    tag = slug(model)
    content, meta = call_llm(model, ab_words, ru_words)
    # always save the raw response + meta so failures are debuggable
    (OUT_DIR / f"ep{ep}_{tag}_raw.txt").write_text(content, encoding="utf-8")
    print(f"  finish_reason={meta['finish_reason']}  usage={meta['usage']}")
    result = parse_links(content)
    links = result.get("links", [])
    clipped = dedup_overlaps(links)  # ensure no word lands in two pairs
    if clipped:
        print(f"  clipped {clipped} overlapping span(s)")
    (OUT_DIR / f"ep{ep}_{tag}_alignment.json").write_text(
        json.dumps(result, ensure_ascii=False, indent=1), encoding="utf-8"
    )

    tsv_lines, review_lines = [], []
    for n, link in enumerate(links, 1):
        ab_txt = span_to_text(link.get("ab"), ab_words)
        ru_txt = span_to_text(link.get("ru"), ru_words)
        if ab_txt and ru_txt:
            tsv_lines.append(f"{ab_txt}\t{ru_txt}")
        review_lines.append(
            f"[{n}] ab{link.get('ab')} ru{link.get('ru')}\n"
            f"    AB: {ab_txt or '<none>'}\n"
            f"    RU: {ru_txt or '<none>'}"
        )
    (OUT_DIR / f"ep{ep}_{tag}_aligned.tsv").write_text("\n".join(tsv_lines), encoding="utf-8")
    (OUT_DIR / f"ep{ep}_{tag}_review.txt").write_text("\n".join(review_lines), encoding="utf-8")

    stats = evaluate(links, len(ab_words), len(ru_words))
    stats["model"] = model
    stats["paired_rows"] = len(tsv_lines)
    stats["clipped_overlaps"] = clipped
    print(json.dumps(stats, indent=2, ensure_ascii=False))
    print(f"  -> ep{ep}_{tag}_aligned.tsv  |  ep{ep}_{tag}_review.txt")
    return stats


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--episode", type=int, default=5)
    ap.add_argument("--models", nargs="+", default=DEFAULT_MODELS)
    args = ap.parse_args()

    if args.episode not in EPISODES:
        sys.exit(f"No extracted pair registered for episode {args.episode}")
    ab_name, ru_name = EPISODES[args.episode]
    ab_words = tokenize(RAW_BBC / ab_name)
    ru_words = tokenize(RAW_BBC / ru_name)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    ep = args.episode
    (OUT_DIR / f"ep{ep}_ab.words.txt").write_text(numbered_lines("AB", ab_words), encoding="utf-8")
    (OUT_DIR / f"ep{ep}_ru.words.txt").write_text(numbered_lines("RU", ru_words), encoding="utf-8")
    print(f"Tokenized: {len(ab_words)} ab words / {len(ru_words)} ru words")

    all_stats = []
    for model in args.models:
        try:
            all_stats.append(run_model(model, ep, ab_words, ru_words))
        except Exception as exc:  # keep comparing other models if one fails
            print(f"  !! {model} failed: {exc}")

    if all_stats:
        cols = ["model", "n_links", "paired_rows", "ab_word_coverage",
                "ru_word_coverage", "reused_words", "reordered_links", "clipped_overlaps"]
        print("\n=== Model comparison ===")
        print("  ".join(c.ljust(30 if c == "model" else 16) for c in cols))
        for s in all_stats:
            row = [str(s.get(c)) for c in cols]
            print("  ".join(v.ljust(30 if i == 0 else 16) for i, v in enumerate(row)))
        print(f"\nOutputs in {OUT_DIR}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
