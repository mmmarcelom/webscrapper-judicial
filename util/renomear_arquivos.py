import os

# List all files in the directory
files = [f for f in os.listdir(download_folder) if os.path.isfile(os.path.join(download_folder, f))]

# Rename files
for old_name in files:
    # Construct the new name as per your requirements
    new_name = old_name.replace('REQUISIÇÃO DE PAGAMENTO ', '')  # Modify this line based on your naming convention

    # Full path to the files
    print(os.path.join(download_folder, old_name))
    print(os.path.join(download_folder, new_name))
    old_path = os.path.join(download_folder, old_name)
    new_path = os.path.join(download_folder, new_name)

    # Rename the file
    os.rename(old_path, new_path)

print("Files renamed successfully.")