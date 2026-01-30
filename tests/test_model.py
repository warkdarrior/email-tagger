import unittest
import os
import shutil
from src.model import TaggingModel

class TestTaggingModel(unittest.TestCase):
    def setUp(self):
        self.model_path = "test_model.pkl"
        self.model = TaggingModel(model_path=self.model_path)

    def tearDown(self):
        if os.path.exists(self.model_path):
            os.remove(self.model_path)

    def test_train_and_predict(self):
        # Mock training data: (raw_bytes, label)
        # We need to simulate raw bytes that extract_features can handle.
        # Just use strings for now inside extract_features wrapper if valid?
        # extract_features takes bytes or string.
        
        train_data = [
            (b"Subject: Meeting\n\nLet's reset discussing the project.", "Work"),
            (b"Subject: Party\n\nCome to the BBQ this weekend.", "Personal"),
            (b"Subject: Report\n\nHere is the Q3 financial report.", "Work"),
            (b"Subject: Movie\n\nLet's go see a movie.", "Personal")
        ]
        
        self.model.train(train_data)
        self.assertTrue(self.model.is_trained)
        self.assertTrue(os.path.exists(self.model_path))
        
        # Test Prediction
        pred_work = self.model.predict(b"Subject: Sync\n\nProject sync meeting.")
        self.assertEqual(pred_work, "Work")
        
        pred_personal = self.model.predict(b"Subject: Fun\n\nWeekend plans?")
        self.assertEqual(pred_personal, "Personal")

    def test_load_model(self):
        # Train and save
        self.test_train_and_predict()
        
        # Create new instance and load
        new_model = TaggingModel(model_path=self.model_path)
        loaded = new_model.load()
        self.assertTrue(loaded)
        self.assertTrue(new_model.is_trained)
        
        pred = new_model.predict(b"Subject: Sync\n\nProject sync meeting.")
        self.assertEqual(pred, "Work")

if __name__ == '__main__':
    unittest.main()
