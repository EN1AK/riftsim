import sys, os, glob

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, ".pylibs"))
import fitz

OUT = os.path.join(ROOT, "extracted")
os.makedirs(OUT, exist_ok=True)

for folder in ("loltcg_pdfs", "riftbound_en_rules"):
    base = os.path.join(ROOT, folder)
    for pdf in sorted(glob.glob(os.path.join(base, "*.pdf"))):
        name = os.path.splitext(os.path.basename(pdf))[0]
        out_path = os.path.join(OUT, f"{folder}__{name}.txt")
        try:
            doc = fitz.open(pdf)
            text = []
            for i, page in enumerate(doc):
                text.append(f"\n===== PAGE {i+1} =====\n" + page.get_text())
            with open(out_path, "w", encoding="utf-8") as f:
                f.write("".join(text))
            print(f"OK {name}: {len(doc)} pages, {sum(len(t) for t in text)} chars")
        except Exception as e:
            print(f"FAIL {name}: {e}")
