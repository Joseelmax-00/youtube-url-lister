import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
import requests
from bs4 import BeautifulSoup

from config import YOUTUBE_API_KEY


def get_video_urls_from_channel(channel_input, api_key=YOUTUBE_API_KEY):
    youtube = build('youtube', 'v3', developerKey=api_key)
    
    # Regular expression to match both channel ID and username formats
    match = re.match(r'(?:https?://)?(?:www\.)?youtube\.com/(?:channel/|@)?([^/]+)/?', channel_input)
    if not match:
        print('Invalid YouTube channel URL or ID')
        return []

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
            print('Could not extract channel ID')
            return []

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

channel_input = st.text_input('Enter Youtube channel URL or ID')
if channel_input:
    video_list = get_video_urls_from_channel(channel_input, YOUTUBE_API_KEY)
    st.table(video_list)

