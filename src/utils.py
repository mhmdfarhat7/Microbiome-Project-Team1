import os
import json
from typing import Iterable, Optional, Tuple
import pandas as pd


# ----------------------------
# Metadata loaders (M1 output)
# ----------------------------

def load_metadata(path: str) -> pd.DataFrame:
    """
    Load cleaned biorun metadata (prefer Parquet; fallback to CSV).
    Expects a column named 'run_accession' (used as index) and 'organism_name'.
    If the file already has an index of run_accession, we keep it.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"Metadata file not found: {path}")

    ext = os.path.splitext(path)[1].lower()

    if ext in {".parquet"}:
        df = pd.read_parquet(path)
    else:
        # Works for .csv or .csv.gz
        df = pd.read_csv(path)

    # Ensure required columns
    if "run_accession" not in df.columns and df.index.name != "run_accession":
        raise ValueError("Metadata must include a 'run_accession' column or have it as index.")

    # Normalize index to 'run_accession'
    if "run_accession" in df.columns:
        df = df.drop_duplicates(subset=["run_accession"]).set_index("run_accession")

    # Basic sanity checks / normalization
    if "organism_name" not in df.columns:
        raise ValueError("Metadata must include an 'organism_name' column.")

    # Ensure consistent types
    df["organism_name"] = df["organism_name"].astype(str)

    return df


# ----------------------------------------------------
# Phylum table loader (chunked for memory efficiency)
# ----------------------------------------------------

def load_phylum_rows(phylum_path: str, target_bioruns: Iterable[str]) -> pd.DataFrame:
    """
    Load ONLY the rows (bioruns) we need from the large phylum file by chunking.
    - phylum_path: path to phylum composition file (CSV or Parquet)
    - target_bioruns: iterable (set/list) of run_accession IDs to keep

    Returns a DataFrame where:
      index = biorun (run_accession)
      columns = phylum taxa (floats; %)
    """
    if not os.path.exists(phylum_path):
        raise FileNotFoundError(f"Phylum file not found: {phylum_path}")

    # We'll scan in chunks and keep only the needed rows
    target = set(map(str, target_bioruns))
    if not target:
        # Return empty DF with no columns; caller should handle
        return pd.DataFrame()

    ext = os.path.splitext(phylum_path)[1].lower()
    
    if ext in {".parquet"}:
        # For parquet files, read the entire file and filter
        df_full = pd.read_parquet(phylum_path)
        if 'biorun' in df_full.columns:
            df_full = df_full.set_index('biorun')
        elif df_full.index.name != 'biorun':
            # Assume first column is biorun if not set as index
            df_full = df_full.set_index(df_full.columns[0])
        
        # Filter to target bioruns
        keep = df_full.index.isin(target)
        if keep.any():
            df = df_full.loc[keep].copy()
            # Ensure numeric dtype
            df = df.apply(pd.to_numeric, errors="coerce")
            df = df.astype("float64")
            return df
        else:
            return pd.DataFrame()
    else:
        # For CSV files, use chunked reading
        chunks = []
        for chunk in pd.read_csv(
            phylum_path,
            index_col=0,
            chunksize=50_000,   # tune if needed
            low_memory=True
        ):
            # chunk.index are biorun ids
            keep = chunk.index.isin(target)
            if keep.any():
                # Ensure numeric dtype (sometimes CSVs load as object)
                num = chunk.loc[keep].apply(pd.to_numeric, errors="coerce")
                chunks.append(num)

        if not chunks:
            return pd.DataFrame()

        df = pd.concat(chunks, axis=0)
        # Optional sanity: ensure values are floats
        df = df.astype("float64")

        return df


# ----------------------------------------------------
# Core M2 logic: average composition (phylum)
# ----------------------------------------------------

def group_small_percentages(series: pd.Series, threshold: float = 0.5) -> pd.Series:
    """
    Group small percentages below threshold into an "Other" category.
    
    Args:
        series: pandas Series with taxa as index and percentages as values
        threshold: percentage threshold below which taxa are grouped (default: 0.5)
    
    Returns:
        Modified series with small percentages grouped as "Other"
    """
    if series.empty:
        return series
    
    # Find taxa below threshold
    below_threshold = series < threshold
    
    if below_threshold.any():
        # Sum up all small percentages
        other_sum = series[below_threshold].sum()
        
        # Keep only taxa above threshold
        result = series[~below_threshold].copy()
        
        # Add "Other" category if there are small percentages
        if other_sum > 0:
            result["Other"] = other_sum
            
        return result
    
    return series


def select_bioruns_for_env(
    df_meta: pd.DataFrame,
    env: str,
    case_insensitive: bool = True
) -> pd.Index:
    """
    Filter metadata to bioruns matching the environment (organism_name).
    Returns their run_accession index.
    """
    if case_insensitive:
        mask = df_meta["organism_name"].str.lower() == env.lower()
    else:
        mask = df_meta["organism_name"] == env

    return df_meta.index[mask]


def average_composition(
    env: str,
    df_meta: pd.DataFrame,
    phylum_path: str,
    top_n: Optional[int] = 50,
    group_others: bool = True,
    others_threshold: float = 0.5
) -> Tuple[pd.Series, int]:
    """
    Compute the average phylum-level composition for a given environment.

    Steps:
    1) From metadata, pick all bioruns where organism_name == env.
    2) Load ONLY those bioruns' rows from the phylum CSV (chunked).
    3) Average column-wise (ignore NaNs).
    4) Sort descending, drop zeros/NaNs, optionally keep top_n.
    5) Group small percentages into "Other" category if requested.

    Args:
        env: environment name to filter by
        df_meta: metadata DataFrame
        phylum_path: path to phylum composition file
        top_n: keep top N taxa (None for all)
        group_others: whether to group small percentages into "Other"
        others_threshold: percentage threshold for grouping (default: 0.5%)

    Returns:
      (series, n_runs_used)
      - series: index = phylum taxa, values = mean percent (float)
      - n_runs_used: number of bioruns that actually appeared in the phylum file
    """
    # 1) Get the bioruns belonging to this environment
    bioruns = select_bioruns_for_env(df_meta, env)
    if len(bioruns) == 0:
        return pd.Series(dtype="float64"), 0

    # 2) Load ONLY those rows from the massive phylum file
    df_phylum_subset = load_phylum_rows(phylum_path, bioruns)

    if df_phylum_subset.empty:
        return pd.Series(dtype="float64"), 0

    # 3) Compute the mean (% across bioruns)
    # Rows = bioruns, columns = taxa
    mean_series = df_phylum_subset.mean(axis=0, skipna=True)

    # 4) Clean up: drop NaNs, zeros; sort desc; keep top_n
    mean_series = mean_series.dropna()
    mean_series = mean_series[mean_series > 0].sort_values(ascending=False)
    
    # 5) Group small percentages into "Other" if requested
    if group_others:
        mean_series = group_small_percentages(mean_series, others_threshold)
    
    # 6) Apply top_n limit after grouping (so "Other" is preserved)
    if top_n is not None:
        # If we have "Other", make sure it's included in top_n
        if "Other" in mean_series.index:
            # Keep top_n-1 individual taxa + "Other"
            top_individual = mean_series[mean_series.index != "Other"].head(top_n - 1)
            other_value = mean_series["Other"]
            mean_series = pd.concat([top_individual, pd.Series([other_value], index=["Other"])])
        else:
            mean_series = mean_series.head(top_n)

    n_runs_used = df_phylum_subset.shape[0]
    return mean_series, n_runs_used


# ----------------------------------------------------
# Small helpers for presentation
# ----------------------------------------------------

def as_json_payload(env: str, level: str, n_runs: int, composition: pd.Series) -> str:
    """
    Turn the result into a JSON string your friend (M3) can consume.
    """
    payload = {
        "env": env,
        "level": level,
        "n_runs": int(n_runs),
        "composition": [
            {"taxon": str(taxon), "mean_percent": float(value)}
            for taxon, value in composition.items()
        ],
        "unassigned_included": True
    }
    return json.dumps(payload, ensure_ascii=False, indent=2)