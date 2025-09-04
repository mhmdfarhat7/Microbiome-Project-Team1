import pandas as pd
import os

def main():
    # תיקיית הסקריפט הנוכחי
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # קובץ מקור biosample-metadata
    source_file = os.path.join(script_dir, "sandpiper1.0.0.condensed.biosample-metadata.csv.gz")
    
    # קובץ biosample IDs תקין מתוך biorun_metadata_clean
    biorun_file = os.path.join(script_dir, "..", "data", "processed", "biorun_metadata_clean.parquet")
    
    # תיקיית פלט
    output_dir = os.path.join(script_dir, "..", "data", "processed")
    os.makedirs(output_dir, exist_ok=True)
    
    # קובץ פלט ראשי
    output_file = os.path.join(output_dir, "relevant_columns_data.csv.gz")

    if not os.path.exists(source_file):
        print(f"ERROR: File '{source_file}' not found!")
        return
    if not os.path.exists(biorun_file):
        print(f"ERROR: File '{biorun_file}' not found!")
        return

    # רשימת העמודות שאתה רוצה לחלץ (יחד עם biosample לצורך החיתוכים)
    columns_to_extract = [
        "biosample",
        "collection_date",
        "geo_loc_name",
        "lat_lon",
        "isolation_source",
        "host"
    ]

    # ערכים לא רצויים להסרה
    unwanted_values = {
        "not collected","Not Collected","Not collected","NOT COLLECTED",
        "Not Available", "not available",
        "not provided", 
        "missing", "N/A", "na", "NA",
        "none", "None",
        "unspecified", 
        "not determined","Not Determined",
        "restricted access"
    }

    try:
        print(f"Loading biosample metadata from '{source_file}'...")
        df_selected = pd.read_csv(
            source_file, 
            compression='gzip', 
            usecols=columns_to_extract
        )

        print(f"Loading valid biosamples from '{biorun_file}'...")
        df_biorun = pd.read_parquet(biorun_file)
        valid_biosamples = set(df_biorun['biosample'].dropna().unique())

        print(f"Filtering biosamples: keeping only rows with biosample in biorun_metadata_clean...")
        before = len(df_selected)
        df_selected = df_selected[df_selected['biosample'].isin(valid_biosamples)]
        after = len(df_selected)
        print(f"✓ Filtered: {before:,} → {after:,} rows remain")

        # שמירה של הקובץ הראשי
        print("Saving the filtered main file...")
        df_selected.to_csv(output_file, compression='gzip', index=False)
        print(f"✅ Main file '{output_file}' created with {df_selected.shape[0]} rows.")

        # יצירת קבצים נפרדים לכל עמודה
        for col in columns_to_extract:
            if col == "biosample":
                continue  # לא יוצרים קבצים לעמודת biosample עצמה

            print(f"Processing column: {col}")

            # קובץ 1: העמודה + biosample (עם סינון ערכים לא רצויים)
            col_with_biosample = df_selected[["biosample", col]].dropna()
            col_with_biosample = col_with_biosample[
                ~col_with_biosample[col].isin(unwanted_values)
            ]
            file_with_biosample = os.path.join(output_dir, f"{col}_with_biosample.csv.gz")
            col_with_biosample.to_csv(file_with_biosample, compression='gzip', index=False)

            # קובץ 2: ערכים ייחודיים בלבד (אחרי סינון)
            unique_values = df_selected[[col]].dropna()
            unique_values = unique_values[
                ~unique_values[col].isin(unwanted_values)
            ].drop_duplicates()
            file_unique = os.path.join(output_dir, f"{col}_unique.csv.gz")
            unique_values.to_csv(file_unique, compression='gzip', index=False)

            print(f"   ➡ Saved {file_with_biosample}")
            print(f"   ➡ Saved {file_unique}")

        print("🎉 All files created successfully in data/processed")

    except ValueError as ve:
        print(f"ERROR: One or more of the specified columns were not found in the file. {ve}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    main()
