from dotenv import load_dotenv
import requests, os
from typing import List

def api_request():
    

def get_data():
    https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&key={api_key}


if __name__ == "__main__":

    # Load api key
    load_dotenv()
    api_key = os.getenv("YOUTUBE_API_KEY")


    youtube_comment_data = get_data(videos_id:List, api_key)