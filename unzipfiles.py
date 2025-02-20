import os
import zipfile

def unzip_all_files(source_dir, destination_base_folder):
    # Check if the source directory exists
    if not os.path.isdir(source_dir):
        raise Exception('Source directory does not exist.')
    
    # Walk through the source directory and its subdirectories
    for root, dirs, files in os.walk(source_dir):
        # Check each directory to see if it's a valid year
        for dir_name in dirs:
            if dir_name.isdigit() and 2010 <= int(dir_name) <= 2012: # just for remaining years 
                year = dir_name
                # Define the specific destination folder for the current year
                year_destination_folder = os.path.join(destination_base_folder, year, 'TOB')
                
                # Create the destination folder if it doesn't exist
                if not os.path.isdir(year_destination_folder):
                    os.makedirs(year_destination_folder)
                
                # File to log the errors
                error_log_file = os.path.join(year_destination_folder, 'error_log.txt')
                
                # Ensure the error log file is created and emptied if it already exists
                with open(error_log_file, 'w') as log:
                    log.write('Error Log\n')
                    log.write('=========\n\n')
                
                if 2014 <= int(year) <= 2019:
                    # For years 2014 to 2019, go inside 'turb' directory
                    year_dir_path = os.path.join(root, dir_name, 'turb')
                else:
                    # For years not in 2014 to 2019, use the year's directory
                    year_dir_path = os.path.join(root, dir_name)
                
                for sub_root, _, files in os.walk(year_dir_path): # no get different root so the loop keeps running 
                    for file in files:
                        if file.endswith('.zip'):
                            # Full path to the current .zip file
                            zip_file_path = os.path.join(sub_root, file)
                            
                            # Check if any files from the zip already exist in the destination folder
                            try:
                                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                                    all_files_exist = all(
                                        os.path.isfile(os.path.join(year_destination_folder, member)) 
                                        for member in zip_ref.namelist()
                                    )
                                
                                if all_files_exist:
                                    print(f'Skipping already unzipped file: {zip_file_path}')
                                    continue
                            
                                # Try to unzip the file into the destination folder
                                with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
                                    zip_ref.extractall(year_destination_folder)
                                print(f'Unzipped: {zip_file_path}')
                            except Exception as e:
                                # Log the error to the error log file
                                with open(error_log_file, 'a') as log:
                                    log.write(f'Failed to unzip {zip_file_path}: {e}\n')
                                print(f'Error unzipping {zip_file_path}. Check {error_log_file} for details.')
    
    print(f'All .zip files have been processed. Errors, if any, are logged in the respective year folders.')

# Define the source and destination base folders
source_folder = '/Volumes/Group/Siteswrs/Speuld/data/1_raw/old'
destination_base_folder = '/Volumes/Group/speuldpro_praj'

# Call the function
unzip_all_files(source_folder, destination_base_folder)
