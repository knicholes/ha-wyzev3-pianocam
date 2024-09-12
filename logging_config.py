# logging_config.py
import logging

def setup_logging():
    logging.basicConfig(
        level=logging.INFO,  # Change to DEBUG for more detailed logs
        format='%(asctime)s - %(levelname)s - %(name)s - %(message)s'
    )
