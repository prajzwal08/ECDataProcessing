import os
import pandas as pd

def get_start_and_end_times(filename):
    start_time = None
    end_time = None
    
    with open(filename, 'r') as file:
        # Skip the first four lines
        for _ in range(4):
            next(file)
        
        # Read the fifth line to get the start time
        start_time = file.readline().split(',')[0]
        
        # Move the file pointer to the end and read the last line
        file.seek(0, 2)  # Move to the end of the file
        file_size = file.tell()
        
        # Check if the file is empty
        if file_size == 0:
            raise ValueError("File is empty.")
        
        # Read the last line
        buffer_size = 1024
        position = file_size - buffer_size
        
        while position >= 0:
            file.seek(position)
            lines = file.readlines()
            if lines:
                end_time = lines[-1].split(',')[0]
                break
            position -= buffer_size
    
    return start_time, end_time

def process_files_in_directory(directory_path):
    # Create a list to store file data
    file_data = []
    
    # Iterate over all .dat files in the directory
    for filename in os.listdir(directory_path):
        if filename.endswith('.dat') and '103320000' not in filename: # Skip files with '103320000' in the filename , this is corrupted file. 
            file_path = os.path.join(directory_path, filename)
            try:
                # Get start and end times for each file
                start_time, end_time = get_start_and_end_times(file_path)
                # Append data to the list
                file_data.append({'filename': filename, 'start_time': start_time, 'end_time': end_time})
            except Exception as e:
                print(f"Error processing {filename}: {e}")
    
    # Create a DataFrame from the list of file data
    df = pd.DataFrame(file_data)
    
    return df

def main():   
    # Initialize an empty list to store DataFrames from each directory
    all_dataframes = []

    directory_path = '/Volumes/Group/speuldpro_praj/'
    subdirectories = [d for d in os.listdir(directory_path) if os.path.isdir(os.path.join(directory_path, d))]
    
    for subdirectory in subdirectories:
        subdirectory_path = os.path.join(directory_path, subdirectory,'TOA5')
        df = process_files_in_directory(subdirectory_path)
        all_dataframes.append(df)
    
    # Concatenate all DataFrames in the list
    combined_df = pd.concat(all_dataframes, ignore_index=True)
    
    # Write the combined DataFrame to a CSV file
    csv_output_path = 'file_times.csv'
    combined_df.to_csv(csv_output_path, index=False)

    print(f"Data has been written to {csv_output_path}")
    
if __name__ == "__main__":
    main()

