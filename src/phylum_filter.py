#!/usr/bin/env python3
import pandas as pd
import os

def main():
    # תיקיית הסקריפט
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # קבצי מקור
    summary_file = os.path.join(script_dir, "sandpiper1.0.0.condensed.summary.phylum.csv.gz")
    bioruns_file = os.path.join("data", "processed", "filtered_bioruns.csv")

    # קובץ פלט Parquet באותה תיקיה של הסקריפט
    output_file = os.path.join(script_dir, "sandpiper1.0.0.condensed.summary.phylum.filtered.parquet")

    # בדיקות קיום
    if not os.path.exists(summary_file):
        print(f"❌ ERROR: File not found: {summary_file}")
        return
    if not os.path.exists(bioruns_file):
        print(f"❌ ERROR: File not found: {bioruns_file}")
        return

    print("✅ Loading filtered_bioruns.csv to collect run_accession IDs...")
    df_bioruns = pd.read_csv(bioruns_file, usecols=["run_accession"])
    run_ids = set(df_bioruns["run_accession"].dropna().unique())
    print(f"Found {len(run_ids):,} unique run_accession IDs")

    print("✅ Filtering summary.phylum file...")
    filtered_chunks = []
    chunk_size = 200_000  # אפשר לשחק עם הגודל לפי הזיכרון שלך

    for chunk in pd.read_csv(summary_file, compression="gzip", chunksize=chunk_size):
        filtered = chunk[chunk["biorun"].isin(run_ids)]
        if not filtered.empty:
            filtered_chunks.append(filtered)

    if filtered_chunks:
        df_filtered = pd.concat(filtered_chunks, ignore_index=True)
        # שמירה כ־Parquet
        df_filtered.to_parquet(output_file, engine="pyarrow", index=False)
        print(f"🎉 Done! Filtered file saved to: {output_file}")
        print(f"Remaining rows: {len(df_filtered):,}")
    else:
        print("⚠️ No matching rows found!")

if __name__ == "__main__":
    main()
