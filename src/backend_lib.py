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
import numpy as np
import time
from threading import Lock

from utils import load_metadata, average_composition, average_phylum_composition

# תיקיית הסקריפט הנוכחי
script_dir = os.path.dirname(os.path.abspath(__file__))

# Fixed paths for M3 integration
METADATA_PATH = os.path.join(script_dir, "..", "data", "processed", "biorun_metadata_clean.parquet")

# Taxonomic level file paths
TAXONOMIC_PATHS = {
    "phylum": os.path.join(script_dir, "soil.summary.phylum.compact.parquet"),
    "class": os.path.join(script_dir, "soil.summary.class.compact.parquet"),
    "order": os.path.join(script_dir, "soil.summary.order.compact.parquet"),
    "family": os.path.join(script_dir, "soil.summary.family.compact.parquet"),
    "genus": os.path.join(script_dir, "soil.summary.genus.compact.parquet")
}

# Backward compatibility
PHYLUM_PATH = TAXONOMIC_PATHS["phylum"]

# Advanced caching for better performance
_cache_lock = Lock()
_composition_cache = {}
_cache_timestamps = {}
CACHE_EXPIRY_SECONDS = 300  # 5 minutes


@lru_cache(maxsize=1)
def _get_cached_metadata() -> pd.DataFrame:
    """
    Cache metadata loading to avoid repeated file I/O.
    Returns the cleaned metadata DataFrame.
    """
    return load_metadata(METADATA_PATH)


def _get_cache_key(env: str, level: str, top: Optional[int]) -> str:
    """Generate a cache key for composition data."""
    return f"{env}:{level}:{top}"


def _is_cache_valid(cache_key: str) -> bool:
    """Check if cached data is still valid."""
    if cache_key not in _cache_timestamps:
        return False
    return time.time() - _cache_timestamps[cache_key] < CACHE_EXPIRY_SECONDS


def _get_cached_composition(env: str, level: str, top: Optional[int]) -> Optional[Dict[str, Any]]:
    """Get composition data from cache if valid."""
    cache_key = _get_cache_key(env, level, top)
    with _cache_lock:
        if cache_key in _composition_cache and _is_cache_valid(cache_key):
            return _composition_cache[cache_key]
    return None


def _set_cached_composition(env: str, level: str, top: Optional[int], data: Dict[str, Any]) -> None:
    """Store composition data in cache."""
    cache_key = _get_cache_key(env, level, top)
    with _cache_lock:
        _composition_cache[cache_key] = data
        _cache_timestamps[cache_key] = time.time()
        
        # Clean up old cache entries
        current_time = time.time()
        expired_keys = [k for k, t in _cache_timestamps.items() 
                       if current_time - t >= CACHE_EXPIRY_SECONDS]
        for key in expired_keys:
            _composition_cache.pop(key, None)
            _cache_timestamps.pop(key, None)


def clear_composition_cache() -> None:
    """Clear all cached composition data."""
    with _cache_lock:
        _composition_cache.clear()
        _cache_timestamps.clear()


def get_cache_stats() -> Dict[str, Any]:
    """Get cache statistics for monitoring."""
    with _cache_lock:
        current_time = time.time()
        valid_entries = sum(1 for t in _cache_timestamps.values() 
                           if current_time - t < CACHE_EXPIRY_SECONDS)
        return {
            'total_entries': len(_composition_cache),
            'valid_entries': valid_entries,
            'expired_entries': len(_composition_cache) - valid_entries,
            'cache_keys': list(_composition_cache.keys())
        }


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


def get_composition(
    env: str, 
    level: str = "phylum",
    top: Optional[int] = 50, 
    as_dataframe: bool = False
) -> Union[Dict[str, Any], pd.DataFrame]:
    """
    Get taxonomic composition for a specific environment and level.
    
    Args:
        env: Environment name (must match organism_name exactly)
        level: Taxonomic level (phylum, class, order, family, genus)
        top: Number of top taxa to return (None for all)
        as_dataframe: If True, return pandas DataFrame. If False, return dict.
    
    Returns:
        If as_dataframe=False: Dict with structure:
            {
                'env': str,
                'level': str,
                'n_runs': int,
                'composition': [{'taxon': str, 'mean_percent': float}, ...],
                'unassigned_included': bool
            }
        
        If as_dataframe=True: DataFrame with:
            - index: taxonomic taxa names
            - column: 'mean_percent' (float values)
    
    Raises:
        ValueError: If environment not found or invalid level
        FileNotFoundError: If data files not found
    """
    # Check cache first (only for dict results)
    if not as_dataframe:
        cached_result = _get_cached_composition(env, level, top)
        if cached_result is not None:
            return cached_result
    
    df_meta = _get_cached_metadata()
    
    # Verify environment exists
    available_envs = df_meta['organism_name'].unique()
    if env not in available_envs:
        raise ValueError(
            f"Environment '{env}' not found. Available environments: {sorted(available_envs)}"
        )
    
    # Verify level is supported
    if level not in TAXONOMIC_PATHS:
        raise ValueError(
            f"Level '{level}' not supported. Available levels: {list(TAXONOMIC_PATHS.keys())}"
        )
    
    # Get taxonomic composition using updated utils
    avg_series, n_runs = average_composition(
        env=env,
        df_meta=df_meta,
        taxonomic_path=TAXONOMIC_PATHS[level],
        level=level,
        top_n=top
    )
    
    if n_runs == 0:
        # Return empty result structure
        if as_dataframe:
            return pd.DataFrame(columns=['mean_percent'])
        else:
            result = {
                'env': env,
                'level': level,
                'n_runs': 0,
                'composition': [],
                'unassigned_included': True
            }
            # Cache the empty result
            _set_cached_composition(env, level, top, result)
            return result
    
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
        
        result = {
            'env': env,
            'level': level,
            'n_runs': int(n_runs),
            'composition': composition_list,
            'unassigned_included': True
        }
        
        # Cache the result
        _set_cached_composition(env, level, top, result)
        return result


def get_phylum_composition(
    env: str, 
    top: Optional[int] = 50, 
    as_dataframe: bool = False
) -> Union[Dict[str, Any], pd.DataFrame]:
    """
    Get phylum composition for a specific environment (backward compatibility).
    
    Args:
        env: Environment name (must match organism_name exactly)
        top: Number of top phyla to return (None for all)
        as_dataframe: If True, return pandas DataFrame. If False, return dict.
    
    Returns:
        Same as get_composition with level="phylum"
    """
    return get_composition(env, "phylum", top, as_dataframe)


# Convenience functions for common use cases
def get_top_environments(n: int = 10) -> List[str]:
    """Get top N environments by biorun count."""
    return get_environments(top=n)


def get_environment_stats() -> Dict[str, int]:
    """Get environment names and their biorun counts."""
    df_meta = _get_cached_metadata()
    env_counts = df_meta['organism_name'].value_counts()
    return dict(env_counts)


def get_data_by_location(location: str, level: str = "phylum", top: Optional[int] = 50) -> Dict[str, Any]:
    """
    Get taxonomic composition data filtered by geographic location.
    
    This function:
    1. Gets matching biosamples from geo_loc_name_with_biosample.csv.gz
    2. Filters biorun_metadata_clean.parquet for matching biosamples
    3. Gets taxonomic data from the appropriate level file
    4. Calculates average composition like the regular environment function
    
    Args:
        location: Geographic location name to filter by
        level: Taxonomic level (phylum, class, order, family, genus)
        top: Number of top taxa to return (None for all)
    
    Returns:
        Dict with structure:
            {
                'success': bool,
                'location': str,
                'level': str,
                'n_runs': int,
                'composition': [{'taxon': str, 'mean_percent': float}, ...],
                'unassigned_included': bool,
                'error': str (if success=False)
            }
    """
    try:
        # Verify level is supported
        if level not in TAXONOMIC_PATHS:
            return {
                'success': False,
                'location': location,
                'level': level,
                'n_runs': 0,
                'composition': [],
                'unassigned_included': True,
                'error': f'Level "{level}" not supported. Available levels: {list(TAXONOMIC_PATHS.keys())}'
            }
        
        # Paths to data files
        geo_loc_path = os.path.join(script_dir, "..", "data", "processed", "geo_loc_name_with_biosample.csv.gz")
        metadata_path = os.path.join(script_dir, "..", "data", "processed", "biorun_metadata_clean.parquet")
        taxonomic_path = TAXONOMIC_PATHS[level]
        
        # Step 1: Load geographic location data and get matching biosamples
        geo_df = pd.read_csv(geo_loc_path)
        
        # Debug: print available locations
        print(f"DEBUG: Looking for location: {location}")
        print(f"DEBUG: Available locations sample: {geo_df['geo_loc_name'].head(10).tolist()}")
        
        # Try exact match first
        matching_biosamples = geo_df[geo_df['geo_loc_name'] == location]['biosample'].tolist()
        print(f"DEBUG: Exact match found {len(matching_biosamples)} biosamples")
        
        # If no exact match, try case-insensitive match
        if not matching_biosamples:
            matching_biosamples = geo_df[geo_df['geo_loc_name'].str.lower() == location.lower()]['biosample'].tolist()
            print(f"DEBUG: Case-insensitive match found {len(matching_biosamples)} biosamples")
        
        # If still no match, try partial match
        if not matching_biosamples:
            matching_biosamples = geo_df[geo_df['geo_loc_name'].str.contains(location, case=False, na=False)]['biosample'].tolist()
            print(f"DEBUG: Partial match found {len(matching_biosamples)} biosamples")
        
        if not matching_biosamples:
            return {
                'success': False,
                'location': location,
                'level': level,
                'n_runs': 0,
                'composition': [],
                'unassigned_included': True,
                'error': f'No biosamples found for location: {location}'
            }
        
        # Step 2: Load metadata and filter by matching biosamples
        df_meta = pd.read_parquet(metadata_path)
        filtered_meta = df_meta[df_meta['biosample'].isin(matching_biosamples)]
        print(f"DEBUG: Found {len(filtered_meta)} bioruns for {len(matching_biosamples)} biosamples")
        
        if filtered_meta.empty:
            return {
                'success': False,
                'location': location,
                'level': level,
                'n_runs': 0,
                'composition': [],
                'unassigned_included': True,
                'error': f'No bioruns found for biosamples in location: {location}'
            }
        
        # Step 3: Get taxonomic data using run_accession from filtered_meta
        # The taxonomic files have biorun as index, so we need to use run_accession from filtered_meta
        taxonomic_df = pd.read_parquet(taxonomic_path)
        print(f"DEBUG: Taxonomic file shape: {taxonomic_df.shape}")
        print(f"DEBUG: Taxonomic file columns: {taxonomic_df.columns.tolist()}")
        print(f"DEBUG: Taxonomic file index name: {taxonomic_df.index.name}")
        
        # Get run_accession values from filtered_meta (these are the biorun IDs)
        run_accessions = filtered_meta.index.tolist()
        print(f"DEBUG: Looking for {len(run_accessions)} run_accessions in taxonomic file")
        
        # Match by biorun (run_accession) - this should be the index of the taxonomic file
        if taxonomic_df.index.name == 'biorun':
            matching_taxonomic = taxonomic_df[taxonomic_df.index.isin(run_accessions)]
        elif 'biorun' in taxonomic_df.columns:
            matching_taxonomic = taxonomic_df[taxonomic_df['biorun'].isin(run_accessions)]
        else:
            # If biorun is not the index and not a column, assume first column is biorun
            first_col = taxonomic_df.columns[0]
            matching_taxonomic = taxonomic_df[taxonomic_df[first_col].isin(run_accessions)]
        
        print(f"DEBUG: Found {len(matching_taxonomic)} matching taxonomic rows")
        
        if matching_taxonomic.empty:
            return {
                'success': False,
                'location': location,
                'level': level,
                'n_runs': 0,
                'composition': [],
                'unassigned_included': True,
                'error': f'No {level} data found for run_accessions in location: {location}'
            }
        
        # Step 4: Calculate average composition
        # The taxonomic files have biorun as index and taxonomic levels as columns
        # We need to calculate the mean across all bioruns for each taxonomic level
        
        print(f"DEBUG: Matching taxonomic data shape: {matching_taxonomic.shape}")
        print(f"DEBUG: Matching taxonomic columns: {matching_taxonomic.columns.tolist()}")
        
        # Get numeric columns (these should be the taxonomic levels)
        numeric_cols = matching_taxonomic.select_dtypes(include=[np.number]).columns
        print(f"DEBUG: Numeric columns found: {len(numeric_cols)}")
        
        if len(numeric_cols) == 0:
            return {
                'success': False,
                'location': location,
                'level': level,
                'n_runs': 0,
                'composition': [],
                'unassigned_included': True,
                'error': f'No numeric data found in {level} file for location: {location}'
            }
        
        # Calculate mean across all bioruns for each taxonomic level
        taxonomic_avg = matching_taxonomic[numeric_cols].mean().sort_values(ascending=False)
        print(f"DEBUG: Calculated averages for {len(taxonomic_avg)} taxonomic levels")
        
        # Apply top filter if specified
        if top is not None:
            taxonomic_avg = taxonomic_avg.head(top)
        
        # Convert to the expected format
        composition_list = [
            {'taxon': str(taxon), 'mean_percent': float(percent)}
            for taxon, percent in taxonomic_avg.items()
        ]
        
        print(f"DEBUG: Final result - {len(composition_list)} composition items, {len(filtered_meta)} runs")
        
        return {
            'success': True,
            'location': location,
            'level': level,
            'n_runs': len(filtered_meta),
            'composition': composition_list,
            'unassigned_included': True,
            'error': None
        }
        
    except Exception as e:
        return {
            'success': False,
            'location': location,
            'level': level,
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
