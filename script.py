import csv
import requests
import os
import time
from urllib.parse import urlparse
from termcolor import colored  # For colored terminal output

class IDGenerator:
    def __init__(self, length, characters="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789", start_id=None, end_id=None):
        self.length = length
        self.characters = characters
        self.num_characters = len(characters)
        self.current_index = [0] * length
        self.start_id = start_id
        self.end_id = end_id
        
        # Set start index
        if self.start_id:
            if len(self.start_id) != self.length:
                raise ValueError(f"Start ID length must be {self.length}")
            self.current_index = self._id_to_index(self.start_id)
        else:
            self.current_index = [0] * length
        
        self.finished = False
    
    def _id_to_index(self, id_str):
        return [self.characters.index(char) for char in id_str]
    
    def _index_to_id(self, index_list):
        return ''.join(self.characters[idx] for idx in index_list)
    
    def _index_to_number(self, index_list):
        number = 0
        for idx in index_list:
            number = number * self.num_characters + idx
        return number
    
    def _id_to_number(self, id_str):
        return self._index_to_number(self._id_to_index(id_str))
    
    def next_id(self):
        id_str = self._index_to_id(self.current_index)
        self._increment_index()
        return id_str
    
    def _increment_index(self):
        for i in range(self.length - 1, -1, -1):
            self.current_index[i] += 1
            if self.current_index[i] >= self.num_characters:
                self.current_index[i] = 0
            else:
                break
    
    def is_finished(self):
        if self.end_id:
            end_number = self._id_to_number(self.end_id)
            current_number = self._id_to_number(self._index_to_id(self.current_index))
            if current_number > end_number:
                return True
        return all(idx == 0 for idx in self.current_index) and not self.start_id
    
    def __lt__(self, other):
        return self._id_to_number(self._index_to_id(self.current_index)) < self._id_to_number(other._index_to_id(other.current_index))
    
    def __le__(self, other):
        return self._id_to_number(self._index_to_id(self.current_index)) <= self._id_to_number(other._index_to_id(other.current_index))
    
    def __gt__(self, other):
        return self._id_to_number(self._index_to_id(self.current_index)) > self._id_to_number(other._index_to_id(other.current_index))
    
    def __ge__(self, other):
        return self._id_to_number(self._index_to_id(self.current_index)) >= self._id_to_number(other._index_to_id(other.current_index))

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
def main(length, output_file='goo_gl_results.csv', wait_time=1, batch_size=20, start_id=None, end_id=None):
    generator = IDGenerator(length, start_id=start_id, end_id=end_id)
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
    wait_time = 0.5  # Wait time between requests in seconds
    batch_size = 20  # Number of results to save in each batch
    
    start_id = "aaPa"  # Start ID (inclusive)
    end_id = "aaP0"    # End ID (exclusive)
    
    print(f"Starting the script with length {length}, output file '{output_file}', wait time {wait_time} seconds, and batch size {batch_size}.")
    print(f"Checking IDs from {start_id} to {end_id}")
    main(length, output_file, wait_time, batch_size, start_id=start_id, end_id=end_id)

