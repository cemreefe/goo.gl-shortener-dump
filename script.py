import csv
import requests
import os
import time
from urllib.parse import urlparse
from termcolor import colored  # For colored terminal output

class IDGenerator:
    def __init__(self, length, characters="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"):
        self.length = length
        self.characters = characters
        self.current_index = [0] * length  # Initialize index array
        self.total_generated = 0  # Counter for total generated IDs
        
    def next_id(self):
        id_str = ''.join(self.characters[idx] for idx in self.current_index)
        self._increment_index()
        self.total_generated += 1
        return id_str
    
    def _increment_index(self):
        for i in range(self.length - 1, -1, -1):
            self.current_index[i] += 1
            if self.current_index[i] >= len(self.characters):
                self.current_index[i] = 0
            else:
                break
    
    def is_finished(self):
        return all(idx == 0 for idx in self.current_index) and self.total_generated > 0

# Function to check if a goo.gl-like link resolves to a valid URL
def check_goo_gl_link(short_id):
    base_url = "https://goo.gl/"
    url = base_url + short_id
    try:
        response = requests.head(url, allow_redirects=False)
        
        # Define lists for configurable status codes
        valid_statuses = [200, 302, 400]
        invalid_statuses = [404]
        sleep_error_statuses = [403, 429]  # Example: 403 Forbidden, 429 Too Many Requests
        
        # Check response status code
        if response.status_code in valid_statuses:
            print(colored(f"{short_id} -> {url} : {response.status_code}", 'green'))
            if response.status_code == 302:
                return response.headers['Location']
            else:
                return url
        
        elif response.status_code in invalid_statuses:
            print(colored(f"{short_id} -> {url} : {response.status_code}", 'grey'))
            return None
        
        elif response.status_code in sleep_error_statuses:
            print(colored(f"{short_id} -> {url} : {response.status_code}", 'red'))
            print(colored("Sleeping for 2 minutes...", 'red'))
            time.sleep(120)  # Sleep for 2 minutes (120 seconds)
            return None
        
        else:
            print(colored(f"{short_id} -> {url} : {response.status_code}", 'yellow'))
            return None
    
    # Handle connection errors and timeouts
    except requests.RequestException as e:
        print(colored(f"Request failed for {short_id}: {str(e)}", 'red'))
        return None

# Function to save results to a CSV file
def save_to_csv(results, filename):
    with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        for short_id, resolved_url in results.items():
            writer.writerow([short_id, resolved_url])

# Function to load IDs that have already been checked from existing CSV file
def load_checked_ids(filename):
    checked_ids = set()
    if os.path.exists(filename):
        with open(filename, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.reader(csvfile)
            try:
                next(reader)  # Skip header row
            except StopIteration:
                pass  # File is empty, no header to skip
            
            for row in reader:
                if row:
                    checked_ids.add(row[0])  # Assuming the short ID is in the first column
    return checked_ids

# Main function to iterate through all possible IDs of specified lengths
def main(length, output_file='goo_gl_results.csv', wait_time=1, batch_size=20):
    generator = IDGenerator(length)
    checked_ids = load_checked_ids(output_file)
    results = {}
    total_ids = len(generator.characters) ** length
    print(f"Total IDs to check: {total_ids}")

    while not generator.is_finished():
        short_id = generator.next_id()
        if short_id in checked_ids:
            print(colored(f"Skipping {short_id}, already checked", 'grey'))
            continue  # Skip IDs that have already been checked
        
        resolved_url = check_goo_gl_link(short_id)
        if resolved_url:
            results[short_id] = resolved_url
        
        # Save results in batches
        if len(results) >= batch_size:
            save_to_csv(results, output_file)
            print(f"Progress: {len(results)} / {total_ids}")
            results = {}  # Clear results batch
            time.sleep(wait_time)  # Add a configurable wait time between batches
    
    # Save any remaining results
    if results:
        save_to_csv(results, output_file)
        print(f"Progress: {len(results)} / {total_ids}")
    
    print(f"Finished. Results saved to {output_file}")

if __name__ == "__main__":
    # Adjust length, output_file, wait_time, and batch_size as needed
    length = 4  # Length of IDs to check
    output_file = 'goo_gl_results.csv'
    wait_time = 0.1  # Wait time between requests in seconds
    batch_size = 20  # Number of results to save in each batch
    
    print(f"Starting the script with length {length}, output file '{output_file}', wait time {wait_time} seconds, and batch size {batch_size}.")
    main(length, output_file, wait_time, batch_size)

