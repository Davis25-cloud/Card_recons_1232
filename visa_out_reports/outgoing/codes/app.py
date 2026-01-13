import sys
import os

from flask import Flask, jsonify, render_template
from threading import Thread
import configparser
from utils.logger import setup_logger
from utils.file_handler import process_files

app = Flask(__name__)

# Progress tracking object
progress = {
    "total": 0,
    "current": 0,
    "status": "Idle"
}

# Load config
config = configparser.ConfigParser()
config.read('E:/Automation - Copy/Card_recon/visa_out_reports/outgoing/codes/config.ini')

# Logger
logger = setup_logger()

# Home route
@app.route("/")
def index():
    return render_template("dashboard.html")

# Start background processing job
@app.route("/start-processing")
def start_processing():
    def background_job():
        process_files(config, logger, progress)
    Thread(target=background_job).start()
    return jsonify({"status": "started"})

# Progress polling route
@app.route("/progress")
def get_progress():
    return jsonify(progress)

if __name__ == "__main__":
    app.run(debug=True)
