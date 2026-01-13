## main.py
import configparser
import schedule
import time
import argparse
from utils.logger import setup_logger
from utils.file_handler import process_file
from utils.db_handler import init_db

# Setup
config = configparser.ConfigParser()
config.read('E:/Automation - Copy/Card_recon/visa_out_reports/outgoing/codes/config.ini')
print("Sections:", config.sections()) 
logger = setup_logger()

init_db(config, logger)

def job():
    logger.info("Automation job started.")
    process_file(config, logger)
    logger.info("Automation job completed.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--run-now", action="store_true", help="Run job immediately")
    args = parser.parse_args()

    if args.run_now:
        job()
    else:
        schedule.every().day.at("06:00").do(job)
        logger.info("Scheduler started.")
        while True:
            schedule.run_pending()
            time.sleep(60)

# job()  # Run the job immediately if --run-now is specified