import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re

from config import YOUTUBE_API_KEY

def get_video_urls_from_channel(channel_input, api_key=YOUTUBE_API_KEY):
    youtube = build('youtube', 'v3', developerKey=api_key)

    # If the input is a URL, extract the channel ID
    match = re.search('channel/([a-zA-Z0-9_-]+)', channel_input)
    if match:
        channel_id = match.group(1)
    else:
        channel_id = channel_input

    try:
        request = youtube.search().list(
            part='snippet',
            channelId=channel_id,
            maxResults=50,  # This can be increased up to 50 per request
            type='video'
        )
        response = request.execute()

        video_urls = []
        for item in response['items']:
            video_id = item['id']['videoId']
            video_url = f'https://www.youtube.com/watch?v={video_id}'
            video_urls.append(video_url)

        return video_urls

    except HttpError as e:
        print(f'An HTTP error {e.resp.status} occurred:\n{e.content}')
        return []


channel_url = st.text_input('Enter Youtube channel URL')
if channel_url:
    video_list = get_video_urls_from_channel(channel_url)  # Function to implement
    st.table(video_list)

