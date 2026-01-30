import sys
import time
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

from src.service import EmailTaggerService    
import time

def main():
    logger.info("Starting Email Tagger Service...")
    
    service = EmailTaggerService()
    service.run()

if __name__ == "__main__":
    main()
