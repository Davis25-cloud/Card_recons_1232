import tkinter as tk
from tkinter import filedialog
from tkinter import ttk
import pandas as pd
import os
import threading


def validate_file(filepath, allowed_extensions=('.xlsx', '.txt', '.csv')):
    _, ext = os.path.splitext(filepath)
    ext = ext.lower()
    if ext not in allowed_extensions:
        return False, f"Invalid file extension: {ext}", None
    try:
        if ext == '.csv':
            pd.read_csv(filepath, nrows=5)
            return True, "Valid CSV", "csv"
        elif ext == '.xlsx':
            pd.read_excel(filepath, nrows=5)
            return True, "Valid Excel", "excel"
        elif ext == '.txt':
            pd.read_csv(filepath, delimiter="\t", nrows=5)
            return True, "Valid Text", "text"
        else:
            return False, "Unsupported file type", None
    except Exception as e:
        return False, str(e), None


def process_file(filepath, file_type):
    try:
        if file_type == "csv":
            df = pd.read_csv(filepath)
        elif file_type == "excel":
            df = pd.read_excel(filepath)
        elif file_type == "text":
            df = pd.read_csv(filepath, delimiter="\t")
        else:
            return False
        # Simulate processing (can be replaced with custom logic)
        print(f"Processed file: {os.path.basename(filepath)} | Rows: {len(df)}")
        return True
    except Exception as e:
        print(f"Processing error for {filepath}: {e}")
        return False


class FileUploadApp:
    def __init__(self, master):
        self.master = master
        master.title("File Upload and Processing")

        self.file_display_map = {}  # Add this to __init__

        self.uploaded_files = []
        self.processing = False

        # File Upload Section
        self.upload_label = ttk.Label(master, text="Upload Files:")
        self.upload_label.pack(pady=5)

        self.upload_button = ttk.Button(master, text="Choose Files", command=self.choose_files)
        self.upload_button.pack(pady=5)

        self.file_list = tk.Listbox(master, selectmode="multiple", width=60)
        self.file_list.pack(pady=5)

        self.remove_button = ttk.Button(master, text="Remove Selected", command=self.remove_files, state=tk.DISABLED)
        self.remove_button.pack(pady=5)

        # Processing Section
        self.process_button = ttk.Button(master, text="Process Files", command=self.process_files, state=tk.DISABLED)
        self.process_button.pack(pady=10)

        self.progress_label = ttk.Label(master, text="")
        self.progress_label.pack(pady=5)

        self.status_label = ttk.Label(master, text="Status: Waiting")
        self.status_label.pack(pady=5)

    def choose_files(self):
        filenames = filedialog.askopenfilenames(
            filetypes=[("Excel Files", "*.xlsx"), ("Text Files", "*.txt"), ("CSV Files", "*.csv")]
        )
        for filename in filenames:
            self.add_file(filename)

    def add_file(self, filename):
        display_name = os.path.basename(filename)
        if filename not in self.uploaded_files:
            self.uploaded_files.append(filename)
            self.file_display_map[display_name] = filename
            self.file_list.insert(tk.END, display_name)
            self.update_buttons()
            self.update_file_view()

    def remove_files(self):
        selected_indices = self.file_list.curselection()
        for index in reversed(selected_indices):
            display_name = self.file_list.get(index)
            full_path = self.file_display_map.pop(display_name)
            self.uploaded_files.remove(full_path)
            self.file_list.delete(index)
        self.update_buttons()
        self.update_file_view()


    def update_buttons(self):
        if self.uploaded_files:
            self.remove_button.config(state=tk.NORMAL)
            self.process_button.config(state=tk.NORMAL)
        else:
            self.remove_button.config(state=tk.DISABLED)
            self.process_button.config(state=tk.DISABLED)

    def update_file_view(self):
        # Placeholder for preview functionality
        pass

    def process_files(self):
        if self.processing:
            return

        self.processing = True
        self.process_button.config(state=tk.DISABLED)
        self.progress_label.config(text="Processing files...")
        self.status_label.config(text="Status: Processing...")

        def process_files_thread():
            for display_name in self.file_display_map:
                filename = self.file_display_map[display_name]

                is_valid, msg, file_type = validate_file(filename)
                if is_valid:
                    if process_file(filename, file_type):
                        self.progress_label.config(text=f"Processed: {filename}")
                    else:
                        self.progress_label.config(text=f"Error processing: {filename}")
                else:
                    self.progress_label.config(text=f"Validation failed: {filename} - {msg}")
            self.processing = False
            self.process_button.config(state=tk.NORMAL)
            self.progress_label.config(text="Processing complete.")
            self.status_label.config(text="Status: Done")

        thread = threading.Thread(target=process_files_thread)
        thread.start()


if __name__ == "__main__":
    root = tk.Tk()
    app = FileUploadApp(root)
    root.mainloop()
