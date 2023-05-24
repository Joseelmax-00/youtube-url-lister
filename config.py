from dotenv import load_dotenv
import os

# Load variables from .env
load_dotenv('config.env')

# Get API key
YOUTUBE_API_KEY = os.getenv('YOUTUBE_API_KEY')
