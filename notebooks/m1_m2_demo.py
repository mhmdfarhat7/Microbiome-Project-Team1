#!/usr/bin/env python3
"""
M1-M2 Integration Demo Script
Run this in a Jupyter notebook to see the complete workflow!
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import sys
from pathlib import Path

# Add src to path for M2 imports
sys.path.append('../src')
from utils import load_metadata, average_composition, as_json_payload

def run_m1_m2_demo():
    """Run the complete M1-M2 integration demo."""
    
    print("🧬 M1-M2 Integration Demo")
    print("=" * 60)
    
    # Step 1: Check data availability
    print("\n📁 Step 1: Checking Data Availability")
    data_dir = "../Microbe-vis-data"
    if os.path.exists(data_dir):
        files = os.listdir(data_dir)
        print(f"✅ Found {len(files)} files in {data_dir}")
        for f in sorted(files):
            if f.endswith('.gz'):
                size = os.path.getsize(os.path.join(data_dir, f)) / (1024**3)
                print(f"  📄 {f:<50} ({size:.1f} GB)")
    else:
        print(f"❌ Data directory not found: {data_dir}")
        return
    
    # Step 2: Run M1 data cleaning
    print("\n🧹 Step 2: Running M1 Data Cleaning")
    print("-" * 40)
    
    import subprocess
    result = subprocess.run(["python3", "../M1/load&proccess.py"], 
                           capture_output=True, text=True, cwd="..")
    
    print(result.stdout)
    if result.stderr:
        print("⚠️  Warnings/Errors:")
        print(result.stderr)
    
    # Step 3: Verify M1 output
    print("\n✅ Step 3: Verifying M1 Output")
    print("-" * 40)
    
    m1_output = "../data/processed/biorun_metadata_clean.parquet"
    if os.path.exists(m1_output):
        print(f"✅ M1 output found: {m1_output}")
        
        # Load and examine cleaned metadata
        df_meta = pd.read_parquet(m1_output)
        print(f"📊 Cleaned metadata shape: {df_meta.shape}")
        print(f"🔍 Index: {df_meta.index.name}")
        print(f"📋 Columns: {list(df_meta.columns)}")
        
        # Show environment distribution
        env_counts = df_meta['organism_name'].value_counts()
        print(f"\n🌍 Top 10 environments:")
        for i, (env, count) in enumerate(env_counts.head(10).items(), 1):
            print(f"  {i:2d}. {env:<40} ({count:,} bioruns)")
        
        # Step 4: Test M2 backend
        print("\n🔬 Step 4: Testing M2 Backend")
        print("-" * 40)
        
        test_environments = [
            "soil metagenome",
            "marine metagenome", 
            "human gut metagenome"
        ]
        
        results = {}
        
        for env in test_environments:
            print(f"\n🌍 Analyzing: {env}")
            try:
                # Get phylum path
                phylum_path = "../Microbe-vis-data/sandpiper1.0.0.condensed.summary.phylum.csv.gz"
                
                # Compute average composition
                avg_series, n_runs = average_composition(
                    env=env,
                    df_meta=df_meta,
                    phylum_path=phylum_path,
                    top_n=5
                )
                
                if n_runs > 0:
                    print(f"✅ Found {n_runs:,} bioruns")
                    print(f"Top 5 phyla:")
                    
                    results[env] = {
                        'n_runs': n_runs,
                        'composition': avg_series.head(5)
                    }
                    
                    for i, (taxon, percent) in enumerate(avg_series.head(5).items(), 1):
                        clean_taxon = taxon.replace('d__Bacteria;p__', '')
                        print(f"  {i}. {clean_taxon:<30} {percent:6.2f}%")
                else:
                    print(f"❌ No bioruns found for '{env}'")
                    
            except Exception as e:
                print(f"❌ Error analyzing '{env}': {e}")
        
        # Step 5: Create visualizations
        if results:
            print("\n📈 Step 5: Creating Visualizations")
            print("-" * 40)
            
            # Prepare data for plotting
            plot_data = []
            for env, data in results.items():
                if 'composition' in data and not data['composition'].empty:
                    for phylum, percent in data['composition'].items():
                        clean_phylum = phylum.replace('d__Bacteria;p__', '')
                        plot_data.append({
                            'Environment': env.replace(' metagenome', ''),
                            'Phylum': clean_phylum,
                            'Percentage': percent
                        })
            
            if plot_data:
                df_plot = pd.DataFrame(plot_data)
                
                # Create heatmap
                pivot_data = df_plot.pivot(index='Phylum', columns='Environment', values='Percentage')
                
                plt.figure(figsize=(12, 8))
                sns.heatmap(pivot_data, annot=True, fmt='.1f', cmap='YlOrRd', 
                            cbar_kws={'label': 'Mean Percentage (%)'})
                plt.title('Top Phyla Comparison Across Environments', fontsize=16, fontweight='bold')
                plt.xlabel('Environment')
                plt.ylabel('Phylum')
                plt.xticks(rotation=45, ha='right')
                plt.tight_layout()
                plt.show()
                
                print("✅ Visualization created!")
        
        print("\n🎉 Demo completed successfully!")
        print("\n💡 Next steps:")
        print("  - Explore different environments")
        print("  - Adjust the 'top_n' parameter")
        print("  - Try the JSON output format")
        
    else:
        print(f"❌ M1 output not found: {m1_output}")

if __name__ == "__main__":
    run_m1_m2_demo()
