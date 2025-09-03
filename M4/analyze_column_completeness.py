import pandas as pd
import os

def main():
    data_file = "Microbe-vis-data/sandpiper1.0.0.condensed.biosample-metadata.csv.gz"
    
    if not os.path.exists(data_file):
        print(f"ERROR: File '{data_file}' not found!")
        return

    # Number of rows to sample from the file
    sample_rows = 10000

    try:
        # Read a sample of the file
        print(f"Loading first {sample_rows} rows from the file...")
        # Note: The DtypeWarning can be ignored for this specific task
        df_sample = pd.read_csv(data_file, compression='gzip', nrows=sample_rows, low_memory=False)

        # Create a dictionary to hold the non-null count for each column
        non_null_counts = {}
        for column in df_sample.columns:
            non_null_counts[column] = df_sample[column].count()

        # Convert the dictionary to a DataFrame for easy sorting
        counts_df = pd.DataFrame(non_null_counts.items(), columns=['Column', 'Non-Null Count'])

        # Sort the columns by non-null count in descending order
        sorted_counts = counts_df.sort_values(by='Non-Null Count', ascending=False)
        
        # Select the top 10 columns
        top_10_columns = sorted_counts.head(5000)
        
        print("\n📊 Top 10 columns by number of non-null values (based on a 5000-row sample):")
        print(top_10_columns.to_string(index=False))

    except Exception as e:
        print(f"ERROR loading dataset: {e}")

if __name__ == "__main__":
    main()