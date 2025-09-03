#!/usr/bin/env python3
"""
M2 Backend Library for M3 Frontend Integration

This module provides a clean interface for M3 to:
1. Get available environments for dropdown
2. Get phylum composition data for selected environment
3. Choose between structured dict or DataFrame output

Both functions internally reuse utils.load_metadata and utils.average_composition.
"""

from typing import List, Optional, Union, Dict, Any
from functools import lru_cache
import pandas as pd

from utils import load_metadata, average_composition


# Fixed paths for M3 integration
METADATA_PATH = "data/processed/biorun_metadata_clean.parquet"
PHYLUM_PATH = "Microbe-vis-data/sandpiper1.0.0.condensed.summary.phylum.csv.gz"


@lru_cache(maxsize=1)
def _get_cached_metadata() -> pd.DataFrame:
    """
    Cache metadata loading to avoid repeated file I/O.
    Returns the cleaned metadata DataFrame.
    """
    return load_metadata(METADATA_PATH)


def get_environments(top: Optional[int] = None) -> List[str]:
    """
    Get list of available environments for M3 dropdown.
    
    Args:
        top: If specified, return only top N environments by biorun count.
              If None, return all environments.
    
    Returns:
        List of environment names (organism_name values)
    
    Example:
        >>> get_environments(top=10)
        ['human gut metagenome', 'soil metagenome', 'marine metagenome', ...]
    """
    df_meta = _get_cached_metadata()
    
    if top is None:
        # Return all unique environments
        return sorted(df_meta['organism_name'].unique())
    else:
        # Return top N environments by biorun count
        env_counts = df_meta['organism_name'].value_counts()
        return sorted(env_counts.head(top).index)


def get_phylum_composition(
    env: str, 
    top: Optional[int] = 50, 
    as_dataframe: bool = False,
    group_others: bool = True,
    others_threshold: float = 0.5
) -> Union[Dict[str, Any], pd.DataFrame]:
    """
    Get phylum composition for a specific environment.
    
    Args:
        env: Environment name (must match organism_name exactly)
        top: Number of top phyla to return (None for all)
        as_dataframe: If True, return pandas DataFrame. If False, return dict.
        group_others: Whether to group small percentages into "Other" category (default: True)
        others_threshold: Percentage threshold below which taxa are grouped (default: 0.5%)
    
    Returns:
        If as_dataframe=False: Dict with structure:
            {
                'env': str,
                'level': 'phylum',
                'n_runs': int,
                'composition': [{'taxon': str, 'mean_percent': float}, ...],
                'unassigned_included': bool
            }
        
        If as_dataframe=True: DataFrame with:
            - index: phylum taxa names
            - column: 'mean_percent' (float values)
    
    Example:
        >>> result = get_phylum_composition("soil metagenome", top=5)
        >>> print(f"Found {result['n_runs']} bioruns")
        >>> for phylum in result['composition']:
        ...     print(f"{phylum['taxon']}: {phylum['mean_percent']:.2f}%")
    
    Raises:
        ValueError: If environment not found
        FileNotFoundError: If data files not found
    """
    df_meta = _get_cached_metadata()
    
    # Verify environment exists
    available_envs = df_meta['organism_name'].unique()
    if env not in available_envs:
        raise ValueError(
            f"Environment '{env}' not found. Available environments: {sorted(available_envs)}"
        )
    
    # Get phylum composition using existing utils
    avg_series, n_runs = average_composition(
        env=env,
        df_meta=df_meta,
        phylum_path=PHYLUM_PATH,
        top_n=top,
        group_others=group_others,
        others_threshold=others_threshold
    )
    
    if n_runs == 0:
        # Return empty result structure
        if as_dataframe:
            return pd.DataFrame(columns=['mean_percent'])
        else:
            return {
                'env': env,
                'level': 'phylum',
                'n_runs': 0,
                'composition': [],
                'unassigned_included': True
            }
    
    if as_dataframe:
        # Return as DataFrame for easy plotting/manipulation
        df_result = pd.DataFrame({
            'mean_percent': avg_series
        })
        return df_result
    
    else:
        # Return as structured dict for M3 consumption
        composition_list = [
            {
                'taxon': str(taxon),
                'mean_percent': float(percent)
            }
            for taxon, percent in avg_series.items()
        ]
        
        return {
            'env': env,
            'level': 'phylum',
            'n_runs': int(n_runs),
            'composition': composition_list,
            'unassigned_included': True
        }


# Convenience functions for common use cases
def get_top_environments(n: int = 10) -> List[str]:
    """Get top N environments by biorun count."""
    return get_environments(top=n)


def get_environment_stats() -> Dict[str, int]:
    """Get environment names and their biorun counts."""
    df_meta = _get_cached_metadata()
    env_counts = df_meta['organism_name'].value_counts()
    return dict(env_counts)


# Example usage for M3 developers
if __name__ == "__main__":
    print("M2 Backend Library - M3 Integration Layer")
    print("=" * 50)
    
    # Show available environments
    print(f"Available environments: {len(get_environments())}")
    print(f"Top 5 environments: {get_top_environments(5)}")
    
    # Test phylum composition
    test_env = "soil metagenome"
    try:
        result = get_phylum_composition(test_env, top=5)
        print(f"\n{test_env} results:")
        print(f"  Bioruns: {result['n_runs']}")
        print(f"  Top phyla: {len(result['composition'])}")
        
        # Test DataFrame output
        df_result = get_phylum_composition(test_env, top=5, as_dataframe=True)
        print(f"\nDataFrame output shape: {df_result.shape}")
        
    except Exception as e:
        print(f"Error testing {test_env}: {e}")
