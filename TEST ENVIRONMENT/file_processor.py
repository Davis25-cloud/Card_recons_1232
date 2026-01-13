import time
import pandas as pd
import tkinter as tk
from tkinter import filedialog, ttk

valid_files = []  # Store selected files globally

def select_files(file_listbox, status_label):
    """Allow users to select multiple files for upload."""
    file_types = [("Text files", "*.txt"), ("Excel files", "*.xlsx"), ("All files", "*.*")]
    selected_files = filedialog.askopenfilenames(title="Select files to upload", filetypes=file_types)

    if not selected_files:
        status_label.config(text="No file selected.")
        return
    
    global valid_files
    valid_files = [f for f in selected_files if f.endswith(('.txt', '.xlsx'))]

    if not valid_files:
        status_label.config(text="No valid files selected.")
        return

    # Display selected files in the listbox
    file_listbox.delete(0, tk.END)
    for file in valid_files:
        file_listbox.insert(tk.END, file)

    status_label.config(text="Files ready for upload.")

def upload_files(progress_bar, progress_label, status_label, root):
    """Process selected files with a progress bar and show a new window after completion."""
    if not valid_files:
        status_label.config(text="No files selected for upload.")
        return

    total_files = len(valid_files)
    progress_bar["maximum"] = total_files
    progress_bar["value"] = 0

    uploaded_files = []  # Store successfully uploaded files

    for index, file in enumerate(valid_files, start=1):
        time.sleep(1)  # Simulate slow processing
        
        try:
            if file.endswith(".xlsx"):
                df = pd.read_excel(file, sheet_name=1)  # Read from second sheet
                if not df.empty:
                    first_column_name = df.columns[0]
                    file_date = df[first_column_name].iloc[0]
                    print(f"Extracted date from {file}: {file_date}")
                else:
                    print(f"File {file} is empty.")
            uploaded_files.append(file)
        except Exception as e:
            print(f"Error reading {file}: {e}")
            continue
        
        # Update progress bar
        progress_bar["value"] = index
        progress_label.config(text=f"Processing {index}/{total_files} files...")
        root.update_idletasks()

    progress_label.config(text="Upload Complete!")
    status_label.config(text="All files processed successfully.")

    # Show new window with uploaded files
    show_uploaded_files(uploaded_files, root)
upload_files()
def show_uploaded_files(uploaded_files, root):
    """Display a new window showing all uploaded files."""
    new_window = tk.Toplevel(root)
    new_window.title("Uploaded Files")

    tk.Label(new_window, text="Files Uploaded Successfully:", font=("Arial", 12, "bold")).pack(pady=5)

    uploaded_listbox = tk.Listbox(new_window, width=80, height=10)
    uploaded_listbox.pack(padx=10, pady=5)

    for file in uploaded_files:
        uploaded_listbox.insert(tk.END, file)

    close_button = tk.Button(new_window, text="Close", command=new_window.destroy)
    close_button.pack(pady=5)
