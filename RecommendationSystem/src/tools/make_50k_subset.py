"""
Create a 50k-row ratings subset from ML-100k and package it as data/ml-50k.zip.

Usage:
    python -m src.tools.make_50k_subset

Requirements:
    - Have ML-100k present as data/ml-100k/ or data/ml-100k.zip
    - This script samples ~50,000 rating rows (stratified by user)
      and writes movies.csv + ratings.csv to data/ml-50k/ and data/ml-50k.zip
"""
from __future__ import annotations
import numpy as np
import pandas as pd
import zipfile
from pathlib import Path

from src.recommender import _extract_if_needed, ML100K_FILES

DATA_ROOT = Path(__file__).resolve().parents[2] / "data"


def main():
    ml_dir = DATA_ROOT / "ml-100k"
    _extract_if_needed(DATA_ROOT / "ml-100k.zip", ml_dir)

    r_path = ml_dir / ML100K_FILES["ratings"]
    i_path = ml_dir / ML100K_FILES["items"]
    if not r_path.exists() or not i_path.exists():
        raise SystemExit("Missing ML-100k. Place it in data/ml-100k/ or data/ml-100k.zip")

    r = pd.read_csv(r_path, sep="\t", names=["user_id", "movie_id", "rating", "ts"], engine="python")
    m = pd.read_csv(i_path, sep="|", header=None, encoding="latin-1").rename(columns={0: "movie_id", 1: "title"})[
        ["movie_id", "title"]
    ]

    # stratified sample per-user
    target_n = 50_000
    counts = r.groupby("user_id").size()
    props = (counts / counts.sum()) * target_n
    samples = []
    for u, n in props.round().astype(int).items():
        sub = r[r.user_id == u]
        n = min(n, len(sub))
        if n > 0:
            samples.append(sub.sample(n=n, random_state=42))
    r50 = pd.concat(samples, ignore_index=True)
    if len(r50) > target_n:
        r50 = r50.sample(n=target_n, random_state=42)

    out_dir = DATA_ROOT / "ml-50k"
    out_dir.mkdir(parents=True, exist_ok=True)
    r50.rename(columns={"ts": "timestamp"}).to_csv(out_dir / "ratings.csv", index=False)
    m.to_csv(out_dir / "movies.csv", index=False)

    with zipfile.ZipFile(DATA_ROOT / "ml-50k.zip", "w", zipfile.ZIP_DEFLATED) as z:
        z.write(out_dir / "ratings.csv", "ratings.csv")
        z.write(out_dir / "movies.csv", "movies.csv")

    print("Wrote:", out_dir / "ratings.csv")
    print("Wrote:", out_dir / "movies.csv")
    print("Wrote:", DATA_ROOT / "ml-50k.zip")


if __name__ == "__main__":
    main()