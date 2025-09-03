#!/usr/bin/env python3
import pandas as pd
import os

def main():
    print("=" * 60)
    print("BIORUN METADATA FILTERED EXTRACTION")
    print("=" * 60)
    
    # Dataset file
    data_file = "sandpiper1.0.0.condensed.biorun-metadata.csv"
    if not os.path.exists(data_file):
        print(f"ERROR: File '{data_file}' not found!")
        return
    
    # Load dataset
    try:
        df = pd.read_csv(data_file)
        print(f"✓ Dataset loaded successfully! Total rows: {len(df):,}")
    except Exception as e:
        print(f"ERROR loading dataset: {e}")
        return
    
    # Keep only required columns
    required_cols = ['run_accession', 'biosample', 'organism_name']
    missing_cols = [c for c in required_cols if c not in df.columns]
    if missing_cols:
        print(f"ERROR: Missing columns in dataset: {missing_cols}")
        return
    
    df = df[required_cols].copy()
    
    # Filter for 'metagenome' in organism_name
    df = df[df['organism_name'].str.contains('metagenome', case=False, na=False)]
    print(f"✓ Filtered rows containing 'metagenome': {len(df):,}")
    
    # Rename 'organism_name' to 'organism'
    df.rename(columns={'organism_name': 'organism'}, inplace=True)
    
    # Save filtered dataset
    output_file = "filtered_bioruns.csv"
    df.to_csv(output_file, index=False)
    print(f"✓ Filtered dataset saved to '{output_file}'")
    print("=" * 60)

if __name__ == "__main__":
    main()
