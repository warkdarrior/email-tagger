import unittest
from email.message import EmailMessage
from src.feature_extractor import extract_features

class TestFeatureExtractor(unittest.TestCase):
    def test_basic_text_email(self):
        msg = EmailMessage()
        msg.set_content("Hello world")
        msg['Subject'] = "Test Email"
        
        raw = msg.as_bytes()
        text = extract_features(raw)
        self.assertIn("Test Email", text)
        self.assertIn("Hello world", text)

    def test_multipart_email(self):
        msg = EmailMessage()
        msg.set_content("Plain text body")
        msg.add_alternative("<p>HTML Body</p>", subtype='html')
        msg['Subject'] = "Multipart"
        
        raw = msg.as_bytes()
        text = extract_features(raw)
        # Should contain subject
        self.assertIn("Multipart", text)
        # Should contain html stripped content or plain text depending on extraction logic order
        # My implementation walks parts.
        self.assertTrue("Plain text body" in text or "HTML Body" in text)

    def test_empty_email(self):
        text = extract_features(b"")
        self.assertEqual(text, "")

if __name__ == '__main__':
    unittest.main()
