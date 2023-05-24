import streamlit as st
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import re
import requests
from bs4 import BeautifulSoup

from config import YOUTUBE_API_KEY


def get_video_urls_from_channel(channel_input, api_key):
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
            return None, 'Could not extract channel ID'

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
            print(f'An HTTP error {e.resp.status} occurred:\n{e.content}')
            break  # Stop retrieving videos if an error occurs

    return video_urls, None  # No error

channel_input = st.text_input('Enter Youtube channel URL or ID')
if channel_input:
    video_list, error = get_video_urls_from_channel(channel_input, API_KEY)
    if error:
        st.error(error)
    else:
        st.table(video_list)

