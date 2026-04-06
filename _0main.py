import os
import sys

# Import the necessary functions from each script
from _1indeed_search import main as search_main
from _2r_duplicate_links import remove_duplicates_and_split
from _3indeed_scraper import main as scraper_main
from _4r_duplicate_rows import main as duplicate_rows_main

def run_script(script_name, function):
    print(f"\nRunning {script_name}...")
    try:
        function()
        print(f"{script_name} completed successfully.")
    except Exception as e:
        print(f"An error occurred while running {script_name}: {e}")
        sys.exit(1)

def main():
    # Ensure we're in the correct directory
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)

    # Ask user which script to start from
    while True:
        start_from = input("Enter the number of the script to start from (1, 2, 3, or 4): ")
        if start_from in ['1', '2', '3', '4']:
            start_from = int(start_from)
            break
        else:
            print("Invalid input. Please enter 1, 2, 3, or 4.")

    # Dictionary to map numbers to script functions
    scripts = {
        1: ("1. Indeed Search", search_main),
        2: ("2. Remove Duplicate Links", remove_duplicates_and_split),
        3: ("3. Indeed Scraper", scraper_main),
        4: ("4. Remove Duplicate Rows", duplicate_rows_main)
    }

    # Run the scripts in order, starting from the user's choice
    for i in range(start_from, 5):
        script_name, script_function = scripts[i]
        run_script(script_name, script_function)

    print("\nAll selected scripts have been executed successfully.")

if __name__ == "__main__":
    main()