import os

# Get the current script's directory
script_dir = os.path.dirname(__file__)

# Construct the file path to the parent directory
parent_dir = os.path.abspath(os.path.join(script_dir, os.pardir))

# Now you can use 'parent_dir' in your file path
#file_path = os.path.join(parent_dir, "your_file.txt")

# Use the file_path as needed
print(parent_dir)
