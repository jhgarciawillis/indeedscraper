import pandas as pd
import os

def remove_duplicates(file_path):
    print(f"Reading Excel file: {file_path}")
    df = pd.read_excel(file_path)
    
    print("Original number of rows:", len(df))
    
    # Identify duplicate rows based on columns A-K
    columns_to_check = df.columns[:-1]  # All columns except the last one
    duplicates = df.duplicated(subset=columns_to_check, keep='first')
    
    # Remove duplicate rows
    df_cleaned = df[~duplicates]
    
    print("Number of rows after removing duplicates:", len(df_cleaned))
    print("Number of duplicates removed:", len(df) - len(df_cleaned))
    
    # Save the cleaned dataframe back to Excel
    output_file = os.path.splitext(file_path)[0] + '_cleaned.xlsx'
    df_cleaned.to_excel(output_file, index=False)
    print(f"Cleaned data saved to: {output_file}")

def main():
    # Specify the path to your Excel file
    file_path = 'indeed.xlsx'  # Change this to your file path if different
    
    if not os.path.exists(file_path):
        print(f"Error: File '{file_path}' not found.")
        return
    
    remove_duplicates(file_path)

if __name__ == "__main__":
    main()