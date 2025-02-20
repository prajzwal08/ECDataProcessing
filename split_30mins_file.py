import os
from datetime import datetime,timedelta
from typing import Tuple, List
from utils import get_next_starting_day

def read_initial_date(file) -> Tuple[str, str]:
    """Read the fourth line of the file to extract the initial timestamp.
    
    Args:
        file: File object.
    
    Returns:
        Tuple containing the raw fourth line and the extracted initial date string.
    """
    for _ in range(4):
        next(file)  # Skip the first three lines
    fourth_line = next(file).strip()
    initial_date = fourth_line.split(',')[0].strip('"')
    return fourth_line, initial_date

def count_lines(filepath: str) -> int:
    """Count the total number of lines in a file.
    
    Args:
        filepath: Path to the file.
    
    Returns:
        Number of lines in the file.
    """
    with open(filepath, 'r') as file:
        return sum(1 for _ in file)

def is_start_of_day(initial_date: str) -> bool:
    """Check if the timestamp represents the start of the day (00:00:00).
    
    Args:
        initial_date: Timestamp string.
    
    Returns:
        True if the timestamp is at 00:00:00, False otherwise.
    """
    return initial_date.split(' ')[1].startswith("00:00:00")

# def compute_lines_to_next_start_day(initial_date: str, frequency: int) -> int:
#     """Calculate the number of lines to skip until the next full-day start.
    
#     Args:
#         initial_date: Initial timestamp string.
#         frequency: Sampling frequency (samples per second).
    
#     Returns:
#         Number of lines to skip.
#     """
#     return 0 if is_start_of_day(initial_date) else get_next_starting_day(initial_date, frequency=frequency)

def format_filename(date_str: str, site_name: str) -> str:
    """Generate a formatted filename based on the timestamp and site name.
    
    Args:
        date_str: Timestamp string.
        site_name: Site identifier.
    
    Returns:
        Formatted filename.
    """
    date_formats = ["%Y-%m-%d %H:%M:%S.%f", "%Y-%m-%d %H:%M:%S"]
    
    for date_format in date_formats:
        try:
            date_time = datetime.strptime(date_str.strip('"'), date_format)
            date_time = date_time.replace(minute=(0 if date_time.minute < 30 else 30), second=0, microsecond=0)
            return f"{date_time.strftime('%Y-%m-%d_%H%M')}_{site_name}.raw"
        except ValueError:
            continue
    raise ValueError(f"Unrecognized date format: {date_str}")

def process_and_write_lines(lines_to_process: List[str], output_directory: str, site_name: str, frequency: int) -> None:
    """Process and write data lines to an output file in the specified format.
    
    Args:
        lines_to_process: List of lines to be written.
        output_directory: Directory where the output file will be saved.
        site_name: Site identifier.
        frequency: Sampling frequency (samples per second).
    """
    
    date_str = lines_to_process[0].split(',')[0].strip('"')
    output_filename = format_filename(date_str, site_name)
    output_path = os.path.join(output_directory, output_filename)
    
    if os.path.exists(output_path):
        if count_lines(output_path) == 30*60*frequency:
            print("File exists and is complete. Skipping.")
            return
        elif count_lines(output_path) < 30*60*frequency: 
            print(f"path exists for {output_filename} and appending to the file because it is incomplete")
            with open(output_path, 'a') as outfile:
                for line in lines_to_process:
                    outfile.write('\t'.join([f"{float(entry):.6f}" if entry.strip('"') != "NAN" else "NAN" for entry in line.split(',')[2:9]]) + '\n')
        else:
            print(f"File exists but is larger than expected. THe no flines is {count_lines(output_path)} Skipping.")
                    
    else: 
        print(f"Writing new file {output_filename}")
        with open(output_path, 'w') as outfile:
            for line in lines_to_process:
                outfile.write('\t'.join([f"{float(entry):.6f}" if entry.strip('"') != "NAN" else "NAN" for entry in line.split(',')[2:9]]) + '\n')
                
def lines_to_next_start_day(initial_date, frequency=20):
    ## THis should be made next start round off to 00:00 or 00:30 
    # Parse the date-time string to a datetime objecy
    current_date = datetime.strptime(initial_date, '%Y-%m-%d %H:%M:%S.%f')
    # Increment the date by one day
    if current_date.minute > 0 and current_date.minute < 30: 
        next_time = current_date + timedelta(minutes=30)
    # Set the time to 00:00:00.000000 (start of the next day)
        next_time_start = next_time.replace(hour=0, minute=30, second=0, microsecond=0)
    # Calculate the time difference in seconds
        time_difference = (next_time_start - current_date).total_seconds()
    # Calculate the number of observations
        number_of_observations = time_difference * frequency
        return next_time_start,number_of_observations
    else: 
        next_time = current_date + timedelta(minutes=30)
    # Set the time to 00:00:00.000000 (start of the next day)
        next_time_start = next_time.replace(minute=0, second=0, microsecond=0)
    # Calculate the time difference in seconds
        time_difference = (next_time_start - current_date).total_seconds()
    # Calculate the number of observations
        number_of_observations = time_difference * frequency
        return next_time_start,number_of_observations
        


def main():
    """Main function to process all .dat files in the specified directory."""
    file_location = '/Volumes/Group/speuldpro_praj/2010/TOA5/'
    output_directory = '/Volumes/Group/speuldpro_praj/30mins_files'
    # file_location = "/Users/prajzwal/PhD/TOA5/"
    # output_directory = "/Users/prajzwal/PhD/30mins_files/2010"
    frequency = 20  # Data frequency
    site_name = "speuld"

    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # List .dat files in the input location
    dat_files = [f for f in os.listdir(file_location) if f.endswith('.dat')]
    # Sort the .dat files
    dat_files.sort()
    # If no files, print error and return
    if not dat_files:
        print("No .dat files found in the specified directory.")
        return
    line_indicator = 4  # Start reading from the 4th line
    block_size = 30 * 60 * frequency  # Number of lines per block
    # Process the first file
    for dat_file in dat_files:
        print(f"Processing file: {dat_file}")
        # get the file path
        file_path = os.path.join(file_location, dat_file)
        #check if file path already exists or not

        no_of_lines_in_file = count_lines(file_path)
        # no_of_lines_in_file = count_lines(os.path.join(file_location,"TOA5_sp_turb101830000.dat"))
        with open(file_path, 'r') as file:
            fourth_line, initial_date = read_initial_date(file)

            if line_indicator <= no_of_lines_in_file:
                # Case 1: If the 4th line marks the start of a new day
                if is_start_of_day(initial_date):
                    print("Start of a new day detected.")
                    while line_indicator + block_size <= no_of_lines_in_file:
                        lines_to_process = [fourth_line]  # Start with the fourth line
                        try:
                            for _ in range(block_size - 1):
                                lines_to_process.append(next(file).strip())
                        except StopIteration:
                            break  # Exit if end of file

                        # Process and write the block
                        process_and_write_lines(lines_to_process, output_directory, site_name, frequency)
                        line_indicator += block_size
                # Case 2: If the 4th line is not the start of a new day
                else:
                    print("Not a start of a new day. Skipping to next start.")
                    print(f"I : {line_indicator} ")
                    next_start_day, lines_until_next_start_day = lines_to_next_start_day(initial_date, frequency)
                    lines_to_process = [fourth_line]
                    for _ in range(int(lines_until_next_start_day) - 1):
                        lines_to_process.append(next(file).strip())

                    # Write the collected initial lines to a file
                    process_and_write_lines(lines_to_process, output_directory, site_name, frequency)
                    line_indicator += lines_until_next_start_day
                    
                    # Continue processing the remaining blocks
                    while line_indicator + block_size <= no_of_lines_in_file:
                        lines_to_process = []
                        for _ in range(block_size):
                            lines_to_process.append(next(file).strip())
                
                        process_and_write_lines(lines_to_process, output_directory, site_name, frequency)
                        line_indicator += block_size
                        print(f"I : {line_indicator} ")
            # Case 3: If there are remaining lines after full blocks, write them to a separate file
            remaining_lines = file.readlines()
            if remaining_lines:
                print("Processing remaining lines.")
                
                process_and_write_lines(remaining_lines, output_directory, site_name, frequency)

# Add to existing file. 
# Check complete file or not.
# problem in writing from second and thrid file. 
                
if __name__ == "__main__":
    main()