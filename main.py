import os
import exifread
from datetime import datetime
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def get_date_taken(path):
    """Extract EXIF DateTimeOriginal using exifread (supports .nef, .jpg, .jpeg)."""
    try:
        with open(path, 'rb') as f:
            tags = exifread.process_file(f, stop_tag="EXIF DateTimeOriginal", details=False)
            date_str = tags.get("EXIF DateTimeOriginal")
            if date_str:
                return datetime.strptime(str(date_str), "%Y:%m:%d %H:%M:%S")
    except Exception as e:
        print(f"Error reading EXIF from {path}: {e}")
    return None

class RenameApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Photo Renamer (EXIF DateTimeOriginal)")
        self.root.geometry("750x600")

        self.frame = ttk.Frame(root, padding=10)
        self.frame.pack(fill="both", expand=True)

        # Folder selection
        self.select_button = ttk.Button(self.frame, text="Select Folder", command=self.select_folder)
        self.select_button.pack(pady=5)

        # Display selected folder path
        self.folder_label = ttk.Label(self.frame, text="", foreground="blue", wraplength=700, anchor="w", justify="left")
        self.folder_label.pack(fill="x", padx=5, pady=2)

        # Description of supported file types
        self.supported_label = ttk.Label(
            self.frame,
            text="Only .jpg, .jpeg, and .nef files will be renamed based on EXIF DateTimeOriginal.",
            foreground="gray",
            wraplength=700,
            justify="left"
        )
        self.supported_label.pack(fill="x", padx=5, pady=(0, 5))

        # Topic entry
        topic_frame = ttk.Frame(self.frame)
        topic_frame.pack(pady=5)
        ttk.Label(topic_frame, text="Optional Topic:").pack(side="left")
        self.topic_entry = ttk.Entry(topic_frame, width=40)
        self.topic_entry.pack(side="left", padx=5)

        # Preview table
        self.tree = ttk.Treeview(self.frame, columns=("Original", "New"), show="headings")
        self.tree.heading("Original", text="Original Filename")
        self.tree.heading("New", text="New Filename")
        self.tree.column("Original", width=300)
        self.tree.column("New", width=350)
        self.tree.pack(fill="both", expand=True, pady=10)

        # Progress bar
        self.progress = ttk.Progressbar(self.frame, orient="horizontal", mode="determinate")
        self.progress.pack(fill="x", pady=5)

        # Rename button
        self.rename_button = ttk.Button(self.frame, text="Rename Files", command=self.rename_files)
        self.rename_button.pack(pady=5)

        # Internal state
        self.folder_path = ""
        self.rename_plan = []

    def select_folder(self):
        self.folder_path = filedialog.askdirectory(title="Select Photo Folder")
        self.tree.delete(*self.tree.get_children())
        self.rename_plan.clear()
        self.folder_label.config(text=self.folder_path if self.folder_path else "")

        if not self.folder_path:
            return

        topic = self.topic_entry.get().strip().replace(" ", "_")

        for filename in sorted(os.listdir(self.folder_path)):
            if filename.lower().endswith(('.jpg', '.jpeg', '.nef')):
                full_path = os.path.join(self.folder_path, filename)
                date_taken = get_date_taken(full_path)
                if date_taken:
                    date_str = date_taken.strftime("%Y-%m-%d-%H%M%S")
                    ext = os.path.splitext(filename)[1].lower()
                    new_name = f"{date_str}{'_' + topic if topic else ''}{ext}"
                    new_path = os.path.join(self.folder_path, new_name)
                    self.rename_plan.append((full_path, filename, new_name, new_path))

        for _, original_filename, new_name, _ in self.rename_plan:
            self.tree.insert("", "end", values=(original_filename, new_name))

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
        self.folder_label.config(text="")

if __name__ == "__main__":
    root = tk.Tk()
    app = RenameApp(root)
    root.mainloop()
