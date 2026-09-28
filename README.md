# Multimodal Safety Dataset Viewer

A local, browser-based viewer for two vision-language safety benchmarks:

| Dataset | Rows | Images | What it tests |
|---|---|---|---|
| [VLSBench](https://huggingface.co/datasets/Foreshhh/vlsbench) | 2,241 | 1,957 | Image–instruction pairs where the **image** carries the safety risk |
| [HoliSafe-Bench](https://huggingface.co/datasets/etri-vilab/holisafe-bench) | 4,031 | 1,796 | Image + query pairs labelled by risk type (SSS / SSU / SUU / USU / UUU) |

> ⚠️ **Content warning.** Both datasets contain violent, sexual, hateful and
> self-harm imagery. Images are blurred by default in the viewer. Use for
> AI-safety research only.

## 1. Get access on Hugging Face (one time)

The datasets are **not included in this repo**: you download them yourself
with your own Hugging Face account. HoliSafe-Bench is **gated** (and VLSBench
may be), so before anything else:

1. Log in at <https://huggingface.co>.
2. Open each dataset page, **fill in the access form and accept the terms**:
   - <https://huggingface.co/datasets/etri-vilab/holisafe-bench>
   - <https://huggingface.co/datasets/Foreshhh/vlsbench>

   HoliSafe grants access automatically once the form is submitted.
3. Create a **read** token at <https://huggingface.co/settings/tokens>.

## 2. Install

Python 3.10+.

```bash
git clone https://github.com/saxenarohit/multimodal_safety_dataset.git
cd multimodal_safety_dataset
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
hf auth login          # paste your read token (or: export HF_TOKEN=hf_...)
```

Your token stays in your own Hugging Face cache / environment; nothing in this
repo reads, stores or commits it.

## 3. Download, build, view

```bash
python download.py     # ~3.3 GB into raw/   (VLSBench ~2.4 GB, HoliSafe ~0.9 GB)
python build.py        # resized images + JSON index into site/  (~0.5 GB, <1 min)
python serve.py        # opens http://127.0.0.1:8000
```

If `download.py` stops with *"gated and your account has not been granted
access"*, finish step 1 for that dataset (and check `hf auth whoami` shows the
same account), then re-run it. Downloads resume where they left off.

Only want one dataset? `python download.py --only holisafe` (or `vlsbench`),
then `build.py` builds whatever is present.

Other options: `python serve.py --port 9000 --no-browser`.
After a successful build you can delete `raw/` to reclaim ~3.3 GB; the viewer
only needs `site/`.

## Features

- **Dataset tabs**: VLSBench and HoliSafe.
- **Heatmap** of category × image source (VLSBench) or category × risk type
  (HoliSafe); click a cell to filter.
- **Facet filters** with live counts for every label field, plus full-text
  search (press `/`).
- **Card grid** with infinite scroll; click a card for a detail view with the
  full image and all fields, `←` / `→` to step through.
- HoliSafe detail view lists **every query asked about the same image**.
- **Blur toggle** (on by default); click an image in the detail view to unblur
  just that one.
- Filters and the open item are kept in the URL, so views can be bookmarked.
- Light / dark mode follows your system.

### HoliSafe risk types

Type = image safety / query safety / combined-input safety (S = safe, U = unsafe).

| Type | Meaning |
|---|---|
| SSS | safe image + safe query → safe |
| SSU | safe image + safe query → **unsafe in combination** |
| SUU | safe image + unsafe query → unsafe |
| USU | unsafe image + safe query → unsafe |
| UUU | unsafe image + unsafe query → unsafe |

## Layout

```
download.py        fetch both datasets from HF into raw/ (uses your own HF login)
build.py           raw/ -> site/img/{t,f}/*.jpg + site/{vlsbench,holisafe}.json
serve.py           static server on 127.0.0.1 (stdlib only)
site/index.html    the whole viewer (vanilla JS, no build step)
```

## Data terms

This repo contains only viewer code. The data stays under its original terms:

- **HoliSafe-Bench**: text and generated images CC BY-NC 4.0; images taken from
  other datasets keep their source licences. Its access terms require you to use
  it only for research / safety evaluation, **restrict access to authorised
  people**, and delete it when no longer needed. `serve.py` therefore binds to
  localhost only; do not expose it publicly.
- **VLSBench**: Apache-2.0 (see the dataset card; images come from several sources).

Please cite the original papers if you use either dataset:

- HoliSafe: *Holistic Safety Benchmarking and Modeling for Vision-Language
  Model* — <https://arxiv.org/abs/2506.04704>
- VLSBench: *VLSBench: Unveiling Visual Leakage in Multimodal Safety* —
  <https://arxiv.org/abs/2411.19939>
