import pandas as pd
import os

def main():
    source_file = "Microbe-vis-data/sandpiper1.0.0.condensed.biosample-metadata.csv.gz"
    output_file = "relevant_columns_data.csv.gz"

    if not os.path.exists(source_file):
        print(f"ERROR: File '{source_file}' not found!")
        return

    # רשימת העמודות שאתה רוצה לחלץ
    columns_to_extract = [
        "collection_date",
        "geo_loc_name",
        "lat_lon",
        "isolation_source",
        "host"
    ]

    try:
        print(f"Loading only the specified columns from '{source_file}'...")
        
        # טוען את הקובץ המקורי עם העמודות שבחרת בלבד
        # השימוש ב-usecols גורם לפאנדס לטעון רק את העמודות האלה,
        # מה שחוסך המון זיכרון וזמן
        df_selected = pd.read_csv(source_file, 
                                  compression='gzip', 
                                  usecols=columns_to_extract)
        
        print("Done loading. Saving the data to a new file...")

        # שומר את הנתונים החדשים לקובץ Gzip חדש
        df_selected.to_csv(output_file, compression='gzip', index=False)

        print(f"✅ Success! The new file '{output_file}' has been created.")
        print(f"It contains {df_selected.shape[0]} rows and {df_selected.shape[1]} columns.")

    except ValueError:
        print(f"ERROR: One or more of the specified columns were not found in the file.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()