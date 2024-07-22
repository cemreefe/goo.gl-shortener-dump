# Goo.gl Shortener Dump

By August 2025, [goo.gl is being deprecated](https://developers.googleblog.com/en/google-url-shortener-links-will-no-longer-be-available/) by Google (surprise!). Hence we need a way to preserve what goo.gl shortened link points to what webpage to refer in the future.

This is primarily a Python script for checking goo.gl's shortened URLs. It generates IDs of a specified length, validates their resolution, and logs the results in a CSV file. As it is theoretically impossible for me to parse them all, please do contribute.

## Features

- Generates IDs of customizable length and characters.
- Checks goo.gl-like URLs for validity.
- Handles various HTTP status codes and exceptions.
- Saves results to a CSV file with configurable batch size and wait time.
- Supports ID range filtering.

## Requirements

- Python 3
- `requests` library
- `termcolor` library

Install the required libraries using:

```sh
pip install requests termcolor
```

## Usage

To run the script, execute:

```sh
python script.py
```

### Configuration

Adjust the following parameters in the script:

- **`length`**: Length of IDs to check (default: 4).
- **`output_file`**: Output CSV file name (default: `'goo_gl_results.csv'`).
- **`wait_time`**: Wait time between requests in seconds (default: 0).
- **`batch_size`**: Number of results to save in each batch (default: 20).
- **`start_id`**: Start ID (inclusive), or `None` to start from the beginning.
- **`end_id`**: End ID (exclusive), or `None` to continue until the end.

Modify these settings as needed:

```python
if __name__ == "__main__":
    length = 4
    output_file = 'goo_gl_results.csv'
    wait_time = 0.5
    batch_size = 20
    start_id = "aaaa"
    end_id = "a999"

    print(f"Starting the script with length {length}, output file '{output_file}', wait time {wait_time} seconds, and batch size {batch_size}.")
    print(f"Checking IDs from {start_id} to {end_id}")
    main(length, output_file, wait_time, batch_size, start_id=start_id, end_id=end_id)
```

## Contributing

If you want to help with parsing:

1. **Find a Range**: Choose a range of IDs you wish to parse. Please check the issue tracker [here](https://github.com/cemreefe/goo.gl-shortener-dump/issues/2) to avoid overlapping with others.
2. **Update the Script**: Modify the `start_id` and `end_id` in the script to match your chosen range.
3. **Run the Script**: Execute the script to generate your CSV file.
4. **Submit Your Results**: Open a pull request with your CSV file only. Any changes to the script should be submitted in a separate pull request.

## Contact

For questions or to discuss this initiative, please open a new issue. If you'd like to contribute and reserve an ID range for parsing, please let me know under [this issue.](https://github.com/cemreefe/goo.gl-shortener-dump/issues/2).
