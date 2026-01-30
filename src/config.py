import os
import json
import logging

logger = logging.getLogger(__name__)

class Config:
    def __init__(self):
        # Default values
        self.IMAP_SERVER = os.environ.get("IMAP_SERVER", "")
        self.IMAP_USER = os.environ.get("IMAP_USER", "")
        self.IMAP_PASSWORD = os.environ.get("IMAP_PASSWORD", "")
        self.INBOX_FOLDER = os.environ.get("INBOX_FOLDER", "INBOX")
        self.ARCHIVE_FOLDER = os.environ.get("ARCHIVE_FOLDER", "Archive")
        self.POLL_INTERVAL = int(os.environ.get("POLL_INTERVAL", 60))
        self.TAG_MAPPING = {}

    def load_from_file(self, config_path="config.json"):
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                data = json.load(f)
                self.IMAP_SERVER = data.get("IMAP_SERVER", self.IMAP_SERVER)
                self.IMAP_USER = data.get("IMAP_USER", self.IMAP_USER)
                self.IMAP_PASSWORD = data.get("IMAP_PASSWORD", self.IMAP_PASSWORD)
                self.INBOX_FOLDER = data.get("INBOX_FOLDER", self.INBOX_FOLDER)
                self.ARCHIVE_FOLDER = data.get("ARCHIVE_FOLDER", self.ARCHIVE_FOLDER)
                self.POLL_INTERVAL = data.get("POLL_INTERVAL", self.POLL_INTERVAL)
                self.TAG_MAPPING = data.get("TAG_MAPPING", self.TAG_MAPPING) 
        else:
            logger.warning(f"Config file {config_path} not found. Using defaults/env vars.")

# Global config instance
config = Config()
