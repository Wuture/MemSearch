import pandas as pd
import difflib

def load_data(file_path):
    try:
        # Use tab as the delimiter for reading the tab-separated values file
        csv_file = pd.read_csv(file_path, delimiter='\t')
        # print (csv_file)
        return csv_file
    except Exception as e:
        print(f"Failed to load data from {file_path}: {str(e)}")
        return pd.DataFrame()

def preprocess_data(df):
    # Clean and preprocess text data
    df['text'] = df['text'].astype(str).str.strip()  # Ensure text is treated as string and whitespace is removed
    return df

def compare_texts(df1, df2):
    # Group texts by block and concatenate them within each group
    text1 = df1.groupby(['page_num', 'block_num'])['text'].apply(' '.join)
    text2 = df2.groupby(['page_num', 'block_num'])['text'].apply(' '.join)

    # Compare each block's concatenated text
    changes = []
    for (page, block), txt1 in text1.items():
        txt2 = text2.get((page, block), "")
        # Generate diff output
        diff = difflib.unified_diff(txt1.split(), txt2.split(), lineterm='', fromfile='img1', tofile='img2')
        changes.extend(diff)
    return changes

# Define file paths
file_path1 = 'diff_test/Arc_2024-04-09 15:02:20.txt'  # Adjust file path and extension if necessary
file_path2 = 'diff_test/Arc_2024-04-09 15:02:27.txt'

# Load your data
df1 = load_data(file_path1)
df2 = load_data(file_path2)

# Preprocess data
df1 = preprocess_data(df1)
df2 = preprocess_data(df2)

# Compare and get changes
changes = compare_texts(df1, df2)

# save the changes to a file
changes_file_path = 'diff_test/changes.txt'

with open(changes_file_path, 'w') as file:
    file.write('\n'.join(changes))
    
