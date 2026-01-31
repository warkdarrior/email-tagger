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
from src.imap_manager import ImapManager
from src.config import config
import argparse
import logging
import sys
import getpass

logger = logging.getLogger(__name__)

def main():
    parser = argparse.ArgumentParser(description="Email Tagger Service")
    parser.add_argument('--test-connection', action='store_true', help="Test IMAP connectivity and exit")
    parser.add_argument('--config', default='config.json', help="Path to configuration file")
    args = parser.parse_args()

    # Load configuration
    config.load_from_file(args.config)
    
    if not config.IMAP_PASSWORD:
        print("IMAP Password not found in configuration.")
        config.IMAP_PASSWORD = getpass.getpass("Enter IMAP Password: ")

    if args.test_connection:
        logger.info("Testing IMAP connectivity...")
        try:
            imap = ImapManager()
            imap.connect()
            logger.info("Connection test PASSED.")
            imap.disconnect()
            sys.exit(0)
        except Exception as e:
            error_msg = str(e)
            if isinstance(e, bytes):
                error_msg = e.decode('utf-8', errors='replace')
            elif hasattr(e, 'args') and e.args and isinstance(e.args[0], bytes):
                error_msg = e.args[0].decode('utf-8', errors='replace')
            
            logger.error(f"Connection test FAILED: {error_msg}")
            sys.exit(1)

    logger.info("Starting Email Tagger Service...")
    
    service = EmailTaggerService()
    service.run()

if __name__ == "__main__":
    main()
