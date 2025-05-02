import pandas as pd

# Load the CSV file, handling extra commas or empty columns
df = pd.read_csv('course\\Fact_Sales_2 - Copy.csv', engine='python')

# Remove any trailing commas (empty columns) in the dataframe
df = df.loc[:, ~df.columns.str.contains('^Unnamed')]

# Convert the 'transactional_date' column to datetime, standardizing the format
df['transactional_date'] = pd.to_datetime(df['transactional_date'], errors='coerce')

# Save the cleaned CSV file
df.to_csv('cleaned_file.csv', index=False)
