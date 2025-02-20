import pandas as pd
from datetime import datetime
import matplotlib.pyplot as plt

# Purpose: This script reads a CSV file containing start and end times, processes these times,
#          and identifies the missing date ranges for a specified year.

# Load the data from the CSV file
df = pd.read_csv("file_times.csv")

# Remove all quotation marks from 'start_time' and 'end_time' columns
df['start_time'] = df['start_time'].str.replace('"', '')
df['end_time'] = df['end_time'].str.replace('"', '')

# Ensure 'start_time' and 'end_time' are strings
df['start_time'] = df['start_time'].astype(str)
df['end_time'] = df['end_time'].astype(str)

# # Convert 'start_time' and 'end_time' to datetime objects
df_selected = df[df['end_time'] != "nan"]
# Convert to datetime format
# Homogenize the format: add '.00' to times without milliseconds
# Homogenize the format: ensure 2 digits for milliseconds


df_selected['start_time'] = df_selected['start_time'].apply(
    lambda x: x + '.00' if '.' not in x else x if len(x.split('.')[-1]) == 2 else x + '0'
)

df_selected['end_time'] = df_selected['end_time'].apply(
    lambda x: x + '.00' if '.' not in x else x if len(x.split('.')[-1]) == 2 else x + '0'
)
df_selected['start_time'] = pd.to_datetime(df_selected['start_time'], format='%Y-%m-%d %H:%M:%S.%f')

df_selected['end_time'] = pd.to_datetime(df_selected['end_time'], format='%Y-%m-%d %H:%M:%S.%f')


# Define the year you are interested in
start_year = 2010
end_year = 2018
start_of_year = datetime(start_year, 1, 1)
end_of_year = datetime(end_year, 12, 31)

# Sort the DataFrame by 'start_time'
df_selected = df_selected.sort_values(by='start_time')


# Initialize a list to hold the covered ranges
covered_ranges = []

# Extract the covered ranges from the DataFrame
for _, row in df_selected.iterrows():
    covered_ranges.append((row['start_time'], row['end_time']))

# Sort the ranges by their start time
covered_ranges.sort()

# Initialize a list to hold the missing ranges
missing_ranges = []


# Track the end of the last covered range
current_end = start_of_year
# current_end = covered_ranges[1070][1]
# Identify gaps between the covered ranges

    # Identify gaps between the covered ranges
for start, end in covered_ranges:
    if start > current_end:
        missing_ranges.append((current_end, start))
    current_end = max(current_end, end)


# save the df
df_selected.to_csv('available_times.csv')
# Output the missing ranges
for start, end in missing_ranges:
    print(f"Missing range: {start} to {end}")
    # Write the missing ranges to a file
with open('missing_ranges.txt', 'w') as f:
    for start, end in missing_ranges:
        f.write(f"Missing range: {start} to {end}\n")
    
# Generate a date range covering each day from the start to the end of the specified years
all_days = pd.date_range(start=start_of_year, end=end_of_year, freq='D')

# Initialize a Series to hold binary coverage: 1 for covered, NaN for missing (NaN helps in not plotting those values)
coverage_series = pd.Series(index=all_days, dtype=float)
coverage_series[:] = float('NaN')  # Start with NaN for all days

# Mark covered days with 1
for start, end in covered_ranges:
    coverage_series[start:end] = 1

# Plot only the covered periods
plt.figure(figsize=(12, 4))
plt.plot(coverage_series.index, coverage_series.values, color='blue', label='Covered', drawstyle='steps-post')

# Customize the plot
plt.title(f"Covered Date Ranges from {start_year} to {end_year}")
plt.xlabel("Date")
plt.ylabel("Coverage")
plt.ylim(0.9, 1.1)  # Adjust the y-axis to zoom in on the coverage line
plt.yticks([1], ["Covered"])
plt.grid(True)

# Save and display the plot
plt.savefig('coverage_only.png')



