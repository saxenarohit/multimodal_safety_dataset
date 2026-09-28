"""Download VLSBench and HoliSafe-Bench from Hugging Face into raw/.

    python download.py                 # both datasets
    python download.py --only holisafe

Both repos may be gated: accept the terms on each dataset page first, then log
in once with `hf auth login` (or export HF_TOKEN). Your token is only read by
huggingface_hub from your own environment; nothing is written to this repo.
"""
import argparse
import os
import sys
import tarfile

from huggingface_hub import hf_hub_download, snapshot_download
from huggingface_hub.errors import GatedRepoError, HfHubHTTPError, RepositoryNotFoundError

ROOT = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(ROOT, "raw")

DATASETS = {
    "vlsbench": "Foreshhh/vlsbench",
    "holisafe": "etri-vilab/holisafe-bench",
}


def gated_help(repo):
    sys.exit(
        f"\nCannot access {repo}: it is gated and your account has not been granted access.\n"
        f"  1. Open https://huggingface.co/datasets/{repo} while logged in,\n"
        f"     fill in the access form and accept the terms.\n"
        f"  2. Make sure this machine is logged in as that account:\n"
        f"       hf auth login        (or: export HF_TOKEN=hf_...)\n"
        f"  3. Re-run: python download.py\n"
    )


def get_vlsbench():
    repo = DATASETS["vlsbench"]
    out = os.path.join(RAW, "vls")
    hf_hub_download(repo, "data.json", repo_type="dataset", local_dir=RAW)
    os.replace(os.path.join(RAW, "data.json"), os.path.join(RAW, "vls.json"))
    if os.path.isdir(os.path.join(out, "imgs")) and len(os.listdir(os.path.join(out, "imgs"))) > 1900:
        print("vlsbench images already present")
        return
    print("downloading vlsbench images (~2.4 GB tar)...")
    tar = hf_hub_download(repo, "imgs.tar", repo_type="dataset", local_dir=out)
    with tarfile.open(tar) as t:
        t.extractall(out, filter="data")
    os.remove(tar)


def get_holisafe():
    repo = DATASETS["holisafe"]
    hf_hub_download(repo, "holisafe_bench.json", repo_type="dataset", local_dir=RAW)
    os.replace(os.path.join(RAW, "holisafe_bench.json"), os.path.join(RAW, "holi.json"))
    print("downloading holisafe images (~0.9 GB)...")
    snapshot_download(repo, repo_type="dataset", allow_patterns=["images/**"],
                      local_dir=os.path.join(RAW, "holi"), max_workers=16)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--only", choices=DATASETS)
    a = ap.parse_args()
    os.makedirs(RAW, exist_ok=True)
    for name, fn in (("vlsbench", get_vlsbench), ("holisafe", get_holisafe)):
        if a.only and a.only != name:
            continue
        try:
            fn()
        except (GatedRepoError, RepositoryNotFoundError):
            gated_help(DATASETS[name])
        except HfHubHTTPError as e:
            if e.response is not None and e.response.status_code in (401, 403):
                gated_help(DATASETS[name])
            raise
        print(f"{name}: done")
    print("\nNext: python build.py && python serve.py")


if __name__ == "__main__":
    main()
