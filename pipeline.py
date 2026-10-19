"""Clean, filter and prioritise work orders with pandas (all rules are invented).

Stages:
  0. load / clean / concatenate free text
  1. hard exclusions (training / test entries, excluded categories)
  2. keep if category is whitelisted OR a text rule fires
  3. text rules (regex with word boundaries) -> tags + priority
  4. final priority tier P1 / P2 / P3
"""
import re
from pathlib import Path

import pandas as pd

# ---- Configuration -----------------------------------------------------------
CATEGORY_WHITELIST = {"10", "20", "30", "50", "70"}
EXCLUDED_CATEGORIES = {"60", "80"}
PRIORITY_BY_CATEGORY = {"10": "P1", "20": "P1", "30": "P2", "50": "P2", "70": "P3"}

HARD_EXCLUDE = re.compile(r"\b(?:TRAINING SESSION|DRILL EXERCISE|DUMMY ENTRY|TEST ENTRY)\b")

# \b word boundaries avoid false positives such as STRAIGHT or MISALIGNMENT SHEET.
TEXT_RULES = {
    "LEAKS": ("P1", re.compile(r"\b(?:LEAKS?|LEAKING|LEAKED)\b")),
    "WEAR": ("P2", re.compile(r"\b(?:WORN|CORRODED|CRACKED|FRAYED)\b")),
    "ALIGNMENT": ("P2", re.compile(r"\b(?:MISALIGNED|REALIGN(?:ED|MENT)?)\b[^\n]{0,40}\b(?:SHAFT|BELT|PULLEY)\b|\b(?:SHAFT|BELT|PULLEY)\b[^\n]{0,40}\bMISALIGNED\b")),
    "LOOSE_FIT": ("P2", re.compile(r"\b(?:BRACKET|PANEL|COVER)\b[^\n]{0,30}\b(?:LOOSE|NOT FLUSH|GAP)\b")),
    "COSMETIC": ("P3", re.compile(r"\b(?:PAINT|SCRATCH|DENT)\w*\b")),
    "RESTORED": ("P3", re.compile(r"\b(?:CLEANING|FLUSH)\b[^\n]{0,40}\bRESTORED\b")),
}
ROUTINE_TITLE_OK = re.compile(r"\b(?:CLEANING|LUBRICATION|CALIBRATION)\b")


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, parse_dates=["opened_at", "closed_at"], dtype={"category": str})
    df = df.drop_duplicates(subset="order_id")
    for col in ["description", "action_text", "title"]:
        df[col] = df[col].fillna("").astype(str)
    text = (df["description"] + "\n" + df["action_text"]).str.upper()
    df["text"] = text.str.replace(r"[ \t]+", " ", regex=True).str.strip()
    return df


def tag_text(text: str):
    hits = [(name, prio) for name, (prio, rx) in TEXT_RULES.items() if rx.search(text)]
    tags = ",".join(n for n, _ in hits)
    best = min((p for _, p in hits), default=None)
    return tags, best


def apply_rules(df: pd.DataFrame) -> pd.DataFrame:
    # Stage 1
    df = df[~df["text"].str.contains(HARD_EXCLUDE)]
    df = df[~df["category"].isin(EXCLUDED_CATEGORIES)].copy()

    # Stage 3
    tagged = df["text"].apply(tag_text)
    df["rule_tags"] = tagged.str[0]
    df["rule_priority"] = tagged.str[1]

    # Stage 2
    keep = df["category"].isin(CATEGORY_WHITELIST) | (df["rule_tags"] != "")
    df = df[keep].copy()

    # Routine orders are kept only if a rule fires or the title matches
    routine_ok = (df["order_type"] != "R") | (df["rule_tags"] != "") | \
        df["title"].str.upper().str.contains(ROUTINE_TITLE_OK)
    df = df[routine_ok].copy()

    # Stage 4: best of category priority and text-rule priority
    def final_priority(row):
        cands = [PRIORITY_BY_CATEGORY.get(row["category"]), row["rule_priority"]]
        cands = [c for c in cands if isinstance(c, str)]
        return min(cands) if cands else "P3"

    df["priority"] = df.apply(final_priority, axis=1)
    df["hours_to_close"] = (df["closed_at"] - df["opened_at"]).dt.total_seconds() / 3600
    return df.drop(columns=["rule_priority"])


def run(src: Path, dst: Path) -> pd.DataFrame:
    raw = load(src)
    out = apply_rules(raw)
    out.drop(columns=["text"]).to_csv(dst, index=False)
    print(f"Input rows: {len(raw)} | Kept: {len(out)} ({len(out) / len(raw):.1%})")
    print(out["priority"].value_counts().to_string())
    return out


if __name__ == "__main__":
    base = Path(__file__).resolve().parent.parent / "output"
    run(base / "synthetic_orders.csv", base / "filtered_orders.csv")
