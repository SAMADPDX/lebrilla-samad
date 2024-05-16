# -*- coding: utf-8 -*-
"""
Created on Wed May 15 15:57:19 2024

@author: Lebrilla Lab
"""

import mysql.connector
import pandas as pd

# Database configuration and connection
config = {
    'host': 'DESKTOP-631Q7RC',
    'user': 'Xavier',
    'password': 'Glyco5441',
    'database': 'glycomics'
}
connection = mysql.connector.connect(**config)
cursor = connection.cursor()

# Load the training data from Excel
data = pd.read_excel('Z:/Abdel/Classification/Fragment_Search_Cytokine_2_Training_Abdel.xlsx')

# Get unique file names
file_list = data['data_file'].unique()

# Fetch minimum retention time for each file for compound '5_4_0_0' as the marker
min_rt_list = []
for file in file_list:
    query = "SELECT MIN(rt) FROM compounds WHERE file_name = %s AND compound_name = '5_4_0_0'"
    cursor.execute(query, (file,))
    result = cursor.fetchone()
    min_rt = result[0] 
    min_rt_list.append(min_rt)

# Create DataFrame from fetched data
marker_df = pd.DataFrame(list(zip(file_list, min_rt_list)), columns=['File Name', 'Marker'])

# Define the function to calculate RSD
def RSD(dataset):
    std = dataset.std()
    mean = dataset.mean()
    rsd = (std / mean) * 100
    return rsd

# Calculate RSD for the Marker column (assuming all min_rt are not None for the calculation)
rsd_marker = RSD(marker_df['Marker'].dropna())  # Use dropna() to ensure no NaN values interfere
print(f"The RSD of the Marker '5_4_0_0' retention times is {rsd_marker:.2f}%")

# Close the database connection
cursor.close()
connection.close()

# Filter data for compound '5_4_1_0'
filtered_data = data[data['compound_name'] == '5_4_1_0']

# Merge marker DataFrame with filtered compound data DataFrame using the same file names
data_with_markers = pd.merge(filtered_data, marker_df, left_on='data_file', right_on='File Name', how='left')

# Normalize the retention times by dividing by the marker RT
data_with_markers['normalized_rt'] = data_with_markers['rt'] / data_with_markers['Marker']

# Initialize a new column to store the classification (default to "unknown")
data_with_markers['classification'] = 'unknown'

# Mark "core" and "ant" based on the fragment names
data_with_markers.loc[data_with_markers['fragment'].str.contains('core', case=False), 'classification'] = 'core'
data_with_markers.loc[data_with_markers['fragment'].str.contains('ant', case=False), 'classification'] = 'ant'

# Specify the output path and write the normalized data to a new Excel file
output_path = r'Z:/Abdel/Classification\five_four_one_zero_cytokine_fragment_training_new_normalized_5_4_0_0.xlsx'
data_with_markers.to_excel(output_path, index=False)

print(f"Normalized data with 5_4_0_0 Marker written to: {output_path}")