import os
import joblib
import logging
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.tree import DecisionTreeClassifier
from sklearn.pipeline import Pipeline
from .feature_extractor import extract_features

logger = logging.getLogger(__name__)

class TaggingModel:
    def __init__(self, model_path="model.pkl"):
        self.model_path = model_path
        self.pipeline = Pipeline([
            ('tfidf', TfidfVectorizer(stop_words='english', max_features=5000, lowercase=True)),
            ('clf', DecisionTreeClassifier())
        ])
        self.is_trained = False

    def train(self, training_data):
        """
        Trains the model.
        training_data: list of tuples (raw_email_bytes, tag_label)
        """
        logger.info(f"Starting training with {len(training_data)} samples.")
        
        X_raw = [item[0] for item in training_data]
        y = [item[1] for item in training_data]
        
        # Preprocess features
        # Note: We can do feature extraction here or inside the pipeline if we wrap feature_extractor.
        # But Tfidf expects strings. So we must convert raw bytes to strings first.
        
        X_text = []
        for raw in X_raw:
            X_text.append(extract_features(raw))
            
        try:
            self.pipeline.fit(X_text, y)
            self.is_trained = True
            logger.info("Training completed.")
            self.save()
        except Exception as e:
            logger.error(f"Error during training: {e}")
            raise

    def predict(self, raw_email_bytes):
        """
        Predicts tag for a single email.
        """
        if not self.is_trained:
            logger.warning("Model is not trained.")
            return None
            
        text = extract_features(raw_email_bytes)
        
        try:
            # predict returns an array
            prediction = self.pipeline.predict([text])[0]
            # optional: predict_proba to threshold confidence?
            # For decision tree, proba is usually 0 or 1 unless pruned/leaves have user samples.
            return prediction
        except Exception as e:
            logger.error(f"Error predicting: {e}")
            return None

    def save(self):
        try:
            joblib.dump(self.pipeline, self.model_path)
            logger.info(f"Model saved to {self.model_path}")
        except Exception as e:
            logger.error(f"Error saving model: {e}")

    def load(self):
        if os.path.exists(self.model_path):
            try:
                self.pipeline = joblib.load(self.model_path)
                self.is_trained = True
                logger.info(f"Model loaded from {self.model_path}")
                return True
            except Exception as e:
                logger.error(f"Error loading model: {e}")
                return False
        return False
