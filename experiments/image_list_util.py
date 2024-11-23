import os

# Root directory for images
root_dir = "./experiments/data/by_class"

# List of main folders and their corresponding labels
folders = [
    '70', '36', '52', '6b', '51', '43', '54', '53', '6d', '65', '4c', '69', '79', '71', '31', 
    '55', '33', '6a', '47', '59', '58', '4f', '44', '46', '77', '6c', '45', '63', '38', '6f', 
    '64', '67', '42', '56', '39', '73', '34', '78', '62', '30', '4d', '75', '32', '4e', '41', 
    '6e', '4b', '57', '72', '66', '68', '7a', '49', '4a', '74', '37', '48', '76', '5a', '50', 
    '61', '35'
]

# Mapping from folder names to labels
folder_to_label = {
    "30": "0", "31": "1", "32": "2", "33": "3", "34": "4", "35": "5",
    "36": "6", "37": "7", "38": "8", "39": "9", "41": "A", "42": "B",
    "43": "C", "44": "D", "45": "E", "46": "F", "47": "G", "48": "H",
    "49": "I", "4a": "J", "4b": "K", "4c": "L", "4d": "M", "4e": "N",
    "4f": "O", "50": "P", "51": "Q", "52": "R", "53": "S", "54": "T",
    "55": "U", "56": "V", "57": "W", "58": "X", "59": "Y", "5a": "Z",
    "61": "a", "62": "b", "63": "c", "64": "d", "65": "e", "66": "f",
    "67": "g", "68": "h", "69": "i", "6a": "j", "6b": "k", "6c": "l",
    "6d": "m", "6e": "n", "6f": "o", "70": "p", "71": "q", "72": "r",
    "73": "s", "74": "t", "75": "u", "76": "v", "77": "w", "78": "x",
    "79": "y", "7a": "z"
}

# Output file path
output_file = "./experiments/data_labels.txt"

# Open the file to write
with open(output_file, "w") as f:
    for folder in folders:
        folder_path = os.path.join(root_dir, folder)
        label = folder_to_label.get(folder, None)
        
        if label is None:
            print(f"Warning: No label mapping found for folder {folder}. Skipping.")
            continue

        # Check if the folder exists
        if not os.path.exists(folder_path):
            print(f"Folder {folder_path} does not exist. Skipping.")
            continue
        
        # Iterate through each subfolder (e.g., hsf_0, hsf_1, ..., train_{folder})
        subfolders = [sf for sf in os.listdir(folder_path) if os.path.isdir(os.path.join(folder_path, sf))]
        
        for subfolder in subfolders:
            subfolder_path = os.path.join(folder_path, subfolder)

            # Get all images in the subfolder
            images = [img for img in os.listdir(subfolder_path) if os.path.isfile(os.path.join(subfolder_path, img))]

            # Write each image with its path and label to the output file
            for img in images:
                image_path = os.path.join(subfolder_path, img)
                # Write to file in the format: path/to/image the_image_label
                f.write(f"{image_path}\t{label}\n")

print(f"Labels file has been successfully written to {output_file}")