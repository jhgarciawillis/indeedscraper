import os
import math

def remove_duplicates_and_split():
    print("Starting duplicate removal and file splitting process...")

    # Get the directory of the current script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    
    # Define input file path
    input_file = os.path.join(script_dir, "indeed_job_links.txt")

    # Check if input file exists
    if not os.path.exists(input_file):
        print(f"Error: Input file '{input_file}' not found.")
        return

    print(f"Reading links from '{input_file}'...")
    
    # Read links and remove duplicates
    unique_links = set()
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                link = line.strip()
                if link:  # Ignore empty lines
                    unique_links.add(link)
    except IOError as e:
        print(f"Error reading input file: {e}")
        return

    print(f"Found {len(unique_links)} unique links.")

    # Sort the unique links
    sorted_links = sorted(unique_links)

    # Calculate the number of files needed
    num_files = math.ceil(len(sorted_links) / 500)

    # Write unique links to output files
    for i in range(num_files):
        output_file = os.path.join(script_dir, f"ind_job_link_{i+1}.txt")
        start_index = i * 500
        end_index = min((i + 1) * 500, len(sorted_links))
        
        print(f"Writing links {start_index+1} to {end_index} to '{output_file}'...")
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                for link in sorted_links[start_index:end_index]:
                    f.write(link + '\n')
        except IOError as e:
            print(f"Error writing to output file: {e}")
            return

        print(f"Successfully wrote {end_index - start_index} links to '{output_file}'.")

    print(f"Split {len(sorted_links)} unique links into {num_files} files.")
    print("Duplicate removal and file splitting process completed.")

if __name__ == "__main__":
    print("Starting script to remove duplicate links and split into multiple files...")
    remove_duplicates_and_split()
    print("Script finished.")