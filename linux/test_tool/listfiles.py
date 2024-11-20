import os

def list_files_recursively(folder_path):
    """
    Lists the full paths of all files in the given folder and its subfolders.

    Parameters:
        folder_path (str): The path to the folder to search for files.

    Returns:
        list: A list of full file paths for all files in the folder and subfolders.
    """
    if not os.path.isdir(folder_path):
        raise ValueError(f"The path '{folder_path}' is not a valid directory.")
    
    # Walk through the directory and collect full file paths
    file_paths = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            file_paths.append(os.path.join(root, file))
    
    return file_paths

# Example usage
folder_path = "/applications/logs/fdc"
files = list_files_recursively(folder_path)

if files:
    print("Files in folder and subfolders:")
    for file in files:
        print(file)
else:
    print("No files found in the folder.")

