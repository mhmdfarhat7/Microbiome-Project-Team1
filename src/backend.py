import argparse
import sys
from pathlib import Path

from utils import load_metadata, average_composition, as_json_payload


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(
        description="M2 backend: average phylum composition by environment"
    )
    p.add_argument(
        "environment",
        type=str,
        help="Environment name (exact from organism_name), e.g. 'soil metagenome'"
    )
    p.add_argument(
        "--metadata",
        type=str,
        default="data/processed/biorun_metadata_clean.parquet",
        help="Path to cleaned metadata (Parquet preferred; CSV also supported)."
    )
    p.add_argument(
        "--phylum",
        type=str,
        default="data/sandpiper1.0.0.condensed.summary.phylum.csv.gz",
        help="Path to phylum-level composition CSV (.csv.gz)."
    )
    p.add_argument(
        "--top",
        type=int,
        default=50,
        help="Keep top-N taxa by mean abundance (default: 50; use 0 or negative for all)."
    )
    p.add_argument(
        "--json",
        action="store_true",
        help="Output as JSON instead of a text table."
    )
    return p.parse_args()


def main() -> int:
    args = parse_args()
    env = args.environment

    # Normalize top_n
    top_n = args.top if args.top and args.top > 0 else None

    # Load metadata
    try:
        df_meta = load_metadata(args.metadata)
    except Exception as e:
        print(f"[ERROR] Failed to load metadata: {e}", file=sys.stderr)
        return 1

    # Compute average composition
    series, n_runs = average_composition(
        env=env,
        df_meta=df_meta,
        phylum_path=args.phylum,
        top_n=top_n
    )

    if n_runs == 0 or series.empty:
        print(f"[WARN] No matching bioruns/composition found for environment: {env}")
        return 0

    if args.json:
        print(as_json_payload(env=env, level="phylum", n_runs=n_runs, composition=series))
        return 0

    # Human-readable table
    print(f"\nEnvironment: {env}")
    print(f"Level: phylum")
    print(f"Bioruns used: {n_runs}")
    print(f"Top taxa: {len(series)}\n")
    # Pretty print
    width = max(len(str(idx)) for idx in series.index) if not series.empty else 10
    print(f"{'Taxon'.ljust(width)}  Mean %")
    print("-" * (width + 9))
    for taxon, val in series.items():
        print(f"{str(taxon).ljust(width)}  {val:7.3f}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())