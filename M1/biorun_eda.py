#!/usr/bin/env python3
import pandas as pd
import matplotlib.pyplot as plt
import os

def eda_bioruns(filtered_file: str = "filtered_bioruns.csv"):
    """Perform EDA on filtered bioruns dataset."""
    if not os.path.exists(filtered_file):
        raise FileNotFoundError(f"File '{filtered_file}' not found!")

    df = pd.read_csv(filtered_file)
    print("="*60)
    print("EDA ON FILTERED BIORUNS")
    print("="*60)
    print(f"Total filtered rows: {len(df):,}")
    print(f"Unique biosamples: {df['biosample'].nunique():,}")
    print(f"Unique organisms: {df['organism'].nunique():,}")

    # Bioruns per biosample
    bioruns_per_biosample = df.groupby('biosample').size()
    print("\nBioruns per biosample (first 10):")
    print(bioruns_per_biosample.head(10))
    print(f"Average bioruns per biosample: {bioruns_per_biosample.mean():.2f}")
    print(f"Max bioruns per biosample: {bioruns_per_biosample.max()}")
    print(f"Min bioruns per biosample: {bioruns_per_biosample.min()}")

    # Distribution plot - Bioruns per biosample
    plt.figure(figsize=(10,6))
    plt.hist(bioruns_per_biosample, bins=30, edgecolor='black', alpha=0.7)
    plt.title('Distribution of Bioruns per Biosample', fontsize=14, fontweight='bold')
    plt.xlabel('Number of Bioruns per Biosample')
    plt.ylabel('Number of Biosamples')
    plt.grid(alpha=0.3)
    plt.tight_layout()
    plt.show()

    # Top 10 organisms
    organism_counts = df['organism'].value_counts()
    top_organisms = organism_counts.head(10)
    print("\nTop 10 organisms:")
    print(top_organisms)

    # Bar chart - Top 10 organisms
    plt.figure(figsize=(12,6))
    top_organisms.plot(kind='bar', color='skyblue')
    plt.title('Top 10 Most Common Organisms', fontsize=14, fontweight='bold')
    plt.xlabel('Organism')
    plt.ylabel('Number of Runs')
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    eda_bioruns()
