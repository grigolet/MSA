import re
import pandas as pd
import easyocr
from pathlib import Path
from tqdm import tqdm

# --- knobs you can tweak ---
DROP_TOKENS = {
    "nm", "nm-", "members","member","elite","officer","president","vice","vice president",
    "hardcore","casual","active","daily","active daily","active at night","online",
    "ranking","notice","enter","club","tag","state"
}
MIN_DIGITS = 6            # treat a power as valid if it has at least this many digits
STRICT_MIN_POWER = 3_000_000  # drop entries below this (set None to disable)
# --------------------------

def is_drop_line(s: str) -> bool:
    s0 = re.sub(r"[:;,\-–—]+$", "", s.strip()).lower()  # strip trailing punctuation
    if not s0:
        return True
    if s0 in DROP_TOKENS:
        return True
    # tag/role phrases anywhere in the line
    return any(w in s0 for w in [
        "member","elite","officer","president","hardcore","casual","active","online","vice"
    ])


def parse_power(s: str):
    """Return (int_value, ok_bool) only if the string is strictly a number with separators."""
    s = (s or "").strip()
    if not s:
        return None, False
    # normalize thin spaces etc.
    s = s.replace("\u2009","").replace("\u202F","").replace("\u00A0"," ")
    s = s.replace("|","1")
    # must be ONLY digits/commas/dots/spaces
    if not re.fullmatch(r"[0-9][0-9,.\s]*", s):
        return None, False
    digits = re.sub(r"[^\d]", "", s)
    if digits.isdigit() and len(digits) >= MIN_DIGITS:
        return int(digits), True
    return None, False


def clean_name(raw: str) -> str:
    # remove standalone garbage tokens & keep UTF-8 letters/digits/^~-_
    toks = re.split(r"\s+", raw.strip())
    out = []
    for t in toks:
        if not t:
            continue
        low = t.lower()
        if low in DROP_TOKENS:
            continue
        # drop short numeric level noise like "170"
        if re.fullmatch(r"\d{2,4}", t):
            continue
        letters = sum(c.isalpha() for c in t)
        if letters == 0 or letters/len(t) < 0.35:
            # likely junk like "’" or mostly punctuation
            continue
        out.append(t)
    name = " ".join(out)
    name = re.sub(r"[-_.;:]+$", "", name)         # trim trailing punctuation
    name = re.sub(r"\s{2,}", " ", name).strip()
    return name

def normalize_name_key(name: str) -> str:
    # case-insensitive + trim trailing punctuation/spaces for dedupe
    return re.sub(r"[-_.\s:;]+$", "", name.strip().lower())

def parse_ocr_lines(lines):
    pairs = []            # (name, power)
    suspects = []         # (name_raw, num_text, reason)
    cur_name_parts = []

    for line in lines:
        if line is None:
            continue
        line = str(line).strip()
        if not line:
            continue

        # Power?
        pval, ok = parse_power(line)
        if pval is not None:
            name = clean_name(" ".join(cur_name_parts))
            if name:
                # optional floor filter
                if STRICT_MIN_POWER is not None and pval < STRICT_MIN_POWER:
                    suspects.append((name, line, f"power<{STRICT_MIN_POWER} ({pval})"))
                elif ok:
                    pairs.append((name, pval))
                else:
                    suspects.append((name, line, f"malformed_digits({pval})"))
            cur_name_parts = []
            continue

        # Tag/role? skip
        if is_drop_line(line):
            continue

        # Otherwise, it's part of the name (names can span multiple lines)
        cur_name_parts.append(line)
        print("Raw name part:", cur_name_parts)

    # Deduplicate by a normalized key, keep max power
    best = {}
    for n, p in pairs:
        k = normalize_name_key(n)
        if k not in best or p > best[k][1]:
            best[k] = (n, p)

    # Build DataFrame
    data = [{"Player Name": n, "Power": p} for (n, p) in best.values()]
    df = pd.DataFrame(data).sort_values("Power", ascending=False).reset_index(drop=True)
    return df, suspects



if __name__ == "__main__":
    parsed_all = []
    suspects_all = []
    reader = easyocr.Reader(['en'], gpu=False)
    for f in tqdm(Path("screenshots/cropped").glob("*.jpg")):
        results = reader.readtext(str(f), detail=0, paragraph=False)
        parsed, suspects = parse_ocr_lines(results)
        print(parsed, suspects)
        parsed_all.append(parsed)
        suspects_all.extend(suspects)
        
    df = pd.concat(parsed_all, ignore_index=True)
    df = df.groupby("Player Name", as_index=False)["Power"].max()
    df = df.sort_values(by="Power", ascending=False).reset_index(drop=True)

    # Print clean table
    name_w = max(len("Player Name"), *(len(x) for x in df["Player Name"])) if not df.empty else 12
    pow_w  = max(len("Power"), *(len(str(x)) for x in df["Power"])) if not df.empty else 6
    print(f"{'Player Name':<{name_w}} | {'Power':<{pow_w}}")
    print(f"{'-'*name_w}-+-{'-'*pow_w}")
    for _, r in df.iterrows():
        print(f"{r['Player Name']},{r['Power']}")

    # Show anything suspicious so you can fix it manually if you want
    if suspects_all:
        print("\nSuspects (malformed or below threshold):")
        for n, raw_num, why in suspects_all:
            print(f"  - {n:25s}  num='{raw_num}'  -> {why}")

    # df.to_csv("players_clean.csv", index=False)
