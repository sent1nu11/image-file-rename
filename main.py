import os
from PIL import Image
from PIL.ExifTags import TAGS
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def get_date_taken(path):
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

class RenameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Renamer (EXIF DateTimeOriginal)")
        self.root.geometry("700x500")
        
        # UI Elements
        self.frame = ttk.Frame(root, padding=10)
        self.frame.pack(fill="both", expand=True)

        self.select_button = ttk.Button(self.frame, text="Select Folder", command=self.select_folder)
        self.select_button.pack(pady=5)

        self.tree = ttk.Treeview(self.frame, columns=("Original", "New"), show="headings")
        self.tree.heading("Original", text="Original Filename")
        self.tree.heading("New", text="New Filename")
        self.tree.pack(fill="both", expand=True, pady=10)

        self.progress = ttk.Progressbar(self.frame, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=5)

        self.rename_button = ttk.Button(self.frame, text="Rename Files", command=self.rename_files)
        self.rename_button.pack(pady=5)

        self.folder_path = ""
        self.rename_plan = []

    def select_folder(self):
        self.folder_path = filedialog.askdirectory(title="Select Photo Folder")
        self.tree.delete(*self.tree.get_children())
        self.rename_plan.clear()

        if not self.folder_path:
            return

        # Gather files and proposed new names
        for filename in sorted(os.listdir(self.folder_path)):
            if filename.lower().endswith(('.jpg', '.jpeg')):
                full_path = os.path.join(self.folder_path, filename)
                date_taken = get_date_taken(full_path)
                if date_taken:
                    date_str = date_taken.strftime("%Y-%m-%d-%H%M%S")
                    ext = os.path.splitext(filename)[1].lower()
                    new_name = f"{date_str}{ext}"
                    new_path = os.path.join(self.folder_path, new_name)
                    self.rename_plan.append((full_path, filename, new_name, new_path))

        # Display in tree view
        for _, original, new_name, _ in self.rename_plan:
            self.tree.insert("", "end", values=(original, new_name))

    def rename_files(self):
        if not self.rename_plan:
            messagebox.showwarning("No Files", "No photos to rename.")
            return

        confirm = messagebox.askyesno("Confirm Rename", f"Rename {len(self.rename_plan)} files?")
        if not confirm:
            return

        self.progress["value"] = 0
        self.progress["maximum"] = len(self.rename_plan)

        renamed_count = 0
        for i, (full_path, original, new_name, new_path) in enumerate(self.rename_plan):
            if os.path.abspath(full_path) != os.path.abspath(new_path):
                if not os.path.exists(new_path):
                    try:
                        os.rename(full_path, new_path)
                        renamed_count += 1
                    except Exception as e:
                        print(f"Failed to rename {original}: {e}")
                else:
                    print(f"Skipped (conflict): {original}")
            self.progress["value"] = i + 1
            self.root.update_idletasks()

        messagebox.showinfo("Done", f"Renamed {renamed_count} file(s).")
        self.rename_plan.clear()
        self.tree.delete(*self.tree.get_children())
        self.progress["value"] = 0

if __name__ == "__main__":
    root = tk.Tk()
    app = RenameApp(root)
    root.mainloop()




