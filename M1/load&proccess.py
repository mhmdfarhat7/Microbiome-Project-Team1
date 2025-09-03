#!/usr/bin/env python3
import pandas as pd
import os

def main():
    print("=" * 60)
    print("BIORUN METADATA FILTERED EXTRACTION")
    print("=" * 60)
    
    # Dataset file - updated to use the correct path and .gz extension
    data_file = "Microbe-vis-data/sandpiper1.0.0.condensed.biorun-metadata.csv.gz"
    if not os.path.exists(data_file):
        print(f"ERROR: File '{data_file}' not found!")
        print("Available files in Microbe-vis-data/:")
        if os.path.exists("Microbe-vis-data/"):
            for f in os.listdir("Microbe-vis-data/"):
                if "biorun-metadata" in f:
                    print(f"  - {f}")
        return
    
    # Load dataset
    try:
        print(f"Loading {data_file}...")
        df = pd.read_csv(data_file)
        print(f"✓ Dataset loaded successfully! Total rows: {len(df):,}")
        print(f"Columns: {list(df.columns)}")
    except Exception as e:
        print(f"ERROR loading dataset: {e}")
        return
    
    # Keep only required columns
    required_cols = ['run_accession', 'biosample', 'organism_name']
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        print(f"ERROR: Missing columns in dataset: {missing_cols}")
        print(f"Available columns: {list(df.columns)}")
        return
    
    df = df[required_cols].copy()
    
    # Filter for 'metagenome' in organism_name
    df = df[df['organism_name'].str.contains('metagenome', case=False, na=False)]
    print(f"✓ Filtered rows containing 'metagenome': {len(df):,}")
    
    # Save filtered dataset for EDA
    output_file = "filtered_bioruns.csv"
    df.to_csv(output_file, index=False)
    print(f"✓ Filtered dataset saved to '{output_file}'")
    
    # Create M2-compatible output (with run_accession as index)
    df_m2 = df.copy()
    df_m2['run_accession'] = df_m2['run_accession'].astype(str)
    df_m2 = df_m2.set_index('run_accession')
    
    # Ensure output directory exists
    os.makedirs('data/processed', exist_ok=True)
    
    # Save M2-compatible parquet file
    m2_output = "data/processed/biorun_metadata_clean.parquet"
    df_m2.to_parquet(m2_output)
    print(f"✓ M2-compatible metadata saved to '{m2_output}'")
    print(f"✓ M2 file has {len(df_m2)} rows with index 'run_accession'")
    print("=" * 60)

if __name__ == "__main__":
    main()
