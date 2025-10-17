import re, cv2, pandas as pd
from paddleocr import PaddleOCR

IMG_PATH = "screenshots/stitched.png"  # your uploaded stitched image
OUT_CSV = "players_from_stitched.csv"

# --- Settings tuned for your image ---
ROW_TOL = 30           # vertical grouping tolerance
RIGHT_FRACTION = 0.42  # fraction of width considered as power column
MIN_CONF = 0.4         # OCR confidence threshold
# -------------------------------------

ocr = PaddleOCR(use_angle_cls=True, lang='en', show_log=False)
img = cv2.imread(IMG_PATH)
H, W = img.shape[:2]
results = []

# OCR pass
ocr_res = ocr.ocr(img, cls=True)
if not ocr_res or not ocr_res[0]:
    print("No text detected!")
    exit()

tokens = []
for line in ocr_res[0]:
    box, (text, conf) = line
    if conf < MIN_CONF:
        continue
    cx = sum(p[0] for p in box)/4
    cy = sum(p[1] for p in box)/4
    tokens.append((cx, cy, text))

# Group by Y position (rows)
rows = []
for cx, cy, text in sorted(tokens, key=lambda x:x[1]):
    if not rows or abs(rows[-1]['y'] - cy) > ROW_TOL:
        rows.append({'y': cy, 'names': [], 'powers': []})
    row = rows[-1]
    if cx < W * RIGHT_FRACTION:
        row['names'].append((cx, text))
    else:
        row['powers'].append((cx, text))

# Parse names and numbers
def clean_name(s):
    s = re.sub(r"\b(Members?|Elite|Officer|President|Vice|Daily|Active|Hardcore|Casual|Online)\b", "", s, flags=re.I)
    s = re.sub(r"[^A-Za-z0-9^~\-\s]", "", s)
    s = re.sub(r"\s+", " ", s).strip()
    return s

data = []
for row in rows:
    if not row['names'] or not row['powers']:
        continue
    name = " ".join(t for _, t in sorted(row['names']))
    name = clean_name(name)
    num_text = "".join(t for _, t in sorted(row['powers']))
    num_text = re.sub(r"[^\d]", "", num_text)
    if name and num_text.isdigit():
        data.append((name, int(num_text)))

# Deduplicate (keep max power)
df = pd.DataFrame(data, columns=["Player Name", "Power"])
df = df.groupby("Player Name", as_index=False)["Power"].max()
df = df.sort_values("Power", ascending=False)
df.to_csv(OUT_CSV, index=False)

print(df.to_string(index=False))
print(f"\nSaved results to {OUT_CSV}")
