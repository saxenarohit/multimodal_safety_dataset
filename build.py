"""Build the static site: resized images + one JSON index per dataset.

    python build.py             # reads raw/ (from download.py), writes site/

raw/vls.json + raw/vls/imgs/*        Foreshhh/vlsbench (data.json + imgs.tar)
raw/holi.json + raw/holi/images/**   etri-vilab/holisafe-bench
"""
import json
import os
from concurrent.futures import ProcessPoolExecutor

from PIL import Image, ImageOps

Image.MAX_IMAGE_PIXELS = None
ROOT = os.path.dirname(os.path.abspath(__file__))
RAW, SITE = os.path.join(ROOT, "raw"), os.path.join(ROOT, "site")
THUMB, FULL = 360, 1400

HOLI_LABELS = [
    "safe", "gender", "race", "religion", "harassment", "disability_discrimination",
    "drug_related_hazards", "property_crime", "facial_data_exposure",
    "identity_data_exposure", "physical_self_injury", "suicide", "animal_abuse",
    "obscene_gestures", "physical_altercation", "terrorism",
    "weapon_related_violence", "sexual_content", "financial_advice", "medical_advice",
]


def resize(job):
    src, stem = job
    out_t = os.path.join(SITE, "img", "t", stem + ".jpg")
    out_f = os.path.join(SITE, "img", "f", stem + ".jpg")
    if os.path.exists(out_t) and os.path.exists(out_f):
        return stem, None
    try:
        im = ImageOps.exif_transpose(Image.open(src)).convert("RGB")
        size = im.size
        for out, side, q in ((out_f, FULL, 85), (out_t, THUMB, 78)):
            c = im.copy()
            c.thumbnail((side, side), Image.LANCZOS)
            c.save(out, "JPEG", quality=q, optimize=True)
        return stem, size
    except Exception as e:  # keep the row; the viewer shows a placeholder
        return stem, f"ERR {e}"


def main():
    for d in ("t", "f"):
        os.makedirs(os.path.join(SITE, "img", d), exist_ok=True)

    def load(name):
        path = os.path.join(RAW, name)
        if not os.path.exists(path):
            print(f"skipping {name}: not downloaded")
            return []
        return json.load(open(path))

    vls = load("vls.json")
    vls_rows, jobs = [], []
    for r in vls:
        stem = "v" + os.path.splitext(os.path.basename(r["image_path"]))[0]
        jobs.append((os.path.join(RAW, "vls", r["image_path"]), stem))
        vls_rows.append({
            "id": r["instruction_id"], "img": stem, "instruction": r["instruction"],
            "category": r["category"], "sub_category": r["sub_category"],
            "source": r["source"], "image_description": r["image_description"],
            "safety_reason": r["safety_reason"],
        })

    holi = load("holi.json")
    holi_rows, stems = [], {}
    for r in holi:
        # several queries share one image; one resized copy per unique path
        stem = stems.setdefault(r["image"], "h%d" % len(stems))
        holi_rows.append({
            "id": r["id"], "img": stem, "query": r["query"], "type": r["type"],
            "category": r["category"], "subcategory": r["subcategory"],
            "image_safe": r["image_safe"],
            "image_label": HOLI_LABELS[r["image_safety_label"]],
            "image_path": r["image"],
        })
    jobs += [(os.path.join(RAW, "holi", "images", p), s) for p, s in stems.items()]

    bad = []
    with ProcessPoolExecutor() as ex:
        for i, (stem, res) in enumerate(ex.map(resize, jobs, chunksize=16)):
            if isinstance(res, str):
                bad.append((stem, res))
            if i % 500 == 0:
                print(f"{i}/{len(jobs)} images", flush=True)
    for stem, err in bad:
        print("failed:", stem, err)
    missing = {s for s, _ in bad}
    for r in vls_rows + holi_rows:
        if r["img"] in missing:
            r["img"] = None

    for name, rows in (("vlsbench", vls_rows), ("holisafe", holi_rows)):
        if not rows:
            continue
        with open(os.path.join(SITE, name + ".json"), "w") as f:
            json.dump(rows, f, ensure_ascii=False, separators=(",", ":"))
        print(name, len(rows), "rows")


if __name__ == "__main__":
    main()
