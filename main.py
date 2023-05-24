import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
import requests
from bs4 import BeautifulSoup
import json

from config import YOUTUBE_API_KEY

YOUTUBE_API_KEY = st.secrets["YOUTUBE_API_KEY"]

def get_video_urls_from_channel(channel_input, api_key=YOUTUBE_API_KEY):
    """
    Fetches all the video URLs from a given YouTube channel.

    Parameters:
    - channel_input: The URL or ID of a YouTube channel.
    - api_key: The API key for accessing the YouTube Data API v3. If not provided, it defaults to the YOUTUBE_API_KEY environment variable.

    Returns:
    - :(list, str/None) A tuple containing -a list of video URLs and -an error string. If no error occurred, the error string is None.

    Errors:
    - If the channel_input is not a valid YouTube channel URL or ID, an error string is returned.
    - If an HTTP error occurs when accessing the YouTube Data API, an error string is returned.
    """
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    if channel_input.startswith('@'):
        channel_input = 'https://www.youtube.com/' + channel_input
    
    match = re.match(r'(?:https?://)?(?:www\.)?youtube\.com/(?:channel/|@)?([^/]+)/?', channel_input)
    if not match:
        return None, 'Invalid YouTube channel URL or ID'

    channel_id_or_username = match.group(1)
    
    if channel_id_or_username.startswith('UC'):  # It's a channel ID
        channel_id = channel_id_or_username
    else:  # It's a username, fetch the channel ID via web scraping
        response = requests.get(channel_input)
        soup = BeautifulSoup(response.text, 'html.parser')
        canonical_link = soup.find('link', {'rel': 'canonical'})
        if canonical_link:
            channel_id = canonical_link['href'].split('/')[-1]
        else:
            return None, "Could not extract channel ID. It's possible you entered an ID that doesn't exist. If this is not the case it's likely caused by an update on Youtube's part."

    video_urls = []
    page_token = None
    while True:
        try:
            request = youtube.search().list(
                part='snippet',
                channelId=channel_id,
                maxResults=50,
                type='video',
                pageToken=page_token
            )
            response = request.execute()

            for item in response['items']:
                video_id = item['id']['videoId']
                video_url = f'https://www.youtube.com/watch?v={video_id}'
                video_urls.append(video_url)

            page_token = response.get('nextPageToken')
            if not page_token:  # No more pages
                break

        except HttpError as e:
            error_content = json.loads(e.content)
            error_message = error_content.get('error', {}).get('message', '')
            if e.resp.status == 403:
                return None, "Request cannot be completed. Daily quota exceeded. Please try again later."
            else:
                return None, f"An HTTP error {e.resp.status} occurred: {error_message}. Please try again later."

    return video_urls, None  # No error


channel_input = st.text_input('Enter Youtube channel URL or ID').strip()
if channel_input:
    video_list, error = get_video_urls_from_channel(channel_input)
    if error:
        st.error(error)
    else:
        st.table(video_list)

