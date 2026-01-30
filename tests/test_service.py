import unittest
from unittest.mock import MagicMock, patch
from src.service import EmailTaggerService
from src.config import config

class TestEmailTaggerService(unittest.TestCase):
    @patch('src.service.ImapManager')
    @patch('src.service.TaggingModel')
    def test_initialization_trains_if_needed(self, MockModel, MockImap):
        # Setup
        service = EmailTaggerService()
        service.model.load.return_value = False # Not trained
        service.imap.get_training_data.return_value = [("content", "Tag")]
        
        # Action
        service.initialize()
        
        # Assert
        service.imap.connect.assert_called_once()
        service.model.train.assert_called_once()

    @patch('src.service.ImapManager')
    @patch('src.service.TaggingModel')
    def test_process_inbox(self, MockModel, MockImap):
        service = EmailTaggerService()
        service.model.predict.return_value = "Work"
        # Mock fetch_unseen_inbox returning dict of {uid: {data...}}
        # data structure: {b'BODY[]': b'content'}
        service.imap.fetch_unseen_inbox.return_value = {
            101: {b'BODY[]': b"Meeting about project"}
        }
        
        service.process_inbox()
        
        service.model.predict.assert_called_with(b"Meeting about project")
        service.imap.add_tag.assert_called_with(101, "Work")

    @patch('src.service.ImapManager')
    @patch('src.service.TaggingModel')
    def test_process_archive(self, MockModel, MockImap):
        service = EmailTaggerService()
        
        # Setup Config Mapping
        config.TAG_MAPPING = {"Work": "WorkFolder", "Personal": "PersonalFolder"}
        
        # Mock archive tagged messages
        service.imap.fetch_archive_tagged.return_value = {
            201: "Work",
            202: "Personal",
            203: "UnknownTag" # Should handle gracefully
        }
        
        service.process_archive()
        
        # Assert moves
        service.imap.move_message.assert_any_call(201, "WorkFolder")
        service.imap.move_message.assert_any_call(202, "PersonalFolder")
        # Ensure 203 not moved to None or crashed
        # call_args_list is a list of calls.
        # We expect 2 valid calls.
        self.assertEqual(service.imap.move_message.call_count, 2)

if __name__ == '__main__':
    unittest.main()
