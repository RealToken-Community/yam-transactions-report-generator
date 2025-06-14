import os
import logging
import logging.config
from logging.handlers import RotatingFileHandler


def setup_logging():

    os.makedirs("logs/api", exist_ok=True)

    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            RotatingFileHandler(
                'logs/api/app.log', 
                maxBytes=10*1024*1024,  # 10MB per file
                backupCount=5,          # Keep 5 backup files
                encoding='utf-8'
            )
        ]
    )

if __name__ == "__main__":
    # Test the configuration
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.debug("Debug message")
    logger.info("Info message")
    logger.warning("Warning message")
    logger.error("Error message")
    logger.critical("Critical message")