from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time
import os
import configparser
from logger import setup_logger
from file_handler import process_file

class NewFileHandler(FileSystemEventHandler):
    def __init__(self, config):
        self.config = config
        self.logger = setup_logger()

    def on_created(self, event):
        if not event.is_directory and event.src_path.endswith((".csv", ".xlsx", ".pdf")):
            filename = os.path.basename(event.src_path)
            self.logger.info(f"New file detected: {filename}")
            process_file(event.src_path, self.config, self.logger)

def start_watcher():
    config = configparser.ConfigParser()
    config.read('config.ini')
    input_dir = config['FILES']['input_dir']
    logger = setup_logger()
    
    event_handler = NewFileHandler(config)
    observer = Observer()
    observer.schedule(event_handler, path=input_dir, recursive=False)
    observer.start()
    logger.info(f"Watching directory: {input_dir}")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        logger.info("File watcher stopped.")
    observer.join()
