import time
import logging
from .config import config
from .imap_manager import ImapManager
from .model import TaggingModel

logger = logging.getLogger(__name__)

class EmailTaggerService:
    def __init__(self):
        self.imap = ImapManager()
        self.model = TaggingModel()
        self.polling_interval = config.POLL_INTERVAL

    def initialize(self):
        """Initial setup: Connect to IMAP, Load Model."""
        try:
            self.imap.connect()
            if not self.model.load():
                logger.info("No trained model found. Attempting initial training...")
                self.train_model()
        except Exception as e:
            logger.error(f"Initialization failed: {e}")
            raise

    def train_model(self):
        """Fetches training data and trains the model."""
        logger.info("Gathering training data from folders...")
        training_data = self.imap.get_training_data()
        
        if not training_data:
            logger.warning("No training data found. Skipping training.")
            return

        logger.info(f"Training model with {len(training_data)} samples...")
        self.model.train(training_data)

    def process_inbox(self):
        """Fetches unseen messages, predicts tags, and applies them."""
        logger.debug("Checking Inbox for new messages...")
        messages = self.imap.fetch_unseen_inbox()
        
        if not messages:
            return

        logger.info(f"Found {len(messages)} new messages in Inbox.")
        
        for uid, data in messages.items():
            content = data.get(b'BODY[]') or data.get(b'BODY.PEEK[]')
            if not content:
                continue
                
            prediction = self.model.predict(content)
            if prediction:
                logger.info(f"Predicted tag '{prediction}' for message {uid}")
                self.imap.add_tag(uid, prediction)
            else:
                logger.info(f"No prediction for message {uid}")

    def process_archive(self):
        """Checks Archive for tagged messages and moves them."""
        logger.debug("Checking Archive for tagged messages...")
        tagged_messages = self.imap.fetch_archive_tagged()
        
        if not tagged_messages:
            return

        logger.info(f"Found {len(tagged_messages)} tagged messages in Archive.")
        
        # Tag Mapping: Tag -> Folder
        for uid, tag in tagged_messages.items():
            target_folder = config.TAG_MAPPING.get(tag)
            if target_folder:
                self.imap.move_message(uid, target_folder)
            else:
                logger.warning(f"No folder mapping found for tag '{tag}'")

    def run(self):
        """Main service loop."""
        self.initialize()
        
        logger.info(f"Service running. Polling every {self.polling_interval} seconds.")
        
        try:
            while True:
                # 1. Prediction Loop
                # Only predict if model is trained
                if self.model.is_trained:
                    self.process_inbox()
                else:
                    logger.warning("Model not trained. Skipping Inbox processing.")

                # 2. Archiving Loop
                self.process_archive()
                
                # 3. Retraining Check? (Optional, maybe trigger periodically or manually)
                
                time.sleep(self.polling_interval)
                
        except KeyboardInterrupt:
            logger.info("Stopping service...")
        except Exception as e:
            logger.error(f"Service crashed: {e}")
        finally:
            self.imap.disconnect()
