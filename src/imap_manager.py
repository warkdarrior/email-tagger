import logging
import time
from imapclient import IMAPClient
from .config import config

logger = logging.getLogger(__name__)

class ImapManager:
    def __init__(self):
        self.server = None

    def connect(self):
        """Connects to the IMAP server and logs in."""
        try:
            logger.info(f"Connecting to IMAP server: {config.IMAP_SERVER}")
            self.server = IMAPClient(config.IMAP_SERVER, use_uid=True, ssl=True)
            self.server.login(config.IMAP_USER, config.IMAP_PASSWORD)
            logger.info("Successfully connected to IMAP server.")
        except Exception as e:
            logger.error(f"Failed to connect to IMAP server: {e}")
            raise

    def disconnect(self):
        """Disconnects from the IMAP server."""
        if self.server:
            try:
                self.server.logout()
            except Exception as e:
                logger.error(f"Error disconnecting: {e}")
            finally:
                self.server = None

    def _ensure_connection(self):
        """Reconnects if the connection is lost."""
        if not self.server:
            self.connect()
        else:
            try:
                self.server.noop()
            except Exception:
                logger.warning("Connection lost. Reconnecting...")
                self.connect()

    def fetch_unseen_inbox(self):
        """Fetches unseen messages from the Inbox."""
        self._ensure_connection()
        try:
            self.server.select_folder(config.INBOX_FOLDER)
            # Fetch messages that do NOT have any of our known tags yet?
            # Or just fetch all UNSEEN? Let's stick to UNSEEN for now as per plan.
            messages = self.server.search(['UNSEEN'])
            if not messages:
                return {}
            
            # Fetch envelope and body structure/content
            response = self.server.fetch(messages, ['BODY.PEEK[]', 'INTERNALDATE', 'FLAGS'])
            return response
        except Exception as e:
            logger.error(f"Error fetching unseen inbox: {e}")
            return {}

    def add_tag(self, uid, tag):
        """Adds a keyword (tag) to a message."""
        self._ensure_connection()
        try:
            # Note: IMAP keywords must be valid atoms.
            logger.info(f"Tagging message {uid} with {tag}")
            self.server.add_flags(uid, [tag])
        except Exception as e:
            logger.error(f"Error adding tag {tag} to {uid}: {e}")

    def fetch_archive_tagged(self):
        """Fetches messages in Archive that have one of our known tags."""
        self._ensure_connection()
        try:
            self.server.select_folder(config.ARCHIVE_FOLDER)
            
            # Search for messages that have ANY of the keys in TAG_MAPPING
            # OR search for all messages and filter locally?
            # IMAP search for keywords: KEYWORD "mytag"
            # We can construct a search criteria ORing all tags
            
            if not config.TAG_MAPPING:
                return {}

            # Construct search criteria: (OR (KEYWORD "Tag1") (OR (KEYWORD "Tag2") ...))
            # imapclient supports a list of criteria.
            # But let's simplify: iterate over tags and search? Or fetch all and check flags?
            # Fetching all flags for Archive might be heavy if it's large.
            # Let's search for each tag. It might be slow if many tags.
            # Optimization: 'OR' criteria is better if supported.
            
            # For simplicity in this v1: Let's search for each known tag.
            found_messages = {} # uid -> tag
            
            for tag in config.TAG_MAPPING.keys():
                uids = self.server.search(['KEYWORD', tag])
                for uid in uids:
                     found_messages[uid] = tag
            
            return found_messages
            
        except Exception as e:
            logger.error(f"Error fetching archive tagged: {e}")
            return {}

    def move_message(self, uid, folder):
        """Moves a message to a specific folder."""
        self._ensure_connection()
        try:
            if not self.server.folder_exists(folder):
                # Optionally create folder?
                # logger.info(f"Creating folder {folder}")
                # self.server.create_folder(folder)
                pass

            logger.info(f"Moving message {uid} to {folder}")
            self.server.move([uid], folder)
        except Exception as e:
            logger.error(f"Error moving message {uid} to {folder}: {e}")

    def get_training_data(self):
        """
        Iterates over folders defined in TAG_MAPPING values.
        Returns a list of (email_content, tag_label).
        """
        self._ensure_connection()
        training_data = [] # List of (content, label)
        
        # Invert mapping to find Tag for a Folder
        # TAG_MAPPING: Tag -> Folder.
        # We need Folder -> Tag.
        folder_to_tag = {v: k for k, v in config.TAG_MAPPING.items()}
        
        try:
            for folder, tag in folder_to_tag.items():
                if not self.server.folder_exists(folder):
                    logger.warning(f"Training folder {folder} does not exist. Skipping.")
                    continue
                
                self.server.select_folder(folder)
                # Fetch all messages? Or limit to recent?
                # For training, more is better, but speed matters.
                # Let's limit to last 1000? or all. 
                # Let's try to fetch all, assuming user doesn't have millions.
                # Or maybe user 'seen' messages?
                uids = self.server.search(['ALL'])
                
                # Batch fetch to avoid memory issues?
                # For now, fetch all at once.
                if not uids:
                    continue
                    
                response = self.server.fetch(uids, ['BODY.PEEK[]'])
                
                for uid, data in response.items():
                    content = data.get(b'BODY[]') or data.get(b'BODY.PEEK[]')
                    if content:
                        # Decode bytes to string handled by feature extractor?
                        # Or keep as bytes? Feature extractor will likely need string or handling bytes.
                        # Let's keep as bytes here, pass to feature extractor later.
                        training_data.append((content, tag))
                        
            return training_data

        except Exception as e:
            logger.error(f"Error getting training data: {e}")
            return []
