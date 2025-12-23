import os
from loaders.registry import get_loader

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

RAW_DIR = os.path.join(BASE_DIR, "raw_docs")
MD_DIR = os.path.join(BASE_DIR, "markdown")

os.makedirs(MD_DIR, exist_ok=True)

for file in os.listdir(RAW_DIR):
    path = os.path.join(RAW_DIR, file)

    if not os.path.isfile(path):
        continue

    loader = get_loader(path)
    md_content = loader.load(path)

    out_path = os.path.join(MD_DIR, file + ".md")
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md_content)

    print(f"[OK] {file} -> Markdown")
