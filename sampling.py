import pandas as pd
import numpy as np
import glob
import os

# define directory 

data_dir = './Netflix_data/' 

# Our data is divided in 4 files. we will take a proportional sample from each file. Here we define the number of rows to randomly select from each file
PROPORTIONAL_TARGETS = {
    'combined_data_1.txt': 119695,
    'combined_data_2.txt': 134242,
    'combined_data_3.txt': 112469,
    'combined_data_4.txt': 133594
}

# get file names - they have the same structure 
file_names = glob.glob(os.path.join(data_dir, 'combined_data_*.txt'))

#define size of our sample 
TOTAL_TARGET_LINES = 500000

#initialize sampled dfs and film id 
all_sampled_dfs = [] 
current_film_id = None

#start restructuring and sampling 
print(f"Starting Proportional Restructuring and Sampling (Total Target: {TOTAL_TARGET_LINES:,})...")
print("---")

# Here we do a loop where for each file, we set the sample size and we restructure the data.

for file_path in file_names:
    # Use os.path.basename to get the key for the PROPORTIONAL_TARGETS dictionary
    file_base_name = os.path.basename(file_path)
    
    # Get the required sample size for this specific file
    target_sample_size = PROPORTIONAL_TARGETS.get(file_base_name, 0)
    
    if target_sample_size == 0:
        print(f"Warning: Sample size not defined for {file_base_name}. Skipping.")
        continue
        
    print(f"Processing and sampling {file_base_name} (Target: {target_sample_size:,} lines)...")
    
    data_rows = []
    
    # 1. Restructure: Read the data, estract film id if the row contains the film id, and separate customer id, rating and date if the row contains these data ù
    with open(file_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line.endswith(':'):
                current_film_id = int(line[:-1])
            elif line:
                try:
                    customer_id, rating, date = line.split(',')
                    # Store the complete, flattened row
                    data_rows.append([current_film_id, int(customer_id), int(rating), date])
                except ValueError:
                    # Skip malformed rating lines
                    continue
    
    # 2. Convert to DataFrame (only the current file's data)
    current_file_df = pd.DataFrame(
        data_rows, 
        columns=['movie_id', 'customer_id', 'rating', 'date'])
        
# 3. Sample IMMEDIATELY
    if len(current_file_df) < target_sample_size:
        print(f"Warning: File {file_base_name} had fewer lines than the target. Taking all {len(current_file_df):,} lines.")
        sampled_df = current_file_df.copy()
    else:
        # random_state=42 ensures this sample is reproducible
        sampled_df = current_file_df.sample(n=target_sample_size, random_state=42)
    
    # 4. Store the small sample and release the large intermediate DataFrame
    all_sampled_dfs.append(sampled_df)
    del current_file_df # Explicitly free up memory
    
    print(f"Finished sampling from {file_base_name}. Sample size collected: {len(sampled_df):,}")

# 5. Combine the small samples into the final DataFrame
print("---")
print("Combining all small samples...")
final_sampled_data = pd.concat(all_sampled_dfs, ignore_index=True)

# 6. Final Output
output_file = 'netflix_sampled_500k_proportional.csv'
final_sampled_data.to_csv(output_file, index=False)

print(f"Process complete! The final proportional dataset has **{len(final_sampled_data):,}** lines.")
print(f"Saved to **{output_file}**.")
