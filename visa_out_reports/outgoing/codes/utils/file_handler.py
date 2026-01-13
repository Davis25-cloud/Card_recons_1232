import os
import pandas as pd
import pdfplumber
import shutil
from txn_parser import parse_txt_file_to_csv_and_db

def process_files(config, logger, progress=None):
    input_dir = config['FILES']['input_dir']
    files = [f for f in os.listdir(input_dir) if f.endswith(".txt") or f.endswith(".xlsx")]

    if progress is not None:
        progress["total"] = len(files)
        progress["current"] = 0
        progress["status"] = "Running"

    for i, file in enumerate(files):
        try:
            logger.info(f"Processing file: {file}")
            file_path = os.path.join(input_dir, file)

            # Add your parsing logic here for each file type
            if file.lower().endswith(".txt"):
                parse_txt_file_to_csv_and_db(file_path, config, logger)
                pass
            elif file.lower().endswith(".xlsx"):
                # call your loe parser
                pass

            # Update progress
            if progress is not None:
                progress["current"] = i + 1

        except Exception as e:
            logger.error(f"Error processing {file}: {e}")

    if progress is not None:
        progress["status"] = "Done"


