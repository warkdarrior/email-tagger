import email
from email.policy import default
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)

def extract_features(email_bytes):
    """
    Parses email bytes and returns a combined string of Subject and Body.
    """
    try:
        # Parse email bytes
        if isinstance(email_bytes, bytes):
            msg = email.message_from_bytes(email_bytes, policy=default)
        else:
            msg = email.message_from_string(email_bytes, policy=default)

        # Get Subject
        subject = msg.get("subject", "")

        # Get Body (Text/HTML)
        body = ""
        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                if "attachment" in content_disposition:
                    continue

                try:
                    payload = part.get_payload(decode=True)
                    if payload:
                        charset = part.get_content_charset() or 'utf-8'
                        decoded_payload = payload.decode(charset, errors='replace')
                        
                        if content_type == "text/plain":
                            body += decoded_payload + " "
                        elif content_type == "text/html":
                            # Strip HTML tags
                            soup = BeautifulSoup(decoded_payload, "html.parser")
                            body += soup.get_text(separator=" ") + " "
                except Exception as e:
                    logger.warning(f"Error parsing part: {e}")
        else:
            # Single part
            try:
                payload = msg.get_payload(decode=True)
                if payload:
                    charset = msg.get_content_charset() or 'utf-8'
                    decoded_payload = payload.decode(charset, errors='replace')
                    
                    if msg.get_content_type() == "text/html":
                        soup = BeautifulSoup(decoded_payload, "html.parser")
                        body += soup.get_text(separator=" ")
                    else:
                        body += decoded_payload
            except Exception as e:
                logger.warning(f"Error parsing body: {e}")

        # Combine Subject and Body
        # Adding Subject multiple times or giving it simple weight?
        # For now, just concatenate.
        combined_text = f"{subject} {body}"
        
        # Basic cleaning (newlines, extra spaces)
        combined_text = " ".join(combined_text.split())
        
        return combined_text
    
    except Exception as e:
        logger.error(f"Error extracting features: {e}")
        return ""
