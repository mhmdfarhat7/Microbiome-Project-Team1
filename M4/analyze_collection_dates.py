import pandas as pd
import os

def main():
    data_file = "sandpiper1.0.0.condensed.biosample-metadata.csv.gz"
    if not os.path.exists(data_file):
        print(f"ERROR: File '{data_file}' not found!")
        return

    target_column = "collection_date"

    try:
        df = pd.read_csv(data_file, compression='gzip', usecols=[target_column])

        total_rows = len(df)

        non_empty_rows = df[target_column].count()

        print(f"\n📊 Summary for column '{target_column}':")
        print(f"Total rows in column: {total_rows}")
        print(f"Non-empty rows in column: {non_empty_rows}")

        df_filtered = df.dropna(subset=[target_column])

        print(f"\n📊 First 10 rows of column '{target_column}' without NaN values:")
        print(df_filtered[target_column].head(10).to_string(index=False))

    except ValueError:
        print(f"ERROR: Column '{target_column}' not found in the file.")
    except Exception as e:
        print(f"ERROR loading dataset: {e}")

if __name__ == "__main__":
    main()