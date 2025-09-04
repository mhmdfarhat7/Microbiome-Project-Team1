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
import os
import pandas as pd

from utils import load_metadata, average_composition

# תיקיית הסקריפט הנוכחי
script_dir = os.path.dirname(os.path.abspath(__file__))

# Fixed paths for M3 integration
METADATA_PATH = os.path.join(script_dir, "..", "data", "processed", "biorun_metadata_clean.parquet")
PHYLUM_PATH = os.path.join(script_dir, "sandpiper1.0.0.condensed.summary.phylum.filtered.parquet")


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
    as_dataframe: bool = False
) -> Union[Dict[str, Any], pd.DataFrame]:
    """
    Get phylum composition for a specific environment.
    
    Args:
        env: Environment name (must match organism_name exactly)
        top: Number of top phyla to return (None for all)
        as_dataframe: If True, return pandas DataFrame. If False, return dict.
    
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
        top_n=top
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
        df_result = pd.DataFrame({'mean_percent': avg_series})
        return df_result
    else:
        # Return as structured dict for M3 consumption
        composition_list = [
            {'taxon': str(taxon), 'mean_percent': float(percent)}
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


def get_data_by_location(location: str, top: Optional[int] = 50) -> Dict[str, Any]:
    """
    Get phylum composition data filtered by geographic location.
    
    This function:
    1. Gets matching biosamples from geo_loc_name_with_biosample.csv.gz
    2. Filters biorun_metadata_clean.parquet for matching biosamples
    3. Gets phylum data from sandpiper1.0.0.condensed.summary.phylum.csv.gz
    4. Calculates average composition like the regular environment function
    
    Args:
        location: Geographic location name to filter by
        top: Number of top phyla to return (None for all)
    
    Returns:
        Dict with structure:
            {
                'success': bool,
                'location': str,
                'level': 'phylum',
                'n_runs': int,
                'composition': [{'taxon': str, 'mean_percent': float}, ...],
                'unassigned_included': bool,
                'error': str (if success=False)
            }
    """
    try:
        # Paths to data files
        geo_loc_path = os.path.join(script_dir, "..", "data", "processed", "geo_loc_name_with_biosample.csv.gz")
        metadata_path = os.path.join(script_dir, "..", "data", "processed", "biorun_metadata_clean.parquet")
        phylum_path = os.path.join(script_dir, "sandpiper1.0.0.condensed.summary.phylum.filtered.parquet")
        
        # Step 1: Load geographic location data and get matching biosamples
        geo_df = pd.read_csv(geo_loc_path)
        matching_biosamples = geo_df[geo_df['geo_loc_name'] == location]['biosample'].tolist()
        
        if not matching_biosamples:
            return {
                'success': False,
                'location': location,
                'level': 'phylum',
                'n_runs': 0,
                'composition': [],
                'unassigned_included': True,
                'error': f'No biosamples found for location: {location}'
            }
        
        # Step 2: Load metadata and filter by matching biosamples
        df_meta = pd.read_parquet(metadata_path)
        filtered_meta = df_meta[df_meta['biosample'].isin(matching_biosamples)]
        
        if filtered_meta.empty:
            return {
                'success': False,
                'location': location,
                'level': 'phylum',
                'n_runs': 0,
                'composition': [],
                'unassigned_included': True,
                'error': f'No bioruns found for biosamples in location: {location}'
            }
        
        # Step 3: Get phylum data for the filtered biosamples
        phylum_df = pd.read_parquet(phylum_path)
        matching_phylum = phylum_df[phylum_df['biosample'].isin(matching_biosamples)]
        
        if matching_phylum.empty:
            return {
                'success': False,
                'location': location,
                'level': 'phylum',
                'n_runs': 0,
                'composition': [],
                'unassigned_included': True,
                'error': f'No phylum data found for biosamples in location: {location}'
            }
        
        # Step 4: Calculate average composition using the same logic as get_phylum_composition
        # Group by phylum and calculate mean percentage
        phylum_avg = matching_phylum.groupby('phylum')['percent'].mean().sort_values(ascending=False)
        
        # Apply top filter if specified
        if top is not None:
            phylum_avg = phylum_avg.head(top)
        
        # Convert to the expected format
        composition_list = [
            {'taxon': str(taxon), 'mean_percent': float(percent)}
            for taxon, percent in phylum_avg.items()
        ]
        
        return {
            'success': True,
            'location': location,
            'level': 'phylum',
            'n_runs': len(filtered_meta),
            'composition': composition_list,
            'unassigned_included': True,
            'error': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'location': location,
            'level': 'phylum',
            'n_runs': 0,
            'composition': [],
            'unassigned_included': True,
            'error': f'Error processing location data: {str(e)}'
        }


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
