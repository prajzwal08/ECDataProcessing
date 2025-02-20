import os
from datetime import datetime,timedelta
from typing import Tuple, List

def read_initial_time(file, lines_to_skip: int) -> Tuple[str, str]:
    """Read the specified line of the file to extract the initial timestamp.
    
    Args:
        file: File object.
        lines_to_skip: Number of lines to skip before reading the target line.
    
    Returns:
        Tuple containing the raw target line and the extracted initial date string.
    """
    for _ in range(lines_to_skip):
        next(file)  # Skip the specified number of lines
    target_line = next(file).strip()
    initial_date = target_line.split(',')[0].strip('"')
    return target_line, initial_date

def count_lines(filepath: str) -> int:
    """Count the total number of lines in a file.
    
    Args:
        filepath: Path to the file.
    
    Returns:
        Number of lines in the file.
    """
    with open(filepath, 'r') as file:
        return sum(1 for _ in file)

def is_on_the_hour_or_half_hour(timestamp: str) -> bool:
    """Check if the given timestamp is at HH:00:00 or HH:30:00.
    
    Args:
        timestamp: A timestamp string in the format "YYYY-MM-DD HH:MM:SS".
    
    Returns:
        True if the timestamp is at HH:00:00 or HH:30:00, False otherwise.
    """
    try:
        time_part = timestamp.split(' ')[1]  # Extract HH:MM:SS
        return time_part.endswith("00:00") or time_part.endswith("30:00")
    except IndexError:
        return False  # Handle incorrect input format

                
def round_to_half_hour_mark(initial_date: str, frequency: int = 20) -> tuple[datetime, int]:
    """Round up the timestamp to the next HH:00:00 or HH:30:00 and calculate the number of observations.
    
    Args:
        initial_date: A timestamp string in the format "YYYY-MM-DD HH:MM:SS.%f".
        frequency: Observations per minute.
    
    Returns:
        A tuple containing:
        - The rounded-up datetime object.
        - The number of observations until that rounded time.
    """
    current_date = datetime.strptime(initial_date, '%Y-%m-%d %H:%M:%S.%f')

    # Determine next rounded time (HH:00:00 or HH:30:00)
    if current_date.minute < 30:
        next_time = current_date.replace(minute=30, second=0, microsecond=0)
    else:
        next_time = (current_date + timedelta(hours=1)).replace(minute=0, second=0, microsecond=0)

    # Compute time difference in seconds
    time_difference = (next_time - current_date).total_seconds()

    # Calculate the number of observations
    number_of_observations = time_difference* frequency

    return next_time, number_of_observations

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

def process_and_write_lines(lines_to_process: List[str], output_directory: str, site_name: str, block_size : int) -> None:
    """Process and write data lines to an output file in the specified format.
    
    Args:
        lines_to_process: List of lines to be written.
        output_directory: Directory where the output file will be saved.
        site_name: Site identifier.
        frequency: Sampling frequency (samples per second).
        time_block: time(blocks) inm minutes eg: 30 minutes block
    """
    if not lines_to_process:
        print("No lines to process. Skipping.")
        return
    
    date_str = lines_to_process[0].split(',')[0].strip('"')
    output_filename = format_filename(date_str, site_name)
    output_path = os.path.join(output_directory, output_filename)
    
    if os.path.exists(output_path):
        num_lines = count_lines(output_path)
        
        if num_lines == block_size:
            print(f"File {output_filename} exists and is complete. Skipping.")
            return
        elif num_lines < block_size: 
            print(f"Appending to {output_filename} (incomplete file: {num_lines}/{block_size} lines).")
            mode = 'a'
        else:
            print(f"File {output_filename} exists but is larger than expected ({num_lines} lines). Skipping.")
            return
    else: 
        print(f"Writing new file {output_filename}")
        mode = 'w'
        # Write the processed lines to the file
    with open(output_path, mode) as outfile:
        for line in lines_to_process:
            processed_line = '\t'.join([f"{float(entry):.6f}" if entry.strip('"') != "NAN" else "NAN" for entry in line.split(',')[2:9]]) + '\n'
            outfile.write(processed_line)
        

def main():
    """Main function to process all .dat files in the specified directory."""
    file_location = '/Volumes/Group/speuldpro_praj/2010/TOA5/'
    output_directory = '/Volumes/Group/speuldpro_praj/30mins_files'
    # file_location = "/Users/prajzwal/PhD/TOA5/"
    # output_directory = "/Users/prajzwal/PhD/30mins_files/2010"
    frequency = 20  # Data frequency
    time_block = 30 
    site_name = "speuld"

    block_size = time_block*60*frequency
    # Ensure output directory exists
    os.makedirs(output_directory, exist_ok=True)

    # List .dat files in the input location
    dat_files = sorted([f for f in os.listdir(file_location) if f.endswith('.dat')])
   
    # If no files, print error and return
    if not dat_files:
        print("No .dat files found in the specified directory.")
        return

    #check if file path already exists or not
    line_indicator = 4  # Start reading from the 4th line
    # Process the first file
    for dat_file in dat_files:
        
        # get the file path
        file_path = os.path.join(file_location, dat_file)
        print(f"Processing file: {dat_file}")
        
        # Get number of lines in file
        with open(file_path, 'r') as file:
            no_of_lines_in_file = sum(1 for _ in file)
        
        if no_of_lines_in_file == 0:
            print(f"Skipping empty file: {dat_file}")
            continue
            
        # Read the fourth line separately
        with open(file_path, 'r') as file:
            fourth_line, initial_date = read_initial_time(file=file, lines_to_skip=4)
            
            if is_on_the_hour_or_half_hour(initial_date):
                print(f"{dat_file} starts on 00 or 30 minutes")
            
                # Read and process 30-min blocks
                line_indicator = 4  # Start from the fourth line
                
                while line_indicator + block_size <= no_of_lines_in_file:
                    lines_to_process = [fourth_line]  # First line is the fourth line
                    try:
                        lines_to_process.extend(next(file).strip() for _ in range(block_size - 1))
                    except StopIteration:
                        break  # Stop if EOF
                    process_and_write_lines(lines_to_process = lines_to_process, 
                                            output_directory = output_directory, 
                                            site_name = site_name, 
                                            block_size=block_size)
                    line_indicator += block_size
            else:
                print(f"{dat_file} does not start on 00 or 30 minutes")
                
                # Get the lines until the next 00 or 30-minute mark
                next_half_hour_mark, lines_until_next_half_hour = round_to_half_hour_mark(initial_date, frequency)
                lines_to_process = [fourth_line]
                try:
                    lines_to_process.extend(next(file).strip() for _ in range(int(lines_until_next_half_hour) - 1))
                except StopIteration:
                    pass
                
                process_and_write_lines(lines_to_process = lines_to_process, 
                                        output_directory = output_directory, 
                                        site_name = site_name, 
                                        block_size=block_size)
                line_indicator += lines_until_next_half_hour
                
                # Process the remaining full 30-minute blocks
                while line_indicator + block_size <= no_of_lines_in_file:
                    lines_to_process = []
                    try:
                        lines_to_process.extend(next(file).strip() for _ in range(block_size))
                    except StopIteration:
                        break

                    process_and_write_lines(lines_to_process = lines_to_process, 
                                            output_directory = output_directory, 
                                            site_name = site_name, 
                                            block_size=block_size)
                    line_indicator += block_size
                    
            # Process any remaining lines
            remaining_lines = file.readlines()
            if remaining_lines:
                print(f"Processing remaining lines for {dat_file}")
                process_and_write_lines(lines_to_process = remaining_lines, 
                                        output_directory = output_directory, 
                                        site_name = site_name, 
                                        block_size=block_size)
                
if __name__ == "__main__":
    main()