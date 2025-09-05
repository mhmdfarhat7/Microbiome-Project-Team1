import os
import json
from typing import Iterable, Optional, Tuple
import pandas as pd
import pyarrow as pa
import pyarrow.parquet as pq


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
# Taxonomic level table loader (chunked for memory efficiency)
# ----------------------------------------------------

def load_taxonomic_rows(taxonomic_path: str, target_bioruns: Iterable[str], level: str) -> pd.DataFrame:
    """
    Load ONLY the rows (bioruns) we need from the large taxonomic file using PyArrow for efficiency.
    - taxonomic_path: path to taxonomic composition file (CSV or Parquet)
    - target_bioruns: iterable (set/list) of run_accession IDs to keep
    - level: taxonomic level (phylum, class, order, family, genus)

    Returns a DataFrame where:
      index = biorun (run_accession)
      columns = taxonomic taxa (floats; %)
    """
    if not os.path.exists(taxonomic_path):
        raise FileNotFoundError(f"Taxonomic file not found: {taxonomic_path}")

    # We'll scan in chunks and keep only the needed rows
    target = set(map(str, target_bioruns))
    if not target:
        # Return empty DF with no columns; caller should handle
        return pd.DataFrame()

    ext = os.path.splitext(taxonomic_path)[1].lower()
    
    if ext in {".parquet"}:
        # For parquet files, use PyArrow for efficient chunked reading
        try:
            # Open parquet file
            parquet_file = pq.ParquetFile(taxonomic_path)
            
            # Get the schema to understand the structure
            schema = parquet_file.schema
            column_names = [field.name for field in schema]
            
            # Determine the biorun column (usually first column or named 'biorun')
            biorun_col = None
            if 'biorun' in column_names:
                biorun_col = 'biorun'
            elif len(column_names) > 0:
                biorun_col = column_names[0]  # Assume first column is biorun
            
            if biorun_col is None:
                raise ValueError("Could not identify biorun column in parquet file")
            
            # Read in chunks and filter
            chunks = []
            batch_size = 10000  # Process 10k rows at a time
            
            for batch in parquet_file.iter_batches(batch_size=batch_size):
                # Convert batch to pandas
                batch_df = batch.to_pandas()
                
                # Set biorun as index if it's not already
                if biorun_col in batch_df.columns:
                    batch_df = batch_df.set_index(biorun_col)
                
                # Filter to target bioruns
                keep = batch_df.index.isin(target)
                if keep.any():
                    filtered_batch = batch_df.loc[keep].copy()
                    # Ensure numeric dtype for all columns except index
                    numeric_cols = filtered_batch.select_dtypes(include=[object]).columns
                    for col in numeric_cols:
                        filtered_batch[col] = pd.to_numeric(filtered_batch[col], errors='coerce')
                    filtered_batch = filtered_batch.astype("float64")
                    chunks.append(filtered_batch)
            
            if not chunks:
                return pd.DataFrame()
            
            # Combine all chunks
            df = pd.concat(chunks, axis=0)
            return df
            
        except Exception as e:
            # Fallback to pandas if PyArrow fails
            print(f"PyArrow failed, falling back to pandas: {e}")
            df_full = pd.read_parquet(taxonomic_path)
            if 'biorun' in df_full.columns:
                df_full = df_full.set_index('biorun')
            elif df_full.index.name != 'biorun':
                df_full = df_full.set_index(df_full.columns[0])
            
            keep = df_full.index.isin(target)
            if keep.any():
                df = df_full.loc[keep].copy()
                df = df.apply(pd.to_numeric, errors="coerce")
                df = df.astype("float64")
                return df
            else:
                return pd.DataFrame()
    else:
        # For CSV files, use chunked reading
        chunks = []
        for chunk in pd.read_csv(
            taxonomic_path,
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


# Backward compatibility alias
def load_phylum_rows(phylum_path: str, target_bioruns: Iterable[str]) -> pd.DataFrame:
    """Backward compatibility wrapper for phylum data."""
    return load_taxonomic_rows(phylum_path, target_bioruns, "phylum")


# ----------------------------------------------------
# Core M2 logic: average composition (all taxonomic levels)
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
    taxonomic_path: str,
    level: str = "phylum",
    top_n: Optional[int] = 50,
    group_others: bool = True,
    others_threshold: float = 0.5
) -> Tuple[pd.Series, int]:
    """
    Compute the average taxonomic-level composition for a given environment.

    Steps:
    1) From metadata, pick all bioruns where organism_name == env.
    2) Load ONLY those bioruns' rows from the taxonomic file (chunked).
    3) Average column-wise (ignore NaNs).
    4) Sort descending, drop zeros/NaNs, optionally keep top_n.
    5) Group small percentages into "Other" category if requested.

    Args:
        env: environment name to filter by
        df_meta: metadata DataFrame
        taxonomic_path: path to taxonomic composition file
        level: taxonomic level (phylum, class, order, family, genus)
        top_n: keep top N taxa (None for all)
        group_others: whether to group small percentages into "Other"
        others_threshold: percentage threshold for grouping (default: 0.5%)

    Returns:
      (series, n_runs_used)
      - series: index = taxonomic taxa, values = mean percent (float)
      - n_runs_used: number of bioruns that actually appeared in the taxonomic file
    """
    # 1) Get the bioruns belonging to this environment
    bioruns = select_bioruns_for_env(df_meta, env)
    if len(bioruns) == 0:
        return pd.Series(dtype="float64"), 0

    # 2) Load ONLY those rows from the massive taxonomic file
    df_taxonomic_subset = load_taxonomic_rows(taxonomic_path, bioruns, level)

    if df_taxonomic_subset.empty:
        return pd.Series(dtype="float64"), 0

    # 3) Compute the mean (% across bioruns)
    # Rows = bioruns, columns = taxa
    mean_series = df_taxonomic_subset.mean(axis=0, skipna=True)

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

    n_runs_used = df_taxonomic_subset.shape[0]
    return mean_series, n_runs_used


# Backward compatibility wrapper for phylum
def average_phylum_composition(
    env: str,
    df_meta: pd.DataFrame,
    phylum_path: str,
    top_n: Optional[int] = 50,
    group_others: bool = True,
    others_threshold: float = 0.5
) -> Tuple[pd.Series, int]:
    """Backward compatibility wrapper for phylum composition."""
    return average_composition(env, df_meta, phylum_path, "phylum", top_n, group_others, others_threshold)


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