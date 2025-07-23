import os
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime

def get_date_taken(path):
    """Extract the date the photo was taken from EXIF data."""
    try:
        image = Image.open(path)
        exif_data = image._getexif()
        if exif_data:
            for tag, value in exif_data.items():
                if TAGS.get(tag) == "DateTimeOriginal":
                    return datetime.strptime(value, "%Y:%m:%d %H:%M:%S")
    except Exception as e:
        print(f"Error reading EXIF from {path}: {e}")
    return None

def rename_photos_by_datetime(folder_path):
    images = []

    for filename in os.listdir(folder_path):
        if filename.lower().endswith(('.jpg', '.jpeg')):
            full_path = os.path.join(folder_path, filename)
            date_taken = get_date_taken(full_path)
            if date_taken:
                images.append((date_taken, full_path, filename))

    # Sort by date taken
    images.sort(key=lambda x: x[0])

    for date_taken, full_path, original_filename in images:
        # Format: YYYY-MM-DD-HHMMSS
        date_str = date_taken.strftime("%Y-%m-%d-%H%M%S")
        ext = os.path.splitext(original_filename)[1].lower()
        new_name = f"{date_str}{ext}"
        new_path = os.path.join(folder_path, new_name)

        if os.path.abspath(full_path) != os.path.abspath(new_path):
            if not os.path.exists(new_path):
                os.rename(full_path, new_path)
                print(f"Renamed: {original_filename} → {new_name}")
            else:
                print(f"Conflict: {new_name} already exists. Skipping.")
        else:
            print(f"Skipping: {original_filename} (already named correctly)")


# ✅ Set your photo folder path here
photo_folder = r"C:\photos"  # Change this!
rename_photos_by_datetime(photo_folder)

