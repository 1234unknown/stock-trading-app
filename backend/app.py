from flask import Flask
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

app = Flask(__name__)

# A simple test route to make sure the server is running
@app.route('/api/test')
def test_endpoint():
    return {"message": "Hello from the Python backend!"}

# Example of how you'll access an API key
@app.route('/api/key-check')
def key_check():
    twelve_data_key = os.getenv('TWELVE_DATA_API_KEY')
    if twelve_data_key:
        # Return only a portion of the key for security checking
        return {"key_found": True, "key_sample": f"Starts with: {twelve_data_key[:4]}"}
    else:
        return {"key_found": False}
